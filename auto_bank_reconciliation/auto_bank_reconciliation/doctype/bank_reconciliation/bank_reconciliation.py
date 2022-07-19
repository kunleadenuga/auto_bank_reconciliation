# Copyright (c) 2022, Dexciss Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class BankReconciliation(Document):

	def on_submit(self):
		print(" we are submitting  00000000000000000000")
		for b in self.bank_reconciliation_entries :	
			if b.get("rec") == 1:
				frappe.db.set_value('Payment Entry', b.get("payment_entry"), 'rec', 1, update_modified=False)

		for s in self.bank_statement_import_view:
			print(" inside rec 22222222222222222")
			if s.get("rec") == 1:
				print(" inside rec 22222222222222222")
				frappe.db.set_value('Bank Statement', s.get("name1"), 'rec', 1, update_modified=False)
		
	
	@frappe.whitelist()
	def get_all_transcations(self):
		print(" get_all_transcations called")

		trans = []
		if self.include_reconciled_trans == 1:
			trans = frappe.get_all("Payment Entry", {"posting_date": ["Between", [self.period_from, self.period_to]], "docstatus": 1 }, ["*"])
		else:

			trans = frappe.get_all("Payment Entry", {"posting_date": ["Between", [self.period_from, self.period_to]], r"rec":0, "docstatus": 1 }, ["*"])
		# print(" this are transcations", trans)
		if trans:
			for t in trans:
				print(" this is t", t)
				self.append(
					"bank_reconciliation_entries",{
						"posting_date": t.get("posting_date"),
						"party_type": t.get("party_type"),
						"party" : t.get("party"),
						"party_name": t.get("party_name"),
						"payment_entry": t.get("name"),
						"receipt": t.get("paid_amount") if t.get("payment_type") == "Receive" else 0,
						"payment": t.get("paid_amount") if t.get("payment_type") == "Pay" else 0 ,
						"rec": t.get('rec'),
						"ref_no": t.get("reference_no"),
						"reference_date": t.get("reference_date")
					}
				)




	@frappe.whitelist()
	def get_reconsiling_entries(self):
		print(" 'get_reconsiling_entries', called")	

		trans = []
		if self.include_reconciled_trans == 1: 
			trans = frappe.get_all("Bank Statement", {"posting_date": ["Between", [self.period_from, self.period_to]]}, ["*"])
		else:
			trans = frappe.get_all("Bank Statement", {"posting_date": ["Between", [self.period_from, self.period_to]], r"rec":0 }, ["*"])
		if trans:
			for t in trans:
				self.append("bank_statement_import_view",{
					"posting_date": t.get("posting_date"),
					"name1" : t.get("name"),
					"transaction_description": t.get("transaction_description"),
					"reference": t.get("reference"),
					"type": t.get("type"),
					"withdrawal": t.get("withdrawal"),
					"deposit" : t.get("deposit"),
					"rec" : t.get("rec")
				})

	@frappe.whitelist()
	def get_unpresented_cheque(self):
		print(" this is get_unpresented_cheque")	
		for s in self.bank_reconciliation_entries :
			print(" this is common 2222222222222222222222" )
			mode = frappe.get_doc("Payment Entry", s.get("payment_entry"))

			
			
			if mode.get("mode_of_payment") == "Cheque" and mode.get("payment_type") == "Pay" and s.get('rec') == 0:
				print(" this is referec nooooooooooooooooooo", mode.get("reference_no"))
				self.append("list_of_unpresented_cheques",{
					"posting_date": mode.get("posting_date"),
					"name1": mode.get("name"),
					"transaction_description": mode.get("reference_no"),
					"type": mode.get("payment_type") ,
					"amount" : mode.get("paid_amount")
				})
				
			if mode.get("mode_of_payment") == "Cheque" and mode.get("payment_type") == "Receive" and s.get('rec') == 0:
				print(" this is referec nooooooooooooooooooo", mode.get("reference_no"))
				self.append("list_of_uncredited_cheques",{
					"posting_date": mode.get("posting_date"),
					"name1": mode.get("name"),
					"transaction_description": mode.get("reference_no"),
					"type": mode.get("payment_type") ,
					"amount" : mode.get("paid_amount")
				})	

	@frappe.whitelist()
	def match_table_one_two(self):
		print(" this is match table one two ")
		for b in self.bank_reconciliation_entries :	
			for s in self.bank_statement_import_view:
				if b.get("ref_no") == s.get("reference"):
					b.rec = s.rec = 1