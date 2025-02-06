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

    document.getElementById("run_flow").onclick = function () {
        frappe.call({
            method: "integration_hub.integration_hub.api.integration_flow.run_integration_flow",
            args: { flow_name: flowName },
            callback: function (r) {
                if (r.message) {
                    document.getElementById("integration_result").innerHTML = `<p>${r.message}</p>`;
                } else {
                    alert("Ошибка при запуске потока.");
                }
            },
            error: function (err) {
                alert("Ошибка: не удалось запустить поток.");
                console.error(err);
            },
        });
    };
});
