import json
import frappe
from frappe import _
from integration_hub.integration_hub.services.integration_flow import IntegrationFlowService


def transform_fields_structure(data, parent_name=None):
	"""
	Преобразует вложенные данные в плоскую структуру, добавляя родительское имя для вложенных полей.

	:param data: Входные данные с полями.
	:param parent_name: Имя родительского поля, которое используется для вложенных данных.
	:return: Список плоских данных с полями name, type, parent_name.

	Example of nested data coming from a client:
	{
	  "config_name": "1c_test_ic",
	  "entity_type": "Catalog_ФизическиеЛица",
	  "flow_name": "test_flow55",
	  "fields": [
		{
		  "name": "Ref_Key",
		  "type": "Edm.Guid"
		},
		{
		  "name": "Description",
		  "type": "Edm.String"
		},
		{
		  "name": "КонтактнаяИнформация",
		  "type": "Collection",
		  "fields": [
			{
			  "name": "Ref_Key",
			  "type": "Edm.Guid"
			},
			{
			  "name": "Тип",
			  "type": "Edm.String"
			},
			{
			  "name": "Адреса",
			  "type": "Collection",
			  "fields": [
				{
				  "name": "Город",
				  "type": "Edm.String"
				},
				{
				  "name": "Улица",
				  "type": "Edm.String"
				}
			  ]
			}
		  ]
		}
	  ]
	}

	Example of transformed data:
	{
	  "config_name": "1c_test_ic",
	  "entity_type": "Catalog_ФизическиеЛица",
	  "flow_name": "test_flow55",
	  "fields": [
		{
		  "name": "Ref_Key",
		  "type": "Edm.Guid",
		  "parent_name": null
		},
		{
		  "name": "Description",
		  "type": "Edm.String",
		  "parent_name": null
		},
		{
		  "name": "КонтактнаяИнформация",
		  "type": "Collection",
		  "parent_name": null
		},
		{
		  "name": "Ref_Key",
		  "type": "Edm.Guid",
		  "parent_name": "КонтактнаяИнформация"
		},
		{
		  "name": "Тип",
		  "type": "Edm.String",
		  "parent_name": "КонтактнаяИнформация"
		},
		{
		  "name": "Адреса",
		  "type": "Collection",
		  "parent_name": "КонтактнаяИнформация"
		},
		{
		  "name": "Город",
		  "type": "Edm.String",
		  "parent_name": "Адреса"
		},
		{
		  "name": "Улица",
		  "type": "Edm.String",
		  "parent_name": "Адреса"
		}
	  ]
	}
	"""
	flattened_data = []

	for field in data["fields"]:
		# Преобразуем текущее поле
		flattened_data.append({
			"name": field["name"],
			"type": field["type"],
			"parent_name": parent_name
		})

		# Если поле является коллекцией (содержит вложенные поля)
		if field.get("type") == "Collection" and "fields" in field:
			# Рекурсивно обрабатываем вложенные поля в коллекции
			flattened_data.extend(
				transform_fields_structure({"fields": field["fields"]}, parent_name=field["name"]))

	return flattened_data


@frappe.whitelist()
def create_integration_flow(flow_data):
	"""
	Creates a new integration flow in Frappe using flow_data.

	:param flow_data: JSON with integration flow data (flow_name, config_name, entity_type, fields).
	"""
	try:
		data = json.loads(flow_data)

		flow_name = data.get("flow_name")
		config_name = data.get("config_name")
		entity_type = data.get("entity_type")
		selected_fields = data.get("fields", [])

		if not flow_name or not config_name or not entity_type or not selected_fields:
			frappe.throw(_("Все поля обязательны: flow_name, config_name, entity_type, fields"))

		flattened_fields = transform_fields_structure(data)

		# Create a new document for the integration flow
		flow = frappe.get_doc({
			"doctype": "Integration Flow",
			"flow_name": f"{config_name}/{flow_name}",
			"config_name": config_name,
			"entity_type": entity_type,
			"status": "Draft",
			"fields_json_data": json.dumps({"fields": selected_fields}, ensure_ascii=False, indent=2)  # Add JSON formatted data
		})

		# Add the transformed fields to the "Integration Flow Field"
		for field in flattened_fields:
			flow.append("fields", {
				"field_name": field.get("name"),
				"field_type": field.get("type"),
				"parent_name": field.get("parent_name")
			})

		flow.insert()
		frappe.db.commit()

		return {"success": True, "message": f"Интеграционный поток '{flow_name}' успешно создан."}

	except Exception as e:
		frappe.logger().error(f"Ошибка создания интеграционного потока: {str(e)}")
		frappe.throw(_("Ошибка создания интеграционного потока. Проверьте данные и попробуйте снова."))


@frappe.whitelist()
def run_integration_flow(flow_name):
	"""
	Запускает интеграционный поток и загружает 3 записи из 1С.

	:param flow_name: Название интеграционного потока.
	"""
	try:
		flow = frappe.get_doc("Integration Flow", flow_name)
		service = IntegrationFlowService(flow)
		records = service.fetch_records()
		return records

	except Exception as e:
		frappe.logger().error(f"Ошибка запуска интеграционного потока {flow_name}: {str(e)}")
		frappe.throw(_("Ошибка при запуске интеграционного потока."))


@frappe.whitelist()
def run_output_integration_flow(flow_name, doctype_name, records):
	"""
	Запускает исходящий интеграционный поток, загружает данные из Frappe в 1С.

	:param doctype_name: Название Doctype Frappe
	:param flow_name: Название интеграционного потока.
	:param records: Список записей из Frappe (уже с нужными именами полей).
	"""
	flow = frappe.get_doc("Integration Flow", flow_name)
	service = IntegrationFlowService(flow)

	for record in records:
		frappe_docname = record.get("name")
		guid = record.get("Ref_Key")

		odata_payload = {
			k: v for k, v in record.items()
			if k not in ("name", "Ref_Key")
		}

		if guid:
			try:
				service.update_record(guid, odata_payload)
			except Exception as e:
				frappe.logger().error(
					f"Ошибка при обновлении записи в 1С (guid: {guid}): {str(e)}")
		else:
			try:
				created_record = service.create_record(odata_payload)
				new_ref_key = created_record.model_dump().get("Ref_Key")
				if new_ref_key and frappe_docname:
					update_frappe_ref_key(doctype_name, frappe_docname, new_ref_key)
			except Exception as e:
				frappe.logger().error(f"Ошибка создания записи в 1С: {str(e)}")



def update_frappe_ref_key(doctype_name, record, ref_key):
	"""
	Обновляет ref_key в записи Frappe после успешного создания в 1С.

	:param doctype_name: Название DocType в Frappe.
	:param record: Запись во Frappe.
	:param ref_key: Значение ref_key, полученное из 1С.
	"""
	if ref_key:
		try:
			doc = frappe.get_doc(doctype_name, record)
			doc.ref_key = ref_key
			doc.save(ignore_permissions=True)
			frappe.db.commit()
		except Exception as e:
			frappe.logger().error(f"Ошибка при обновлении ref_key в Frappe (record={record}): {str(e)}")
