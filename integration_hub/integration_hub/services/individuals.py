import frappe
from frappe import _

from OData1C.connection import Connection
from OData1C.odata.manager import OData
from requests.auth import HTTPBasicAuth

from integration_hub.integration_hub.models.individuals import IndividualsModel
from integration_hub.integration_hub.services.integration_config import get_integration_config

config = get_integration_config()

HOST = config.get("1c_host")
PROTOCOL = config.get("1c_protocol")
USERNAME = config.get("1c_login")
PASSWORD = config.get_password("1c_password")
DATABASE = config.get("1c_database_name")

print(f"HOST: {HOST}")
print(f"PROTOCOL: {PROTOCOL}")
print(f"USERNAME: {USERNAME}")
print(f"PASSWORD: {'***' if PASSWORD else 'None'}")
print(f"DATABASE: {DATABASE}")

class IndividualsService(OData):
	"""Service for interacting with Individuals data from 1C OData."""
	database = config.get("1c_database_name")
	entity_model = IndividualsModel
	entity_name = "Catalog_ФизическиеЛица"

	@classmethod
	def manager(cls):
		"""Get OData manager."""
		with Connection(
			host=HOST,
			protocol=PROTOCOL,
			authentication=HTTPBasicAuth(USERNAME, PASSWORD),
		) as conn:
			return super().manager(conn)
