import frappe
from frappe import _


def get_integration_config(config_name: str):
	"""
	Fetch integration configuration from the Integration Configuration DocType.

	:param config_name: Name of the integration configuration.
	:return: Frappe document representing the configuration.
	"""
	if not config_name:
		frappe.throw(_("Integration configuration name is required."))

	config = frappe.get_doc("Integration Configuration", config_name)

	if not config:
		frappe.throw(_("Integration Configuration '{}' not found.").format(config_name))

	return config
