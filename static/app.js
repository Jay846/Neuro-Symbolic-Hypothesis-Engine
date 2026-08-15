let fitChart = null;
let currentData = null; // Stores currently loaded X and Y data
let leaderboardModels = []; // Discovered equations

document.addEventListener("DOMContentLoaded", () => {
    initChart();
    
    // File upload label update
    const fileInput = document.getElementById("csv-file");
    fileInput.addEventListener("change", (e) => {
        const fileName = e.target.files[0] ? e.target.files[0].name : "Choose CSV file...";
        const labelText = document.querySelector(".file-upload-wrapper span");
        labelText.textContent = fileName;
        labelText.classList.add("file-name-display");
        addLog(`Selected file: ${fileName}`, "info");
    });
    
    // Run Discovery Form
    const form = document.getElementById("analyze-form");
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const file = fileInput.files[0];
        if (!file) return;
        
        const domain = document.getElementById("domain-context").value;
        const desc = document.getElementById("data-description").value;
        
        const formData = new FormData();
        formData.append("file", file);
        formData.append("domain_context", domain);
        formData.append("data_description", desc);
        
        setLoading(true);
        addLog("Uploading CSV and starting Neuro-Symbolic search loop...", "info");
        
        try {
            const response = await fetch("/api/analyze", {
                method: "POST",
                body: formData
            });
            
            const responseText = await response.text();
            let responseData;
            try {
                responseData = JSON.parse(responseText);
            } catch (jsonErr) {
                throw new Error(`Invalid server response (not JSON): ${responseText.substring(0, 150)}...`);
            }

            if (!response.ok) {
                throw new Error(responseData.detail || "Server error.");
            }
            
            handleResult(responseData);
        } catch (error) {
            addLog(`Error: ${error.message}`, "error");
        } finally {
            setLoading(false);
        }
    });
    
    // Demo Run Button
    const btnDemo = document.getElementById("btn-demo");
    btnDemo.addEventListener("click", async () => {
        const domain = document.getElementById("domain-context").value;
        const desc = document.getElementById("data-description").value;
        
        setLoading(true);
        addLog("Starting Demo Search on synthetic quadratic data with noise...", "info");
        
        try {
            const formData = new FormData();
            formData.append("domain_context", domain);
            formData.append("data_description", desc);
            
            const response = await fetch("/api/demo", {
                method: "POST",
                body: formData
            });
            
            const responseText = await response.text();
            let responseData;
            try {
                responseData = JSON.parse(responseText);
            } catch (jsonErr) {
                throw new Error(`Invalid server response (not JSON): ${responseText.substring(0, 150)}...`);
            }

            if (!response.ok) {
                throw new Error(responseData.detail || "Server error.");
            }
            
            handleResult(responseData);
        } catch (error) {
            addLog(`Error: ${error.message}`, "error");
        } finally {
            setLoading(false);
        }
    });
    
    // Clear logs button
    const btnClearLogs = document.getElementById("btn-clear-logs");
    btnClearLogs.addEventListener("click", () => {
        const consoleEl = document.getElementById("log-console");
        consoleEl.innerHTML = '<div class="terminal-line system-msg">Console logs cleared. Ready...</div>';
    });
    
    // Wolfram terminal query integration
    async function sendTerminalQuery() {
        const inputEl = document.getElementById("terminal-input");
        const query = inputEl.value.trim();
        if (!query) return;
        
        addLog(`Querying Wolfram: "${query}"`, "info");
        inputEl.value = "";
        
        try {
            const formData = new FormData();
            formData.append("query", query);
            
            const response = await fetch("/api/wolfram", {
                method: "POST",
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            addLog(`Wolfram Result: ${data.result}`, "success");
        } catch (error) {
            addLog(`Wolfram Error: ${error.message}`, "error");
        }
    }
    
    const btnSend = document.getElementById("btn-terminal-send");
    const inputEl = document.getElementById("terminal-input");
    
    btnSend.addEventListener("click", sendTerminalQuery);
    inputEl.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            sendTerminalQuery();
        }
    });
});

function initChart() {
    const ctx = document.getElementById("fit-chart").getContext("2d");
    fitChart = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [
                {
                    label: 'Raw Data',
                    data: [],
                    backgroundColor: 'rgba(0, 242, 254, 0.6)',
                    borderColor: 'rgba(0, 242, 254, 1)',
                    borderWidth: 1,
                    pointRadius: 5
                },
                {
                    label: 'Model Fit',
                    data: [],
                    type: 'line',
                    borderColor: '#4facfe',
                    borderWidth: 3,
                    fill: false,
                    pointRadius: 0,
                    tension: 0.1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#8b949e' }
                },
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#8b949e' }
                }
            },
            plugins: {
                legend: {
                    labels: { color: '#f0f3f6' }
                }
            }
        }
    });
}

function handleResult(data) {
    currentData = data;
    leaderboardModels = data.leaderboard;
    
    // Print logs
    data.logs.forEach(log => {
        let type = "system";
        if (log.includes("failed") || log.includes("Error") || log.includes("Skipping")) {
            type = "error";
        } else if (log.includes("successful") || log.includes("succeeded")) {
            type = "success";
        } else if (log.includes("Fitting") || log.includes("Attempt")) {
            type = "info";
        }
        addLog(log, type);
    });
    
    // Update Leaderboard
    updateLeaderboard();
    
    // Plot best fit (rank 1)
    if (leaderboardModels.length > 0) {
        plotModel(0);
    } else {
        // Plot raw data only
        plotRawDataOnly();
    }
}

function updateLeaderboard() {
    const tbody = document.querySelector("#leaderboard-table tbody");
    tbody.innerHTML = "";
    
    if (leaderboardModels.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="empty-state">No valid models found. Try checking logs for errors.</td></tr>`;
        return;
    }
    
    leaderboardModels.forEach((model, idx) => {
        const row = document.createElement("tr");
        if (idx === 0) row.classList.add("active-row");
        
        const r2Text = (typeof model.r2 === 'number') ? model.r2.toFixed(4) : "N/A";
        const aicText = (typeof model.aic === 'number') ? model.aic.toFixed(2) : "N/A";
        
        row.innerHTML = `
            <td>${idx + 1}</td>
            <td style="font-family: 'JetBrains Mono', monospace; font-size: 0.9rem;">${model.simplified_eq}</td>
            <td style="color: var(--accent-green); font-weight: 600;">${r2Text}</td>
            <td>${aicText}</td>
            <td><button class="btn-plot" onclick="plotModel(${idx})"><i class="fa-solid fa-chart-simple"></i> Plot</button></td>
        `;
        tbody.appendChild(row);
    });
}

function plotModel(index) {
    if (!currentData || !leaderboardModels[index]) return;
    
    const model = leaderboardModels[index];
    const xVals = currentData.x_data;
    const yVals = currentData.y_data;
    const yPred = model.y_pred;
    
    // Pair X and Y for scatter
    const rawPoints = xVals.map((x, i) => ({ x: x, y: yVals[i] }));
    
    // Pair X and Y_pred for line
    // Sort them by X so the line draws correctly without back-crossing
    const linePoints = xVals.map((x, i) => ({ x: x, y: yPred[i] }));
    linePoints.sort((a, b) => a.x - b.x);
    
    fitChart.data.datasets[0].data = rawPoints;
    fitChart.data.datasets[1].data = linePoints;
    fitChart.data.datasets[1].label = `Fit: ${model.simplified_eq}`;
    fitChart.update();
    
    // Update active row highlighting
    const rows = document.querySelectorAll("#leaderboard-table tbody tr");
    rows.forEach((row, i) => {
        if (i === index) {
            row.classList.add("active-row");
        } else {
            row.classList.remove("active-row");
        }
    });
    
    const r2Display = (typeof model.r2 === 'number') ? model.r2.toFixed(4) : "N/A";
    addLog(`Plotting Rank ${index + 1}: ${model.simplified_eq} (R² = ${r2Display})`, "info");
}

function plotRawDataOnly() {
    if (!currentData) return;
    const xVals = currentData.x_data;
    const yVals = currentData.y_data;
    const rawPoints = xVals.map((x, i) => ({ x: x, y: yVals[i] }));
    
    fitChart.data.datasets[0].data = rawPoints;
    fitChart.data.datasets[1].data = [];
    fitChart.data.datasets[1].label = "No Fit Available";
    fitChart.update();
}

function addLog(message, type = "system") {
    const consoleEl = document.getElementById("log-console");
    const line = document.createElement("div");
    line.className = `terminal-line ${type}-msg`;
    line.textContent = `> ${message}`;
    consoleEl.appendChild(line);
    
    // Auto scroll to bottom
    consoleEl.scrollTop = consoleEl.scrollHeight;
}

function setLoading(isLoading) {
    const btnRun = document.getElementById("btn-run");
    const btnDemo = document.getElementById("btn-demo");
    
    if (isLoading) {
        btnRun.disabled = true;
        btnDemo.disabled = true;
        btnRun.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Researching...`;
    } else {
        btnRun.disabled = false;
        btnDemo.disabled = false;
        btnRun.innerHTML = `<i class="fa-solid fa-play"></i> Run Discovery`;
    }
}
