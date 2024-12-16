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

        // Prepare form data using URLSearchParams
        const formData = new URLSearchParams();
        if (uid) formData.append("uid", uid);
        if (full_name) formData.append("full_name", full_name);

        fetch('/api/method/integration_hub.integration_hub.api.individuals.add_individual', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert(data.message);
            } else {
                alert("Success");
            }
        })
        .catch(error => {
            console.error('Error adding individual:', error);
            alert('Error occurred while adding individual.');
        });
    };
});
