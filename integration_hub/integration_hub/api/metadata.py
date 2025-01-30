import frappe
from frappe import _
from integration_hub.integration_hub.services.metadata import MetadataService


@frappe.whitelist()
def fetch_entity_types():
    """
    Fetch a list of entity types from OData metadata.
    """
    try:
        entity_types = MetadataService.fetch_entity_types()
        return entity_types
    except Exception as e:
        frappe.logger().error(f"Error fetching entity types: {str(e)}")
        frappe.throw(_("Failed to fetch entity types."))


@frappe.whitelist()
def fetch_entity_sets():
    """
    Fetch a list of entity sets from OData metadata.
    """
    try:
        entity_sets = MetadataService.fetch_entity_sets()
        return entity_sets
    except Exception as e:
        frappe.logger().error(f"Error fetching entity sets: {str(e)}")
        frappe.throw(_("Failed to fetch entity sets."))


@frappe.whitelist()
def fetch_properties(entity_type: str):
    """
    Fetch properties of a given entity type from OData metadata.
    """
    try:
        properties = MetadataService.fetch_properties(entity_type)
        return properties
    except Exception as e:
        frappe.logger().error(f"Error fetching properties for {entity_type}: {str(e)}")
        frappe.throw(_("Failed to fetch properties for entity type: {0}").format(entity_type))
