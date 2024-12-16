import frappe
from frappe import _
from integration_hub.integration_hub.services.individuals import IndividualsService


@frappe.whitelist()
def fetch_individuals():
	"""
	Fetch a list of individuals from 1C and return the first 10.
	"""
	manager = IndividualsService.manager()
	individuals = manager.all(ignore_invalid=True)

	# Return only the first 10 individuals with uid and description
	result = [{"uid": individual.uid, "description": individual.description} for individual in individuals[:10]]
	return result



@frappe.whitelist()
def add_individual(uid=None, full_name=None):
	"""
	Add an individual to Frappe if not already present by uid or full_name.
	"""
	manager = IndividualsService.manager()

	if uid:
		individual = manager.get(uid)
	elif full_name:
		individuals = manager.filter(description=full_name).all(ignore_invalid=True)
		individual = individuals[0] if individuals else None
	else:
		individual = None
		frappe.throw(_("Either UID or Full Name must be provided."))

	if not individual:
		frappe.throw(_("Individual not found in 1C."))

	# Check if the individual already exists in the Frappe system
	if frappe.db.exists("individuals_1c", {"uid": individual.uid}):
		return _("Individual already exists in Frappe.")

	# Create a new individuals_1c document
	individual_doc = frappe.new_doc("individuals_1c")
	individual_doc.uid = individual.uid
	individual_doc.code = individual.code
	individual_doc.description = individual.description
	individual_doc.first_name = individual.first_name
	individual_doc.last_name = individual.last_name
	individual_doc.middle_name = individual.middle_name
	individual_doc.inn = individual.inn
	individual_doc.snils = individual.snils
	individual_doc.insert()

	frappe.db.commit()
	return _("Individual added successfully.")
