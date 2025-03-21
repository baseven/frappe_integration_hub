# Задаем значения:
FLOW_NAME = "1c_test_ic/output_flow_1"
DOCTYPE_NAME = "output_flow_record_1"

# Сопоставление полей: {поля во Frappe: поля в 1С}
FIELD_MAPPING = {
    "ref_key": "Ref_Key",
    "full_name": "ФИО",
    "description": "Description"
}


def fetch_integration_records(doctype_name):
	"""Запрашивает записи из Frappe и переименовывает поля согласно маппингу."""
	records = frappe.get_all(doctype_name, fields=["name"] + list(FIELD_MAPPING.keys()))
	# records = frappe.get_all(doctype_name, fields=["*"])  # Загружаем все записи
	mapped = []

	for record in records:
		transformed = {onec_field: record.get(frappe_field) for frappe_field, onec_field in FIELD_MAPPING.items()}
		transformed["name"] = record.get("name")  # для обновления ref_key в Frappe при создании
		mapped.append(transformed)

	return mapped


def process_integration_records(flow_name, doctype_name, records):
	"""Передает записи в интеграционный поток на сервере."""
	return frappe.call(
		"integration_hub.integration_hub.api.integration_flow.run_output_integration_flow",
		flow_name=flow_name,
		doctype_name=doctype_name,
		records=records
	)


def process_integration_flow():
	"""Обрабатывает записи из интеграционного потока."""
	records = fetch_integration_records(DOCTYPE_NAME)
	if not records:
		return

	process_integration_records(FLOW_NAME, DOCTYPE_NAME, records)


# Запуск обработки
process_integration_flow()
