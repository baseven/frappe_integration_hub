document.addEventListener("DOMContentLoaded", function () {
    const configSelect = document.getElementById("configurations_list");
    const proceedButton = document.getElementById("proceed_button");

    function loadConfigurations() {
        fetch('/api/method/integration_hub.integration_hub.api.configurations.fetch_configurations')
            .then(response => response.json())
            .then(data => {
                if (data.message && data.message.length > 0) {
                    configSelect.innerHTML = ""; // Очистка списка
                    data.message.forEach(config => {
                        let option = document.createElement("option");
                        option.value = config.name;  // Используем 1c_name как name
                        option.textContent = config.name;
                        configSelect.appendChild(option);
                    });

                    proceedButton.disabled = false;
                } else {
                    configSelect.innerHTML = "<option disabled>No configurations available</option>";
                }
            })
            .catch(error => console.error("Error loading configurations:", error));
    }

    configSelect.addEventListener("change", function () {
        proceedButton.disabled = !configSelect.value;
    });

    proceedButton.addEventListener("click", function () {
        const selectedConfig = configSelect.value;
        if (selectedConfig) {
            window.location.href = `/metadata?config_name=${encodeURIComponent(selectedConfig)}`;
        }
    });

    loadConfigurations();
});
