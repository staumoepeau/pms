# -*- coding: utf-8 -*-
# Copyright (c) 2017, Sione Taumoepeau and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, msgprint, throw
from frappe.model.document import Document

class PreAdvice(Document):


	def on_submit(self):
		self.create_cargo_list_items()
	
	def create_cargo_list_items(self):
#		user = frappe.get_doc("Agents", self.transfer_from_agent)
		doc = frappe.new_doc("Cargo")
		doc.update({
					"company" : self.company,
					"docstatus" : 1,
					"booking_ref" : self.booking_ref,
					"pat_code" : self.pat_code,
					"net_weight" : self.net_weight,
		#			"export_status" : self.export_status,
					"cargo_type" : self.cargo_type,
		#			"pre_advise_status" : self.pre_advise_status,
					"qty" : self.qty,
					"container_no" : self.container_no,
					"voyage_no" : self.voyage_no,
					"bol" : self.bol,
					"work_type" : self.work_type,
					"secondary_work_type" : self.secondary_work_type,
					"third_work_type" : self.third_work_type,
					"pol" : self.pol,
					"agents" : self.agents,
					"commodity_code" : self.commodity_code,
					"vessel" : self.vessel,
					"pod" : self.pod,
					"temperature" : self.temperature,
					"container_type" : self.container_type,
					"mark" : self.mark,
					"final_dest_port" : self.final_dest_port,
					"volume" : self.volume,
		#			"export_arrival_date" : self.export_arrival_date,
					"container_size" : self.container_size,
					"consignee" : self.consignee,
					"container_content" : self.container_content,
					"stowage" : self.stowage,
					"hazardous" : self.hazardous,
					"hazardous_code" : self.hazardous_code,
					"status" : self.status,
					"seal_1" : self.seal_1,
					"seal_2" : self.seal_2,
					"eta_date" : self.eta_date,
					"cargo_description" : self.cargo_description,
					"etd_date" : self.etd_date,
					"chasis_no" : self.chasis_no,
					"yard_slot" : self.yard_slot
				})
		doc.insert()
		doc.submit()

	
	def validate_container_no(self):
    		container_number=None
		container_number = frappe.db.sql("""Select name from `tabExport` where container_no=%s and status="Yard" """, (self.container_no))

		if not container_number:
    			frappe.throw(_("There is no Container No : {0} in the Export List").format(self.container_no))
				
		else:
#    			container_ref = frappe.db.get_value("Export", {"container_no": self.container_no}, "name")
    			val = frappe.db.get_value("Export", {"container_no": self.container_no}, ["status","yard_slot",
				"main_gate_start","main_gate_ends","gate1_start","gate1_ends","driver_start",
				"container_type","container_size","pat_code","container_content","driver_ends","seal_1"], as_dict=True)
			self.yard_slot = val.yard_slot
			self.main_gate_start = val.main_gate_start
			self.main_gate_ends = val.main_gate_ends
			self.gate1_start = val.gate1_start
			self.gate1_ends = val.gate1_ends
			self.driver_start = val.driver_start
			self.driver_ends = val.driver_ends
			self.container_type = val.container_type
			self.container_size = val.container_size
			self.pat_code = val.pat_code
			self.container_content = val.container_content
			self.seal_1 = val.seal_1
    			
			frappe.msgprint(_("Details for the Container No {0} have been imported from the Export List").format(self.container_no))

			frappe.db.sql("""delete from `tabExport` where container_no=%s""", self.container_no)