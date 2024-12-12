import os

from dotenv import load_dotenv
from OData1C.connection import Connection
from OData1C.odata.manager import OData
from requests.auth import HTTPBasicAuth

from integration_hub.integration_hub.models.individuals import IndividualsModel

load_dotenv()

HOST = os.getenv("ODATA_HOST")
PROTOCOL = os.getenv("ODATA_PROTOCOL")
USERNAME = os.getenv("ODATA_USERNAME")
PASSWORD = os.getenv("ODATA_PASSWORD")


class IndividualsService(OData):
    """Service for interacting with Individuals data from 1C OData."""

    database = "zup-demo"
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
