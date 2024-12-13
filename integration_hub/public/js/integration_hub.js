document.addEventListener("DOMContentLoaded", function () {
    // Fetch Individuals
    document.getElementById("fetch_individuals").onclick = function () {
        fetch('/api/method/integration_hub.integration_hub.api.individuals.fetch_individuals', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            const resultDiv = document.getElementById("result");
            resultDiv.innerHTML = ""; // Clear previous results

            if (data.message && data.message.length > 0) {
                const list = document.createElement("ul");
                data.message.forEach((individual) => {
                    const item = document.createElement("li");
                    item.textContent = `UID: ${individual.uid}, Description: ${individual.description}`;
                    list.appendChild(item);
                });
                resultDiv.appendChild(list);
            } else {
                resultDiv.textContent = "No individuals found.";
            }
        })
        .catch(error => console.error('Error fetching individuals:', error));
    };

    // Add Individual
    document.getElementById("add_individual").onclick = function () {
        const uid = document.getElementById("individual_uid").value.trim();
        const full_name = document.getElementById("full_name").value.trim();

        fetch('/api/method/integration_hub.integration_hub.api.individuals.add_individual', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ uid, full_name }),
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message || "Success");
        })
        .catch(error => console.error('Error adding individual:', error));
    };
});
