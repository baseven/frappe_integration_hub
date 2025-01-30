document.addEventListener("DOMContentLoaded", function () {
    const messageArea = document.getElementById("message_area");
    const resultDiv = document.getElementById("result");

    function showError(message) {
        messageArea.innerHTML = `<p style="color:red;">${message}</p>`;
    }

    function showSuccess(message) {
        messageArea.innerHTML = `<p style="color:green;">${message}</p>`;
    }

    function displayList(title, items) {
        resultDiv.innerHTML = `<h3>${title}</h3>`;
        if (items.length === 0) {
            resultDiv.innerHTML += "<p>Нет данных</p>";
            return;
        }
        const ul = document.createElement("ul");
        items.forEach(item => {
            const li = document.createElement("li");
            li.textContent = item;
            ul.appendChild(li);
        });
        resultDiv.appendChild(ul);
    }

    document.getElementById("fetch_entity_types").onclick = function () {
        messageArea.innerHTML = "";
        resultDiv.innerHTML = "Загрузка...";

        frappe.call({
            method: "integration_hub.integration_hub.api.metadata.fetch_entity_types",
            callback: function (r) {
                if (r.message) {
                    displayList("Entity Types", r.message);
                } else {
                    showError("Не удалось получить список EntityType.");
                }
            },
            error: function () {
                showError("Ошибка при загрузке списка EntityType.");
            },
        });
    };

    document.getElementById("fetch_entity_sets").onclick = function () {
        messageArea.innerHTML = "";
        resultDiv.innerHTML = "Загрузка...";

        frappe.call({
            method: "integration_hub.integration_hub.api.metadata.fetch_entity_sets",
            callback: function (r) {
                if (r.message) {
                    displayList("Entity Sets", r.message);
                } else {
                    showError("Не удалось получить список EntitySet.");
                }
            },
            error: function () {
                showError("Ошибка при загрузке списка EntitySet.");
            },
        });
    };

    document.getElementById("fetch_properties").onclick = function () {
        const entityType = document.getElementById("entity_type").value.trim();
        if (!entityType) {
            showError("Введите название EntityType.");
            return;
        }

        messageArea.innerHTML = "";
        resultDiv.innerHTML = "Загрузка...";

        frappe.call({
            method: "integration_hub.integration_hub.api.metadata.fetch_properties",
            args: { entity_type: entityType },
            callback: function (r) {
                if (r.message) {
                    displayList(`Свойства EntityType: ${entityType}`, r.message.map(prop => `${prop.name}: ${prop.type}`));
                } else {
                    showError(`Не удалось получить свойства для ${entityType}.`);
                }
            },
            error: function () {
                showError(`Ошибка при загрузке свойств для ${entityType}.`);
            },
        });
    };
});
