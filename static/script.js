// ============================================================
//  JARVIS — Web Terminal Script
// ============================================================
const socket = io();
const logsEl    = document.getElementById('logs');
const statusTxt = document.getElementById('status-text');
const circle    = document.getElementById('pulse-circle');
const connEl    = document.getElementById('conn-status');
const cmdCount  = document.getElementById('cmd-count');
const modeTxt   = document.getElementById('mode-text');

let commands = 0;

// ------------------------------------------------------------
//  Socket events
// ------------------------------------------------------------
socket.on('connect', () => {
    connEl.textContent = '● Ulandi';
    connEl.className = 'conn-online';
    addLog('🟢 Server bilan ulanish o\'rnatildi.', 'neon');
    modeTxt.textContent = 'Online';
});

socket.on('disconnect', () => {
    connEl.textContent = '● Uzildi';
    connEl.className = 'conn-offline';
    addLog('🔴 Server bilan ulanish uzildi.', 'error');
    modeTxt.textContent = 'Offline';
    setStatus('idle');
});

socket.on('log', (data) => {
    addLog(data.msg, data.type || 'info');
    // User messages = command count
    if (data.type === 'user') {
        commands++;
        cmdCount.textContent = commands;
    }
});

socket.on('status', (data) => {
    setStatus(data.status);
});

// ------------------------------------------------------------
//  Status indicator
// ------------------------------------------------------------
function setStatus(status) {
    circle.className = 'circle';
    if (status === 'listening') {
        circle.classList.add('listening');
        statusTxt.textContent = 'Eshityapman...';
        modeTxt.textContent = 'Tinglash';
    } else if (status === 'processing') {
        circle.classList.add('processing');
        statusTxt.textContent = 'O\'ylayapman...';
        modeTxt.textContent = 'Ishlayapman';
    } else {
        circle.classList.add('idle');
        statusTxt.textContent = 'Kutmoqda...';
        modeTxt.textContent = 'Kutish';
    }
}

// ------------------------------------------------------------
//  Add log entry
// ------------------------------------------------------------
function addLog(message, type) {
    // Remove welcome placeholder
    const welcome = logsEl.querySelector('.welcome-msg');
    if (welcome) welcome.remove();

    const now = new Date();
    const timeStr = now.toLocaleTimeString('uz-UZ', {
        hour: '2-digit', minute: '2-digit', second: '2-digit'
    });

    const entry = document.createElement('div');
    entry.className = `log-entry log-${type}`;

    const timeSpan = document.createElement('span');
    timeSpan.className = 'log-time';
    timeSpan.textContent = timeStr;

    const msgSpan = document.createElement('span');
    msgSpan.className = 'log-msg';
    msgSpan.textContent = message;

    entry.appendChild(timeSpan);
    entry.appendChild(msgSpan);
    logsEl.appendChild(entry);

    // Auto-scroll
    logsEl.scrollTop = logsEl.scrollHeight;

    // Keep max 200 log entries
    while (logsEl.children.length > 200) {
        logsEl.removeChild(logsEl.firstChild);
    }
}

// ------------------------------------------------------------
//  Clear logs
// ------------------------------------------------------------
function clearLogs() {
    logsEl.innerHTML = '<div class="welcome-msg"><span class="welcome-icon">🧹</span><span>Loglar tozalandi.</span></div>';
}
