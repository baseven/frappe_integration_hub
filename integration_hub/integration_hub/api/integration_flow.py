import frappe
from frappe import _
import json

@frappe.whitelist()
def create_integration_flow(flow_data):
    """
    Создает новую запись в "Integration Flow" на основе полученных данных.

    :param flow_data: JSON с информацией о потоке (flow_name, config_name, entity_type, fields).
    """
    try:
        # Разбираем JSON-данные
        data = json.loads(flow_data)

        flow_name = data.get("flow_name")
        config_name = data.get("config_name")
        entity_type = data.get("entity_type")
        selected_fields = data.get("fields", [])

        if not flow_name or not config_name or not entity_type or not selected_fields:
            frappe.throw(_("Все поля обязательны: flow_name, config_name, entity_type, fields"))

        # Создаем новый Integration Flow
        flow = frappe.get_doc({
            "doctype": "Integration Flow",
            "flow_name": f"{config_name}/{flow_name}",
            "config_name": config_name,
            "entity_type": entity_type,
            "status": "Draft"
        })

        # Добавляем выбранные поля в таблицу Integration Flow Field
        for field in selected_fields:
            flow.append("fields", {
                "fieldname": field.get("name"),
                "fieldtype": field.get("type")
            })

        # Сохраняем поток в базе
        flow.insert()
        frappe.db.commit()

        return {"success": True, "message": f"Интеграционный поток '{flow_name}' успешно создан.", "flow_name": flow.name}

    except Exception as e:
        frappe.logger().error(f"Ошибка создания интеграционного потока: {str(e)}")
        frappe.throw(_("Ошибка создания интеграционного потока. Проверьте данные и попробуйте снова."))
