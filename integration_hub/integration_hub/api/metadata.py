import frappe
from frappe import _
from integration_hub.integration_hub.services.metadata import MetadataService


@frappe.whitelist()
def fetch_entity_types(config_name: str):
	"""
	Fetch a list of entity types from OData metadata for a given integration configuration.

	:param config_name: Name of the integration configuration.
	"""
	try:
		entity_types = MetadataService.fetch_entity_types(config_name)
		return entity_types
	except Exception as e:
		frappe.logger().error(f"Error fetching entity types for {config_name}: {str(e)}")
		frappe.throw(_("Failed to fetch entity types."))


@frappe.whitelist()
def fetch_entity_sets(config_name: str):
	"""
	Fetch a list of entity sets from OData metadata for a given integration configuration.

	:param config_name: Name of the integration configuration.
	"""
	try:
		entity_sets = MetadataService.fetch_entity_sets(config_name)
		return entity_sets
	except Exception as e:
		frappe.logger().error(f"Error fetching entity sets for {config_name}: {str(e)}")
		frappe.throw(_("Failed to fetch entity sets."))


@frappe.whitelist()
def fetch_properties(config_name: str, entity_type: str):
	"""
	Fetch properties of a given entity type from OData metadata.

	:param config_name: Name of the integration configuration.
	:param entity_type: The entity type for which properties need to be fetched.
	"""
	try:
		properties = MetadataService.fetch_properties(config_name, entity_type)
		return properties
	except Exception as e:
		frappe.logger().error(f"Error fetching properties for {entity_type} in {config_name}: {str(e)}")
		frappe.throw(_("Failed to fetch properties for entity type: {0}").format(entity_type))
