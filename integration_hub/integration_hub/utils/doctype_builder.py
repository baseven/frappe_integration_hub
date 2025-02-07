import frappe
from frappe.model.meta import get_meta


class DoctypeBuilder:
    """
    Класс для динамического создания Doctype на основе Integration Flow.
    """

    @staticmethod
    def get_or_create_doctype(flow_name: str, fields: list[dict]) -> str:
        """
        Проверяет, существует ли Doctype, и если нет — создает новый.

        :param flow_name: Название интеграционного потока.
        :param fields: Список полей из Integration Flow.
        :return: Имя созданного или найденного Doctype.
        """
        doctype_name = f"Integration Flow - {flow_name}"

        if frappe.db.exists("DocType", doctype_name):
            return doctype_name  # Если Doctype уже существует, просто возвращаем его имя.

        # Определяем структуру нового Doctype
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": doctype_name,
            "module": "Integration Hub",
            "custom": 1,  # Помечаем как кастомный Doctype
            "fields": []
        })

        # Добавляем поле ref_key (уникальный ID из 1С)
        doc.append("fields", {
            "fieldname": "ref_key",
            "label": "Ref_Key",
            "fieldtype": "Data",
            "reqd": 1,  # Обязательное поле
            "unique": 1  # Должно быть уникальным
        })

        # Добавляем ссылку на Integration Flow
        doc.append("fields", {
            "fieldname": "integration_flow",
            "label": "Integration Flow",
            "fieldtype": "Link",
            "options": "Integration Flow",
            "reqd": 1
        })

        # Добавляем поля из Integration Flow
        for field in fields:
            fieldname = field["fieldname"]
            label = field["fieldname"]
            fieldtype = "Data"  # По умолчанию все строки

            if field["fieldtype"] == "Edm.Int32" or field["fieldtype"] == "Edm.Int16":
                fieldtype = "Int"
            elif field["fieldtype"] == "Edm.Decimal":
                fieldtype = "Float"
            elif field["fieldtype"] == "Edm.Date":
                fieldtype = "Date"
            elif field["fieldtype"] == "Edm.Boolean":
                fieldtype = "Check"

            doc.append("fields", {
                "fieldname": fieldname.lower(),
                "label": label,
                "fieldtype": fieldtype
            })

        # Создаем Doctype в системе
        doc.insert()
        frappe.db.commit()

        return doctype_name

# integration_hub/integration_hub/api/integration_flow.py
# import frappe
# from frappe import _
# from integration_hub.integration_hub.services.integration_flow import IntegrationFlowService
# from integration_hub.integration_hub.utils.doctype_builder import DoctypeBuilder
#
#
# @frappe.whitelist()
# def run_integration_flow(flow_name):
# 	"""
# 	Запускает интеграционный поток, загружает 3 записи из 1С и сохраняет их во Frappe.
#
# 	:param flow_name: Название интеграционного потока.
# 	"""
# 	try:
# 		# Получаем объект интеграционного потока
# 		flow = frappe.get_doc("Integration Flow", flow_name)
#
# 		# Создаем Doctype (если его нет)
# 		doctype_name = DoctypeBuilder.get_or_create_doctype(flow_name, flow.fields)
#
# 		# Создаем сервисный объект и загружаем данные
# 		service = IntegrationFlowService(flow)
# 		records = service.fetch_records()
#
# 		if not records:
# 			return {"success": False, "message": "Нет новых записей для загрузки."}
#
# 		saved_records = []
#
# 		for record in records:
# 			ref_key = record.get("Ref_Key")
# 			description = record.get("Description")
#
# 			# Проверяем, существует ли запись в Frappe
# 			if frappe.db.exists(doctype_name, {"ref_key": ref_key}):
# 				continue  # Пропускаем дубликаты
#
# 			# Создаем новую запись
# 			record_doc = frappe.get_doc({
# 				"doctype": doctype_name,
# 				"ref_key": ref_key,
# 				"integration_flow": flow_name,
# 				**record  # Сохраняем все остальные данные как отдельные поля
# 			})
# 			record_doc.insert()
# 			saved_records.append(ref_key)
#
# 		frappe.db.commit()
#
# 		return {"success": True, "message": f"Загружено {len(saved_records)} записей.",
# 				"saved": saved_records}
#
# 	except Exception as e:
# 		frappe.logger().error(f"Ошибка запуска интеграционного потока {flow_name}: {str(e)}")
# 		frappe.throw(_("Ошибка при запуске интеграционного потока."))
#
