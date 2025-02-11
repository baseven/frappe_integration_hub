# 🔹 Имя потока Integration Flow
flow_name = "1c_test_ic/test_flow4"

# 🔹 Имя сущности Frappe
doctype_name = "test_rec_flow"

# Список обработанных записей (для логов)
processed_entries = []

# Получаем записи как Pydantic-модели
records = frappe.call("integration_hub.integration_hub.api.integration_flow.run_integration_flow", flow_name=flow_name)

for record in records:
	# Преобразуем объект модели в словарь
	record_data = record.model_dump()

	# Извлекаем нужные поля. Названия в () указываем, как они есть в 1С.
	# Список полей можно посмотреть в "Поля для интеграции" у выбранного Integration Flow (flow_name).
	ref_key = record_data.get("Ref_Key")
	description = record_data.get("Description")
	gender = record_data.get("Пол")

	# Проверяем наличие обязательного поля. Если полей несколько, то добавить проверку.
	# Это смотрим у выбранной сущности Frappe (doctype_name).
	if not ref_key:
		processed_entries.append(f"Пропущена запись {record_data}: отсутствует Ref_Key")
		continue

	# Проверяем, существует ли уже запись в Frappe
	existing_record = frappe.db.exists(doctype_name, {"ref_key": ref_key})

	# Проверяем, существует ли уже запись
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

# Фиксируем изменения в БД
frappe.db.commit()
log_message = f"Обработано {len(processed_entries)} записей для потока {flow_name}\n" + "\n".join(processed_entries)
