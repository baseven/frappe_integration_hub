document.addEventListener("DOMContentLoaded", function () {
    const messageArea1 = document.getElementById("message_area1");
	const messageArea2 = document.getElementById("message_area2");

    const resultDiv = document.getElementById("result");

    function showError1(message) {
        messageArea1.innerHTML = `<p style="color:red;">${message}</p>`;
    }

    function showSuccess1(message) {
        messageArea1.innerHTML = `<p style="color:green;">${message}</p>`;
    }

	function showError2(message) {
        messageArea2.innerHTML = `<p style="color:red;">${message}</p>`;
    }

    function showSuccess2(message) {
        messageArea2.innerHTML = `<p style="color:green;">${message}</p>`;
    }

    // Загрузка списка физических лиц
    document.getElementById("fetch_individuals").onclick = function () {
        messageArea2.innerHTML = ""; // Очистим сообщения
        frappe.call({
            method: "integration_hub.integration_hub.api.individuals.fetch_individuals",
            callback: function (r) {
                resultDiv.innerHTML = ""; // Очистка предыдущих результатов

                if (r.message && r.message.length > 0) {
                    const ol = document.createElement("ol");
                    ol.style.margin = "0";
                    ol.style.padding = "0 0 0 20px"; // Небольшой отступ для списка

                    r.message.forEach((individual) => {
                        const li = document.createElement("li");
                        li.textContent = `UID: ${individual.uid}, Описание: ${individual.description}`;
                        li.style.marginBottom = "5px";
                        ol.appendChild(li);
                    });

                    resultDiv.appendChild(ol);
                } else {
                    resultDiv.textContent = "Физические лица не найдены.";
                }
            },
            error: function (r) {
                // При ошибке получения списка
                showError2("Произошла ошибка при загрузке списка физических лиц.");
            },
        });
    };

    // Добавление физического лица
    document.getElementById("add_individual").onclick = function () {
        messageArea1.innerHTML = ""; // Очистим сообщения
        const uid = document.getElementById("individual_uid").value.trim();
        const full_name = document.getElementById("full_name").value.trim();

        frappe.call({
            method: "integration_hub.integration_hub.api.individuals.add_individual",
            args: { uid, full_name },
            callback: function (r) {
                if (typeof r.message === "string") {
                    // Проверим, это успех или ошибка
                    if (r.message === "Физическое лицо уже добавлено во Frappe.") {
                        showError1(r.message);
                    } else if (r.message === "Физическое лицо успешно добавлено.") {
                        showSuccess1("Физическое лицо успешно добавлено.");
                    } else {
                        // На случай, если вернётся что-то иное
                        showSuccess1(r.message);
                    }
                }
            },
            error: function (r) {
                // При ошибке (исключение на сервере)
                let error_msg = "Произошла ошибка при добавлении физического лица.";
                if (r && r._server_messages) {
                    try {
                        const server_messages = JSON.parse(r._server_messages);
                        if (server_messages.length > 0) {
                            // Выводим последнее сообщение об ошибке
                            error_msg = server_messages[server_messages.length - 1];
                        }
                    } catch (e) {
                        // Игнорируем ошибки парсинга и используем дефолтное сообщение
                    }
                }
                showError1(error_msg);
            },
        });
    };
});
