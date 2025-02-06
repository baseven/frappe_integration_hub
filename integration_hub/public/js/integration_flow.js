document.addEventListener("DOMContentLoaded", function () {
    const params = new URLSearchParams(window.location.search);
    const configName = params.get("config_name");
    const entityType = params.get("entity_type");

    if (!configName || !entityType) {
        alert("Ошибка: отсутствуют параметры конфигурации или типа сущности.");
        window.location.href = "/metadata";
        return;
    }

    document.getElementById("selected_config").textContent = `Конфигурация: ${configName}`;
    document.getElementById("selected_entity_type").textContent = `EntityType: ${entityType}`;

    const fieldsListDiv = document.getElementById("fields_list");
    const flowNameInput = document.getElementById("flow_name");

    function loadEntityFields() {
        frappe.call({
            method: "integration_hub.integration_hub.api.metadata.fetch_properties",
            args: { config_name: configName, entity_type: entityType },
            callback: function (r) {
                if (r.message) {
                    fieldsListDiv.innerHTML = "";
                    r.message.forEach(prop => {
                        const label = document.createElement("label");
                        const checkbox = document.createElement("input");
                        checkbox.type = "checkbox";
                        checkbox.value = JSON.stringify({ name: prop.name, type: prop.type });
                        label.appendChild(checkbox);
                        label.appendChild(document.createTextNode(` ${prop.name} (${prop.type})`));
                        fieldsListDiv.appendChild(label);
                        fieldsListDiv.appendChild(document.createElement("br"));
                    });
                } else {
                    fieldsListDiv.innerHTML = "<p>Ошибка загрузки полей.</p>";
                }
            },
            error: function () {
                fieldsListDiv.innerHTML = "<p>Ошибка при загрузке полей.</p>";
            },
        });
    }

    document.getElementById("create_flow").onclick = function () {
        const selectedFields = Array.from(fieldsListDiv.querySelectorAll("input:checked")).map(cb => JSON.parse(cb.value));
        const flowName = flowNameInput.value.trim();

        if (!flowName) {
            alert("Введите название потока.");
            return;
        }

        if (selectedFields.length === 0) {
            alert("Выберите хотя бы одно поле для интеграции.");
            return;
        }

        const flowData = JSON.stringify({
            config_name: configName,
            entity_type: entityType,
            flow_name: flowName,
            fields: selectedFields
        });

        frappe.call({
            method: "integration_hub.integration_hub.api.integration_flow.create_integration_flow",
            args: { flow_data: flowData },
            callback: function (r) {
                if (r.message) {
                    alert(`Интеграционный поток "${flowName}" успешно создан.`);
                    window.location.href = `/integration_flow_details?flow_name=${encodeURIComponent(flowName)}&config_name=${encodeURIComponent(configName)}&entity_type=${encodeURIComponent(entityType)}`;
                } else {
                    alert("Ошибка при создании потока.");
                }
            },
            error: function (err) {
                alert("Ошибка: не удалось создать поток.");
                console.error(err);
            },
        });
    };

    loadEntityFields();
});
