import frappe
from frappe import _

@frappe.whitelist()
def fetch_configurations():
	"""
	Fetch the list of available integration configurations using the 1c_name field.
	"""
	configurations = frappe.get_all("Integration Configuration", fields=["1c_name"])
	print(f'configurations: {configurations}')
	return [{"name": config["1c_name"]} for config in configurations]  # Возвращаем список с ключом name
