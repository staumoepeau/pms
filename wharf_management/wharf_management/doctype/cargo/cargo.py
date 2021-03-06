# -*- coding: utf-8 -*-
# Copyright (c) 2017, Caitlah Technology and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, json
from frappe.model.document import Document
from frappe import msgprint, _, scrub
from frappe.utils import cstr, flt, fmt_money, formatdate, cint, getdate, rounded, date_diff, money_in_words, add_days, now


class Cargo(Document):

    def on_submit(self):
        self.validate_booking_ref()
        if not self.hazardous:
            self.hazardous = self.get_hazardous()

    def validate(self):
#        self.check_bulk_cargo()
        self.clear_new_cargo()
        if not self.title:
            self.title = self.get_title()

#    def check_bulk_cargo(self):
#        if self.cargo_type == "Break Bulk":
#            self.name = self.name +"-"+ self.break_bulk_items

    def get_hazardous(self):
        if not self.hazardous_code:
            hazardous_ans = "No"
        if self.hazardous_code:
            hazardous_ans = "Yes"
        return hazardous_ans

    def clear_new_cargo(self):
        self.inspection_status == ""
        self.final_status == ""
#        frappe.db.sql("""Update `tabCargo` set final_status="NULL", inspection_status="NULL" where name=%s""", (self.cargo_ref))


    def validate_booking_ref(self):
        if not self.booking_ref:
            msgprint(_("Booking Ref # is Manadory").format(self.booking_ref),
                    raise_exception=1)

    def get_title(self):
        return self.consignee

    def get_holidays(self, start_date, end_date):
        holiday_list = frappe.db.get_value("Company", "Ports Authority Tonga", "default_holiday_list")
        holidays = frappe.db.sql_list('''select holiday_date  from `tabHoliday`
            where
                parent=%(holiday_list)s
                and holiday_date >= %(start_date)s
                and holiday_date <= %(end_date)s''', {
                    "holiday_list": holiday_list,
                    "start_date": start_date,
                    "end_date": end_date
                })
        holidays = [cstr(i) for i in holidays]
        return holidays

    def get_storage_fee(self):
        working_days, fees, charge_days, free_days = 0.0, 0.0, 0.0, 0.0
        holidays = self.get_holidays(self.gate1_in, self.etd_date)
        working_days = flt(date_diff(self.etd_date, self.gate1_in))
        working_days -= flt(len(holidays))

        if self.cargo_type in ["Tank Tainers", "Container", "Flatrack"]:
            free_days = flt(frappe.db.get_value("Wharf Fees", {"wharf_fee_category":"Storage Fee", "cargo_type" : self.cargo_type, "container_size" : self.container_size, "container_content" : self.container_content }, "grace_days"))

        if self.cargo_type not in ["Tank Tainers", "Container", "Flatrack"]:
            free_days = flt(frappe.db.get_value("Wharf Fees", {"wharf_fee_category":"Storage Fee", "cargo_type" : self.cargo_type}, "grace_days"))

        if self.secondary_work_type == "Transhipment":
            working_days, free_days = 0.0, 0.0
        if self.cargo_type in ["Tank Tainers", "Container", "Flatrack"]:
              wfee = frappe.db.get_value("Wharf Fees", {"wharf_fee_category":"Wharfage Fee", "cargo_type" : self.cargo_type, "container_size" : self.container_size}, "fee_amount")

        if self.cargo_type not in ["Tank Tainers", "Container", "Flatrack"]:
                wfee = frappe.db.get_value("Wharf Fees", {"wharf_fee_category":"Wharfage Fee", "cargo_type" : self.cargo_type}, "fee_amount")

        fees = flt(frappe.db.get_value("Wharf Fees", {"wharf_fee_category":"Storage Fee", "cargo_type" : self.cargo_type, 
        "container_size" : self.container_size, "container_content" : self.container_content}, "fee_amount"))
        
        if free_days < working_days:
                charge_days = working_days - free_days

        if free_days > working_days:
            charge_days = 0

        self.wharfage_fee = wfee
        self.storage_fee = charge_days * fees.fee_amount
        self.charge_days = charge_days
        self.free_days = free_days
        self.storage_days = working_days
        self.storage_rate = fees.fee_amount

@frappe.whitelist()
def update_breakbulk_inspection(name_ref, counter, qty):
    frappe.db.sql("""UPDATE `tabCargo` SET break_bulk_item_count=%s  WHERE name=%s""", (counter, name_ref))


@frappe.whitelist()
def update_security_breakbulk(name_ref, counter, qty):
    frappe.db.sql("""UPDATE `tabCargo` SET security_item_count=%s  WHERE name=%s""", (counter, name_ref))

@frappe.whitelist()
def set_overdue_storage(name_ref):
    frappe.db.sql("""UPDATE `tabCargo` SET storage_overdue=1 WHERE name=%s""", (name_ref))

@frappe.whitelist()
def update_custom_inspection(name_ref):
    frappe.db.sql("""UPDATE `tabCargo` SET status='Custom Inspection', custom_inspection='Closed', custom_inspection_date=%s WHERE name=%s""", (now(), name_ref))

@frappe.whitelist()
def update_deliver_custom_inspection(name_ref):
    frappe.db.sql("""UPDATE `tabCargo` SET status='Inspection Delivered', custom_inspection_deliver='Closed', custom_inspection_deliver_date=%s WHERE name=%s""", (now(), name_ref))
	
#    if counter == qty:
#        frappe.db.sql("""UPDATE `tabCargo` SET break_bulk_item_count=%s  WHERE name=%s""", (counter, name_ref))
#        create_preadvise_history(name_ref)
#        frappe.db.delete('Pre Advice', {'name': name_ref })
