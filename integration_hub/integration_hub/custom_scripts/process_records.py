# 🔹 Имя сущности Frappe
doctype_name = "test_rec_flow"

# Имя потока Integration Flow
flow_name = frappe.form_dict.get("flow_name")

# Получаем записи как JSON
records_raw = frappe.form_dict.get("records") or "[]"

try:
	records = json.loads(records_raw) if isinstance(records_raw, str) else records_raw
except json.JSONDecodeError:
	frappe.throw("Ошибка при разборе records: некорректный JSON")

# Список обработанных записей (для логов)
processed_entries = []

for record in records:
	if not isinstance(record, list) or any(not isinstance(kv, list) or len(kv) != 2 for kv in record):
		processed_entries.append(f"Пропущена запись {record}: некорректные данные")
		continue

	# Преобразуем список пар [[ключ, значение], [ключ, значение]] в словарь
	record_data = {kv[0]: kv[1] for kv in record}

	# Извлекаем нужные поля. Названия в () указываем, как они есть в 1С.
	# Список полей можно посмотреть в "Поля для интеграции" у выбранного Integration Flow (flow_name).
	ref_key = record_data.get("Ref_Key")
	description = record_data.get("Description")
	gender = record_data.get("Пол")  # Новый параметр "Пол"

	# Проверяем наличие обязательного поля. Если полей несколько, то добавить проверку.
	# Это смотрим у выбранной сущности Frappe (doctype_name).
	if not ref_key:
		processed_entries.append(f"Пропущена запись {record_data}: отсутствует Ref_Key")
		continue

	# Проверяем, существует ли уже запись в Frappe
	existing_record = frappe.db.exists(doctype_name, {"ref_key": ref_key})

	if existing_record:
		# Обновление существующей записи.
		# Поля record_doc должны соответствовать полям выбранной сущности Frappe (doctype_name)
		record_doc = frappe.get_doc(doctype_name, existing_record)
		record_doc.description = description
		record_doc.gender = gender
		record_doc.save(ignore_permissions=True)
		processed_entries.append(f"Обновлена запись: {record_data}")
	else:
		# Создание новой записи
		# Поля record_doc должны соответствовать полям выбранной сущности Frappe (doctype_name)
		record_doc = frappe.new_doc(doctype_name)
		record_doc.ref_key = ref_key
		record_doc.description = description
		record_doc.gender = gender
		record_doc.insert(ignore_permissions=True)
		processed_entries.append(f"Создана новая запись: {record_data}")

frappe.db.commit()

frappe.response["message"] = {
	"success": True,
	"message": f"Обработано {len(processed_entries)} записей для потока {flow_name}",
	"processed_records": processed_entries
}
