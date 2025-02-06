from OData1C import Connection, EntityManager
from requests.auth import HTTPBasicAuth
from integration_hub.integration_hub.services.integration_config import get_integration_config
from integration_hub.integration_hub.utils.model_builder import ModelBuilder


class IntegrationFlowService:
	"""
	Сервис для работы с интеграционными потоками. Позволяет запрашивать данные из 1С.
	"""

	def __init__(self, flow):
		"""
		Инициализирует сервис на основе объекта интеграционного потока.

		:param flow: Объект интеграционного потока из Frappe.
		"""
		self.flow = flow
		self.config = get_integration_config(flow.config_name)
		self.entity_model = self.build_model()
		self.manager = self.get_manager()

	def build_model(self):
		"""
		Создает Pydantic-модель на основе полей из Integration Flow.

		:return: Динамически сгенерированная Pydantic-модель.
		"""
		fields = [{"fieldname": field.fieldname, "fieldtype": field.fieldtype} for field in
				  self.flow.fields]
		return ModelBuilder.create_model(self.flow.flow_name, fields)

	def get_manager(self) -> EntityManager:
		"""
		Создает и возвращает экземпляр EntityManager для взаимодействия с OData.

		:return: EntityManager, настроенный для работы с указанной сущностью.
		"""
		connection = Connection(
			host=self.config.get("1c_host"),
			protocol=self.config.get("1c_protocol"),
			authentication=HTTPBasicAuth(
				self.config.get("1c_login"),
				self.config.get_password("1c_password")
			),
		)

		return EntityManager(
			connection=connection,
			database_name=self.config.get("1c_database_name"),
			entity_name=self.flow.entity_type,
			entity_model=self.entity_model
		)

	def fetch_records(self):
		"""
		Получает 3 записи из 1С для указанного EntityType.

		:return: Список записей (JSON).
		"""
		return self.manager.top(3).all(ignore_invalid=True)
