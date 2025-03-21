# Задаем значения:
# Имя потока Integration Flow
FLOW_NAME = "1c_test_ic/test_flow55"
# Имя сущности Frappe, в которую выполняется запись
DOCTYPE_NAME = "test_rec_flow55"


def fetch_integration_records(flow_name):
	"""Запрашивает данные из интеграционного потока Frappe."""
	return frappe.call("integration_hub.integration_hub.api.integration_flow.run_integration_flow",
					   flow_name=flow_name)


def extract_email_contact(contacts):
	"""
	Извлекает первый email-контакт из списка контактов.
	Возвращает словарь с данными контакта или None, если email-контактов нет.
	"""
	for contact in contacts:
		if contact.get("Тип") == "АдресЭлектроннойПочты":
			return {
				"contact_ref_key": contact.get("Ref_Key"),
				"contact_type": contact.get("Тип"),
				"contact_representation": contact.get("Представление"),
			}
	return None


def process_record(record):
	"""
	Обрабатывает одну запись, создавая или обновляя запись в Frappe.
	Возвращает строку с логом обработки.
	"""
	record_data = record.model_dump()
	ref_key = record_data.get("Ref_Key")
	full_name = record_data.get("ФИО")
	contacts = record_data.get("КонтактнаяИнформация", [])

	# Проверяем наличие обязательного поля. Если полей несколько, то добавить их в проверку.
	if not ref_key:
		return f"Пропущена запись {record_data}: отсутствует Ref_Key"

	# Получаем email-контакт
	email_contact = extract_email_contact(contacts)

	if not email_contact:
		return f"Пропущена запись {record_data}: отсутствует email-контакт"

	# Проверяем существование записи
	existing_record = frappe.db.exists(DOCTYPE_NAME, {"ref_key": ref_key})

	if existing_record:
		record_doc = frappe.get_doc(DOCTYPE_NAME, existing_record)
		# Заполняем поля. Поля record_doc должны соответствовать полям выбранной сущности Frappe (DOCTYPE_NAME)
		record_doc.full_name = full_name
		record_doc.contact_ref_key = email_contact["contact_ref_key"]
		record_doc.contact_type = email_contact["contact_type"]
		record_doc.contact_representation = email_contact["contact_representation"]
		# Сохраняем документ
		record_doc.save(ignore_permissions=True)
		action = "Обновлена"
	else:
		record_doc = frappe.new_doc(DOCTYPE_NAME)
		# Заполняем поля. Поля record_doc должны соответствовать полям выбранной сущности Frappe (DOCTYPE_NAME)
		record_doc.ref_key = ref_key
		record_doc.full_name = full_name
		record_doc.contact_ref_key = email_contact["contact_ref_key"]
		record_doc.contact_type = email_contact["contact_type"]
		record_doc.contact_representation = email_contact["contact_representation"]
		# Создаем новый документ
		record_doc.insert(ignore_permissions=True)
		action = "Создана"

	return f"{action} запись: {record_data}"


def process_integration_flow():
	"""Обрабатывает записи из интеграционного потока и логирует результат."""
	processed_entries = []
	records = fetch_integration_records(FLOW_NAME)

	for record in records:
		log_entry = process_record(record)
		processed_entries.append(log_entry)

	frappe.db.commit()

	log_message = f"Обработано {len(processed_entries)} записей для потока {FLOW_NAME}\n" + "\n".join(
		processed_entries)


# frappe.logger().info(log_message)

# Запуск обработки
process_integration_flow()
