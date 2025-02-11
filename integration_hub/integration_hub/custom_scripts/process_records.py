flow_name = frappe.form_dict.get("flow_name")
records_raw = frappe.form_dict.get("records") or "[]"

try:
	records = json.loads(records_raw) if isinstance(records_raw, str) else records_raw
except json.JSONDecodeError:
	frappe.throw("Ошибка при разборе records: некорректный JSON")

result = []

for record in records:
	if not isinstance(record, list) or any(not isinstance(kv, list) or len(kv) != 2 for kv in record):
		result.append('не прошел if not isinstance')
		continue  # Пропускаем некорректные данные

	# Преобразуем список пар [[ключ, значение], [ключ, значение]] в словарь
	record_data = {kv[0]: kv[1] for kv in record}

	ref_key = record_data.get("Ref_Key")
	description = record_data.get("Description")
	gender = record_data.get("Пол")  # Новый параметр "Пол"

	if not ref_key or not description:
		result.append('не прошел if not ref_key or not description')
		continue  # Пропускаем, если данных не хватает

	#Проверяем, существует ли уже запись с таким ref_key
	if not frappe.db.exists("test_rec_flow", {"ref_key": ref_key}):
		record_doc = frappe.new_doc("test_rec_flow")
		record_doc.ref_key = ref_key
		record_doc.description = description
		record_doc.gender = gender
		record_doc.insert(ignore_permissions=True)
		result.append(record_data)

frappe.db.commit()

frappe.response["message"] = {
	"success": True,
	"message": f"Создано новых записей для потока {flow_name}",
	"records": records,
	"result": result
}
