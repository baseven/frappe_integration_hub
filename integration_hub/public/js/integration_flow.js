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

					const expandedCollections = new Map();
					const processedCollections = new Set();

					// 1. Собираем "expanded" коллекции и их свойства
					r.message.forEach(prop => {
						if (prop.type === "Collection" && prop.depth === 1 && prop.properties) {
							const cleanName = prop.name.replace(" (expanded)", "");
							expandedCollections.set(cleanName, prop.properties);
						}
					});

					r.message.forEach(prop => {
						let fieldName = prop.name.replace(" (expanded)", "");

						if (expandedCollections.has(fieldName)) {
							if (!processedCollections.has(fieldName)) {
								// 2. Если есть "expanded" версия, добавляем её и помечаем как обработанную
								const div = document.createElement("div");
								div.innerHTML = `<strong>${fieldName} (Коллекция)</strong>`;
								const subList = document.createElement("ul");

								expandedCollections.get(fieldName).forEach(subProp => {
									const label = document.createElement("label");
									const checkbox = document.createElement("input");
									checkbox.type = "checkbox";
									checkbox.value = JSON.stringify({ name: subProp.name, type: subProp.type, parent: fieldName });
									label.appendChild(checkbox);
									label.appendChild(document.createTextNode(` ${subProp.name} (${subProp.type})`));
									subList.appendChild(label);
									subList.appendChild(document.createElement("br"));
								});

								div.appendChild(subList);
								fieldsListDiv.appendChild(div);
								processedCollections.add(fieldName);
							}
						} else if (prop.type.startsWith("Collection")) {
							if (!expandedCollections.has(fieldName) && !processedCollections.has(fieldName)) {
								// 3. Если "expanded" версии нет, но это коллекция, отображаем её
								const div = document.createElement("div");
								div.innerHTML = `<strong>${fieldName} (Коллекция)</strong>`;
								fieldsListDiv.appendChild(div);
								processedCollections.add(fieldName);
							}
						} else {
							// 4. Обычные поля
							const label = document.createElement("label");
							const checkbox = document.createElement("input");
							checkbox.type = "checkbox";
							checkbox.value = JSON.stringify({ name: fieldName, type: prop.type });
							label.appendChild(checkbox);
							label.appendChild(document.createTextNode(` ${fieldName} (${prop.type})`));
							fieldsListDiv.appendChild(label);
							fieldsListDiv.appendChild(document.createElement("br"));
						}
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

		// Функция для рекурсивной группировки полей по родительским коллекциям
		function groupFieldsByParent(fields) {
			const grouped = {};

			fields.forEach(field => {
				if (field.parent) {
					// Если поле вложенное, добавляем его в родительскую коллекцию
					if (!grouped[field.parent]) {
						grouped[field.parent] = {
							name: field.parent,
							type: "Collection",
							fields: []
						};
					}
					grouped[field.parent].fields.push({
						name: field.name,
						type: field.type
					});
				} else {
					// Если поле не вложенное, добавляем его в основной массив
					grouped[field.name] = {
						name: field.name,
						type: field.type
					};
				}
			});

			// Преобразуем в массив
			return Object.values(grouped).map(item => {
				if (item.fields) {
					item.fields = groupFieldsByParent(item.fields); // Рекурсивно обрабатываем вложенные поля
				}
				return item;
			});
		}

		// Группируем поля
		const groupedFields = groupFieldsByParent(selectedFields);

		const flowData = JSON.stringify({
			config_name: configName,
			entity_type: entityType,
			flow_name: flowName,
			fields: groupedFields
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
