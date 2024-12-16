document.addEventListener("DOMContentLoaded", function () {
    // Fetch Individuals
    document.getElementById("fetch_individuals").onclick = function () {
        frappe.call({
            method: "integration_hub.integration_hub.api.individuals.fetch_individuals",
            callback: function (r) {
                const resultDiv = document.getElementById("result");
                resultDiv.innerHTML = ""; // Clear previous results

                if (r.message && r.message.length > 0) {
                    const list = document.createElement("ul");
                    r.message.forEach((individual) => {
                        const item = document.createElement("li");
                        item.textContent = `UID: ${individual.uid}, Description: ${individual.description}`;
                        list.appendChild(item);
                    });
                    resultDiv.appendChild(list);
                } else {
                    resultDiv.textContent = "No individuals found.";
                }
            },
        });
    };

    // Add Individual
    document.getElementById("add_individual").onclick = function () {
        const uid = document.getElementById("individual_uid").value.trim();
        const full_name = document.getElementById("full_name").value.trim();

        frappe.call({
            method: "integration_hub.integration_hub.api.individuals.add_individual",
            args: { uid, full_name },
            callback: function (r) {
                alert(r.message);
            },
        });
    };
});
