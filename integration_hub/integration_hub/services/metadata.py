from OData1C import Connection, MetadataManager
from requests.auth import HTTPBasicAuth
from integration_hub.integration_hub.services.integration_config import get_integration_config


class MetadataService:
	"""
	Service for fetching metadata (entity sets and types) from OData.
	"""

	@classmethod
	def get_manager(cls, config_name: str) -> MetadataManager:
		"""
		Initialize and return a MetadataManager instance with the given integration configuration.

		:param config_name: Name of the integration configuration.
		:return: MetadataManager instance.
		"""
		config = get_integration_config(config_name)

		protocol = config.get("1c_protocol")
		host = config.get("1c_host")
		database = config.get("1c_database_name")
		username = config.get("1c_login")
		password = config.get_password("1c_password")

		print(f"HOST: {host}")
		print(f"PROTOCOL: {protocol}")
		print(f"USERNAME: {username}")
		print(f"PASSWORD: {'***' if password else 'None'}")
		print(f"DATABASE: {database}")

		connection = Connection(
			host=host,
			protocol=protocol,
			authentication=HTTPBasicAuth(username, password),
		)

		return MetadataManager(connection=connection, database_name=database)

	@classmethod
	def fetch_entity_types(cls, config_name: str):
		"""
		Fetch a list of available entity types from OData metadata.

		:param config_name: Name of the integration configuration.
		:return: List of entity types.
		"""
		manager = cls.get_manager(config_name)
		return manager.get_entity_types()

	@classmethod
	def fetch_entity_sets(cls, config_name: str):
		"""
		Fetch a list of available entity sets from OData metadata.

		:param config_name: Name of the integration configuration.
		:return: List of entity sets.
		"""
		manager = cls.get_manager(config_name)
		return manager.get_entity_sets()

	@classmethod
	def fetch_properties(cls, config_name: str, entity_type: str):
		"""
		Fetch properties of a given entity type.

		:param config_name: Name of the integration configuration.
		:param entity_type: The entity type for which properties need to be fetched.
		:return: List of properties.
		"""
		manager = cls.get_manager(config_name)
		return manager.get_properties(entity_type)
