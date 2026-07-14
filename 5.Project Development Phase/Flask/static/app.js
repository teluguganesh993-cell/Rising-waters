document.addEventListener("DOMContentLoaded", () => {
    // API base URL
    const API_BASE = "";

    // State Variables
    let decisionsChart = null;
    let currentDbTable = "users";

    // DOM Elements
    const navItems = document.querySelectorAll(".nav-item");
    const panels = document.querySelectorAll(".panel");
    const dbTabBtns = document.querySelectorAll(".db-tab-btn");
    const refreshBtn = document.getElementById("btn-refresh-data");

    // Toast Notification helper
    function showToast(message, type = "info") {
        const toast = document.getElementById("toast");
        const icon = document.getElementById("toast-icon");
        const msgSpan = document.getElementById("toast-message");

        // Remove old classes
        toast.className = "toast";
        toast.classList.add(type);

        // Icon settings
        icon.className = "fa-solid";
        if (type === "success") {
            icon.classList.add("fa-circle-check");
        } else if (type === "error") {
            icon.classList.add("fa-circle-exclamation");
        } else {
            icon.classList.add("fa-circle-info");
        }

        msgSpan.textContent = message;
        toast.classList.remove("hidden");

        // Auto hide after 3 seconds
        setTimeout(() => {
            toast.classList.add("hidden");
        }, 3000);
    }

    // Tab Switching Navigation
    navItems.forEach(item => {
        item.addEventListener("click", (e) => {
            e.preventDefault();
            const target = item.getAttribute("data-target");

            navItems.forEach(i => i.classList.remove("active"));
            panels.forEach(p => p.classList.remove("active"));

            item.classList.add("active");
            document.getElementById(`panel-${target}`).classList.add("active");

            // Custom tasks based on panel
            if (target === "database") {
                loadDatabaseTable(currentDbTable);
            } else if (target === "overview") {
                loadOverviewStats();
            } else {
                populateDropdowns();
            }
        });
    });

    // DB Viewer Sub-Tab Switching
    dbTabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            dbTabBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            
            const tableName = btn.getAttribute("data-table");
            currentDbTable = tableName;
            loadDatabaseTable(tableName);
        });
    });

    // Global Refresh Trigger
    if (refreshBtn) {
        refreshBtn.addEventListener("click", () => {
            loadOverviewStats();
            populateDropdowns();
            showToast("Database telemetry stats synchronized!", "success");
        });
    }

    // --- FORM SUBMISSIONS ---

    // 1. Register User Form
    const createUserForm = document.getElementById("form-create-user");
    if (createUserForm) {
        createUserForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(createUserForm);
            const data = Object.fromEntries(formData.entries());

            try {
                const response = await fetch(`${API_BASE}/api/users`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(data)
                });

                if (!response.ok) {
                    const err = await response.json();
                    throw new Error(err.detail || "Failed to register user");
                }

                showToast(`Personnel "${data.name}" registered successfully!`, "success");
                createUserForm.reset();
                loadOverviewStats();
            } catch (error) {
                showToast(error.message, "error");
            }
        });
    }

    // 2. Register Station Location Form
    const createLocationForm = document.getElementById("form-create-location");
    if (createLocationForm) {
        createLocationForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(createLocationForm);
            const data = Object.fromEntries(formData.entries());
            
            data.base_water_threshold = parseFloat(data.base_water_threshold);
            data.latitude = parseFloat(data.latitude);
            data.longitude = parseFloat(data.longitude);

            try {
                const response = await fetch(`${API_BASE}/api/locations`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(data)
                });

                if (!response.ok) {
                    const err = await response.json();
                    throw new Error(err.detail || "Failed to create station profile");
                }

                showToast(`Station "${data.location_name}" registered successfully!`, "success");
                createLocationForm.reset();
                populateDropdowns();
                loadOverviewStats();
            } catch (error) {
                showToast(error.message, "error");
            }
        });
    }

    // 3. Log Telemetry Reading Form
    const createReadingForm = document.getElementById("form-create-reading");
    if (createReadingForm) {
        createReadingForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(createReadingForm);
            const data = Object.fromEntries(formData.entries());

            data.location_id = parseInt(data.location_id);
            data.water_level = parseFloat(data.water_level);
            data.rainfall = parseFloat(data.rainfall);
            data.temperature = parseFloat(data.temperature);
            data.humidity = parseFloat(data.humidity);
            data.river_flow = parseFloat(data.river_flow);
            data.wind_speed = parseFloat(data.wind_speed);

            try {
                const response = await fetch(`${API_BASE}/api/readings`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(data)
                });

                if (!response.ok) {
                    const err = await response.json();
                    throw new Error(err.detail || "Failed to submit telemetry");
                }

                showToast("Sensor reading logged successfully!", "success");
                createReadingForm.reset();
                populateDropdowns();
                loadOverviewStats();
            } catch (error) {
                showToast(error.message, "error");
            }
        });
    }

    // 4. Run Risk Evaluation Form
    const runPredictionForm = document.getElementById("form-run-prediction");
    if (runPredictionForm) {
        runPredictionForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(runPredictionForm);
            const data = Object.fromEntries(formData.entries());

            data.reading_id = parseInt(data.reading_id);
            data.model_id = parseInt(data.model_id);

            const displayDiv = document.getElementById("prediction-result-display");
            const contentDiv = document.getElementById("prediction-result-content");
            const placeholderDiv = displayDiv.querySelector(".result-placeholder");

            try {
                // Show loading
                showToast("Evaluating flood alert metrics...", "info");
                
                const response = await fetch(`${API_BASE}/api/predictions/run`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(data)
                });

                if (!response.ok) {
                    const err = await response.json();
                    throw new Error(err.detail || "Prediction failed");
                }

                const result = await response.json();
                
                // Show content card
                placeholderDiv.classList.add("hidden");
                contentDiv.classList.remove("hidden");

                // Update UI elements
                const statusBox = document.getElementById("result-status-box");
                const statusTitle = document.getElementById("result-status-title");
                const statusIcon = document.getElementById("result-status-icon");
                const probPercent = document.getElementById("result-probability-percent");
                const alertLevel = document.getElementById("result-alert-level");
                const recommendation = document.getElementById("result-recommendation");
                const predTime = document.getElementById("result-prediction-time");
                const modelName = document.getElementById("result-model-name");

                // Reset warning alert boxes
                statusBox.className = "result-status-header";
                statusIcon.className = "fa-solid";

                if (result.risk_level === "High") {
                    statusBox.classList.add("warning");
                    statusIcon.classList.add("fa-triangle-exclamation");
                    statusTitle.textContent = "High Risk Warning";
                } else if (result.risk_level === "Medium") {
                    statusBox.classList.add("watch");
                    statusIcon.classList.add("fa-cloud-showers-water");
                    statusTitle.textContent = "Medium Risk Watch";
                } else {
                    statusBox.classList.add("safe");
                    statusIcon.classList.add("fa-circle-check");
                    statusTitle.textContent = "Low Risk / Safe";
                }

                probPercent.textContent = `${result.flood_probability}%`;
                alertLevel.textContent = result.alert;
                recommendation.textContent = result.recommendation;
                predTime.textContent = new Date(result.prediction_time).toLocaleString();
                
                // Fetch model name
                const modelRes = await fetch(`${API_BASE}/api/models`);
                if (modelRes.ok) {
                    const modelsList = await modelRes.json();
                    const activeModel = modelsList.find(m => m.model_id === result.model_id);
                    modelName.textContent = activeModel ? activeModel.model_name : `Model #${result.model_id}`;
                }

                showToast("Flood alert evaluation complete!", "success");
                loadOverviewStats();
            } catch (error) {
                showToast(error.message, "error");
            }
        });
    }

    // --- UTILITY POPULATE DROPDOWNS ---
    async function populateDropdowns() {
        try {
            // 1. Populate Stations in Dropdowns
            const locSelect = document.getElementById("read-location-id");
            if (locSelect) {
                const res = await fetch(`${API_BASE}/api/locations`);
                if (res.ok) {
                    const locations = await res.json();
                    
                    // Clear and append
                    locSelect.innerHTML = '<option value="">-- Select River Station --</option>';
                    locations.forEach(loc => {
                        const opt = document.createElement("option");
                        opt.value = loc.location_id;
                        opt.textContent = `${loc.location_name} (Threshold: ${loc.base_water_threshold}m)`;
                        locSelect.appendChild(opt);
                    });
                }
            }

            // 2. Populate Pending Readings in Prediction form
            const readSelect = document.getElementById("pred-reading-id");
            if (readSelect) {
                const [readingsRes, locationsRes] = await Promise.all([
                    fetch(`${API_BASE}/api/readings`),
                    fetch(`${API_BASE}/api/locations`)
                ]);

                if (readingsRes.ok && locationsRes.ok) {
                    const readings = await readingsRes.json();
                    const locations = await locationsRes.json();
                    const locMap = {};
                    locations.forEach(l => { locMap[l.location_id] = l.location_name; });

                    readSelect.innerHTML = '<option value="">-- Choose Reading Entry --</option>';
                    // Sort descending by time
                    readings.sort((a, b) => new Date(b.reading_time) - new Date(a.reading_time));
                    readings.forEach(rd => {
                        const opt = document.createElement("option");
                        opt.value = rd.reading_id;
                        const dateStr = new Date(rd.reading_time).toLocaleTimeString();
                        const locName = locMap[rd.location_id] || `Station #${rd.location_id}`;
                        opt.textContent = `Reading #${rd.reading_id} [${locName}] at ${dateStr} (Water: ${rd.water_level}m, Rain: ${rd.rainfall}mm)`;
                        readSelect.appendChild(opt);
                    });
                }
            }

            // 3. Populate ML Models
            const modelSelect = document.getElementById("pred-model-id");
            if (modelSelect) {
                const res = await fetch(`${API_BASE}/api/models`);
                if (res.ok) {
                    const models = await res.json();
                    modelSelect.innerHTML = '<option value="">-- Select Model --</option>';
                    models.forEach(m => {
                        const opt = document.createElement("option");
                        opt.value = m.model_id;
                        opt.textContent = m.model_name;
                        modelSelect.appendChild(opt);
                    });
                    
                    // Auto select first model if available
                    if (models.length > 0) {
                        modelSelect.value = models[0].model_id;
                    }
                }
            }

        } catch (error) {
            console.error("Error populating dropdowns:", error);
        }
    }

    // --- OVERVIEW PANEL STATISTICS & CHARTS ---
    async function loadOverviewStats() {
        try {
            const res = await fetch(`${API_BASE}/api/dashboard/stats`);
            if (!res.ok) return;

            const stats = await res.json();

            // Update Counts
            document.getElementById("stat-active-alerts").textContent = stats.active_alerts;
            document.getElementById("stat-total-readings").textContent = stats.total_readings;
            document.getElementById("stat-avg-water").textContent = `${stats.average_water_level} m`;
            document.getElementById("stat-max-rain").textContent = `${stats.max_rainfall} mm`;

            // Draw/Update Decision Chart (Chart.js)
            const ctx = document.getElementById("chart-decisions");
            if (ctx) {
                const chartData = [stats.low_risk_count, stats.medium_risk_count, stats.high_risk_count];
                
                if (decisionsChart) {
                    decisionsChart.data.datasets[0].data = chartData;
                    decisionsChart.update();
                } else {
                    decisionsChart = new Chart(ctx, {
                        type: "doughnut",
                        data: {
                            labels: ["Low Risk / Safe", "Medium Risk / Watch", "High Risk / Warning"],
                            datasets: [{
                                data: chartData,
                                backgroundColor: ["#10b981", "#f59e0b", "#ef4444"],
                                borderColor: "rgba(255,255,255,0.08)",
                                borderWidth: 2
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: {
                                    position: "bottom",
                                    labels: {
                                        color: "#94a3b8",
                                        font: { family: "'Inter', sans-serif", size: 12 }
                                    }
                                }
                            },
                            cutout: "70%"
                        }
                    });
                }
            }

            // Update Active Model Info
            const modelsRes = await fetch(`${API_BASE}/api/models`);
            if (modelsRes.ok) {
                const models = await modelsRes.json();
                if (models.length > 0) {
                    const activeModel = models[0];
                    document.getElementById("active-model-id").textContent = activeModel.model_id;
                    document.getElementById("model-status-text").textContent = activeModel.model_name.includes("Active") ? activeModel.model_name : `${activeModel.model_name}`;
                    
                    const trainAcc = activeModel.training_accuracy ? `${(activeModel.training_accuracy * 100).toFixed(1)}%` : "--%";
                    const testAcc = activeModel.testing_accuracy ? `${(activeModel.testing_accuracy * 100).toFixed(1)}%` : "--%";
                    
                    document.getElementById("model-train-acc").textContent = trainAcc;
                    document.getElementById("model-test-acc").textContent = testAcc;
                }
            }

            // Render Recent Predictions
            const predsRes = await fetch(`${API_BASE}/api/predictions`);
            if (predsRes.ok) {
                const predictions = await predsRes.json();
                const tbody = document.querySelector("#table-recent-predictions tbody");
                tbody.innerHTML = "";

                if (predictions.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="5" class="text-center">No evaluations run yet.</td></tr>';
                } else {
                    // Sort descending by prediction time
                    predictions.sort((a, b) => new Date(b.prediction_time) - new Date(a.prediction_time));
                    
                    predictions.slice(0, 5).forEach(p => {
                        const tr = document.createElement("tr");
                        const dateStr = new Date(p.prediction_time).toLocaleTimeString();
                        
                        let badgeClass = "safe";
                        if (p.risk_level === "High") badgeClass = "warning";
                        else if (p.risk_level === "Medium") badgeClass = "watch";

                        tr.innerHTML = `
                            <td>#${p.prediction_id}</td>
                            <td>#${p.reading_id}</td>
                            <td><span class="badge ${badgeClass}">${p.risk_level}</span></td>
                            <td><strong>${p.flood_probability}%</strong></td>
                            <td>${p.alert}</td>
                        `;
                        tbody.appendChild(tr);
                    });
                }
            }

        } catch (error) {
            console.error("Error loading overview stats:", error);
        }
    }

    // --- DATABASE VIEWER ---
    async function loadDatabaseTable(tableName) {
        try {
            const table = document.getElementById("table-database-view");
            const thead = table.querySelector("thead");
            const tbody = table.querySelector("tbody");

            thead.innerHTML = "";
            tbody.innerHTML = "";

            if (tableName === "users") {
                thead.innerHTML = `
                    <tr>
                        <th>User ID</th>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Role</th>
                        <th>Created At</th>
                    </tr>
                `;
                
                const res = await fetch(`${API_BASE}/api/users`);
                if (res.ok) {
                    const users = await res.json();
                    if (users.length === 0) {
                        tbody.innerHTML = '<tr><td colspan="5" class="text-center">No users registered yet.</td></tr>';
                    } else {
                        users.forEach(u => {
                            const tr = document.createElement("tr");
                            tr.innerHTML = `
                                <td>#${u.user_id}</td>
                                <td><strong>${u.name}</strong></td>
                                <td>${u.email}</td>
                                <td>${u.role}</td>
                                <td>${new Date(u.created_at).toLocaleString()}</td>
                            `;
                            tbody.appendChild(tr);
                        });
                    }
                }
            } else if (tableName === "locations") {
                thead.innerHTML = `
                    <tr>
                        <th>Station ID</th>
                        <th>Name</th>
                        <th>Threshold Water</th>
                        <th>Latitude</th>
                        <th>Longitude</th>
                    </tr>
                `;
                const res = await fetch(`${API_BASE}/api/locations`);
                if (res.ok) {
                    const stations = await res.json();
                    if (stations.length === 0) {
                        tbody.innerHTML = '<tr><td colspan="5" class="text-center">No stations registered yet.</td></tr>';
                    } else {
                        stations.forEach(st => {
                            const tr = document.createElement("tr");
                            tr.innerHTML = `
                                <td>#${st.location_id}</td>
                                <td><strong>${st.location_name}</strong></td>
                                <td><span class="badge watch">${st.base_water_threshold} m</span></td>
                                <td>${st.latitude.toFixed(4)}</td>
                                <td>${st.longitude.toFixed(4)}</td>
                            `;
                            tbody.appendChild(tr);
                        });
                    }
                }
            } else if (tableName === "readings") {
                thead.innerHTML = `
                    <tr>
                        <th>Reading ID</th>
                        <th>Station ID</th>
                        <th>Water Level</th>
                        <th>Rainfall</th>
                        <th>Temp / Humidity</th>
                        <th>River Flow / Wind</th>
                        <th>Time</th>
                    </tr>
                `;
                const [readingsRes, locationsRes] = await Promise.all([
                    fetch(`${API_BASE}/api/readings`),
                    fetch(`${API_BASE}/api/locations`)
                ]);
                
                if (readingsRes.ok && locationsRes.ok) {
                    const readings = await readingsRes.json();
                    const locations = await locationsRes.json();
                    const locMap = {};
                    locations.forEach(l => { locMap[l.location_id] = l.location_name; });

                    if (readings.length === 0) {
                        tbody.innerHTML = '<tr><td colspan="7" class="text-center">No sensor logs available.</td></tr>';
                    } else {
                        readings.sort((a,b) => new Date(b.reading_time) - new Date(a.reading_time));
                        readings.forEach(rd => {
                            const tr = document.createElement("tr");
                            const locName = locMap[rd.location_id] || `Station #${rd.location_id}`;
                            tr.innerHTML = `
                                <td>#${rd.reading_id}</td>
                                <td><strong>${locName}</strong> (#${rd.location_id})</td>
                                <td><span class="badge blue">${rd.water_level} m</span></td>
                                <td>${rd.rainfall} mm</td>
                                <td>${rd.temperature}°C / ${rd.humidity}%</td>
                                <td>${rd.river_flow} m³/s / ${rd.wind_speed} km/h</td>
                                <td>${new Date(rd.reading_time).toLocaleString()}</td>
                            `;
                            tbody.appendChild(tr);
                        });
                    }
                }
            } else if (tableName === "predictions") {
                thead.innerHTML = `
                    <tr>
                        <th>Prediction ID</th>
                        <th>Reading ID</th>
                        <th>Risk Level</th>
                        <th>Probability</th>
                        <th>Alert Status</th>
                        <th>Recommendation</th>
                        <th>Time</th>
                    </tr>
                `;
                const res = await fetch(`${API_BASE}/api/predictions`);
                if (res.ok) {
                    const predictions = await res.json();
                    if (predictions.length === 0) {
                        tbody.innerHTML = '<tr><td colspan="7" class="text-center">No evaluations stored in database.</td></tr>';
                    } else {
                        predictions.sort((a,b) => new Date(b.prediction_time) - new Date(a.prediction_time));
                        predictions.forEach(p => {
                            const tr = document.createElement("tr");
                            let badgeClass = "safe";
                            if (p.risk_level === "High") badgeClass = "warning";
                            else if (p.risk_level === "Medium") badgeClass = "watch";

                            tr.innerHTML = `
                                <td>#${p.prediction_id}</td>
                                <td>#${p.reading_id}</td>
                                <td><span class="badge ${badgeClass}">${p.risk_level}</span></td>
                                <td><strong>${p.flood_probability}%</strong></td>
                                <td>${p.alert}</td>
                                <td>${p.recommendation}</td>
                                <td>${new Date(p.prediction_time).toLocaleString()}</td>
                            `;
                            tbody.appendChild(tr);
                        });
                    }
                }
            }
        } catch (error) {
            console.error("Error loading database table:", error);
            showToast("Failed to load database content", "error");
        }
    }

    // --- INITIALIZATION ---
    loadOverviewStats();
    populateDropdowns();
});
