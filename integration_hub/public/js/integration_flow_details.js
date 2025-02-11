document.addEventListener("DOMContentLoaded", function () {
    const params = new URLSearchParams(window.location.search);
    const flowName = params.get("flow_name");
    const configName = params.get("config_name");
    const entityType = params.get("entity_type");

    if (!flowName || !configName || !entityType) {
        alert("Ошибка: отсутствуют параметры потока.");
        window.location.href = "/metadata";
        return;
    }

    document.getElementById("flow_name").textContent = flowName;
    document.getElementById("config_name").textContent = configName;
    document.getElementById("entity_type").textContent = entityType;

    const fullFlowName = `${configName}/${flowName}`;

	document.getElementById("run_flow").onclick = function () {
		frappe.call({
			method: "integration_hub.integration_hub.api.integration_flow.run_integration_flow",
			args: { flow_name: fullFlowName },
			callback: function (r) {
				if (r.message) {
					// 1) Показать результат
					document.getElementById("integration_result").innerHTML = `<pre>${JSON.stringify(r.message, null, 2)}</pre>`;

					// 2) Сделать второй вызов к Server Script.
					//Код скрипта хранится integration_hub/integration_hub/custom_scripts/process_records.py
					frappe.call({
						// Если API Method в Server Script = "process_records",
						// то method: "process_records"
						method: "process_records",
						args: {
							flow_name: fullFlowName,
							records: r.message  // предположим, что r.message содержит массив/объект
						},
						callback: function (res) {
							console.log("Server Script process_records result:", res);
							// Здесь можно отобразить вторичный результат.
						},
						error: function (err2) {
							console.error("Ошибка при вызове process_records", err2);
						}
					});

				} else {
					alert("Ошибка при запуске потока. Нет message в ответе.");
				}
			},
			error: function (err) {
				alert("Ошибка: не удалось запустить поток.");
				console.error(err);
			},
		});
	};
});
