import frappe
from frappe import _

def get_integration_config():
	"""
	Fetch integration configuration from the Integration Configuration DocType.
	Assumes there is a single configuration record in the system.
	"""
	config = frappe.get_doc("Integration Configuration", "1c_test_ic")
	if not config:
		frappe.throw(_("No Integration Configuration found."))

	print("Integration config:", config)
	return config
