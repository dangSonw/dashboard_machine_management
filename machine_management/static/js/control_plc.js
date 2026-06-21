// ===== Toggle Address Mapping =====
const TOGGLE_ADDRESSES = {
    'sys-power': 'X200',
    'auto-mode': 'X201',
    'manual-mode': 'X202',
    'reset-sys': 'X203',
    'empty-mode': 'X204',
    'servo-on': 'X210'
};

// ===== Global State =====
let plcConnected = false;
let pollingInterval = null;

// ===== PLC Config (read from data attributes) =====
const configEl = document.getElementById('plc-config');
const PLC_CONFIG = {
    csrfToken: configEl ? configEl.dataset.csrfToken : '',
    apiUrlConnect: configEl ? configEl.dataset.urlConnect : '',
    apiUrlCommand: configEl ? configEl.dataset.urlCommand : '',
    apiUrlReadDevice: configEl ? configEl.dataset.urlReadDevice : ''
};

// ===== PLC Connection =====
function updateConnectionUI(connected, message) {
    const badge = document.getElementById('plc-status-badge');
    const detail = document.getElementById('connection-detail');
    const switchEl = document.getElementById('plc-connect-switch');
    const label = document.getElementById('plc-connect-label');

    if (connected) {
        badge.textContent = '● Connected';
        badge.className = 'px-3 py-1 rounded-full text-[10px] font-bold';
        badge.style.background = 'rgba(16,185,129,0.9)';
        badge.style.color = '#fff';
        detail.textContent = message || 'PLC connection active';
        detail.className = 'text-[10px] text-emerald-500 font-medium';
        switchEl.checked = true;
        label.textContent = 'ON';
    } else {
        badge.textContent = '● Disconnected';
        badge.className = 'px-3 py-1 rounded-full text-[10px] font-bold';
        badge.style.background = 'rgba(239,68,68,0.9)';
        badge.style.color = '#fff';
        detail.textContent = message || 'Click to connect';
        detail.className = 'text-[10px] text-slate-400';
        switchEl.checked = false;
        label.textContent = 'OFF';
    }
}

function connectPLC() {
    const switchEl = document.getElementById('plc-connect-switch');
    switchEl.disabled = true;
    document.getElementById('connection-detail').textContent = 'Connecting...';

    fetch(PLC_CONFIG.apiUrlConnect, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': PLC_CONFIG.csrfToken },
        body: JSON.stringify({ action: 'connect' })
    })
    .then(res => res.json())
    .then(data => {
        if (data.connected) {
            plcConnected = true;
            updateConnectionUI(true);
            startPolling();
        } else {
            plcConnected = false;
            updateConnectionUI(false, 'Failed: ' + (data.message || 'Unable to connect'));
        }
    })
    .catch(err => {
        plcConnected = false;
        updateConnectionUI(false, 'Connection error');
    })
    .finally(() => { switchEl.disabled = false; });
}

function disconnectPLC() {
    const switchEl = document.getElementById('plc-connect-switch');
    switchEl.disabled = true;

    fetch(PLC_CONFIG.apiUrlConnect, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': PLC_CONFIG.csrfToken },
        body: JSON.stringify({ action: 'disconnect' })
    })
    .then(res => res.json())
    .then(() => {
        plcConnected = false;
        stopPolling();
        updateConnectionUI(false, 'Disconnected');
    })
    .catch(() => {})
    .finally(() => { switchEl.disabled = false; });
}

document.getElementById('plc-connect-switch').addEventListener('change', function() {
    if (this.checked) { connectPLC(); }
    else { disconnectPLC(); }
});

// ===== Toggle Switch PLC Control =====
function handleToggleSwitch(el) {
    if (!plcConnected) { el.checked = !el.checked; return; }
    const address = el.dataset.address;
    const value = el.checked ? 1 : 0;
    const statusEl = document.getElementById(el.id + '-status');

    fetch(PLC_CONFIG.apiUrlCommand, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': PLC_CONFIG.csrfToken },
        body: JSON.stringify({ command: address, value: value, readback: true })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') {
            if (statusEl) statusEl.textContent = el.checked ? 'Active' : 'Inactive';
            // Update auto-mode card style
            if (el.id === 'auto-mode') {
                const card = document.getElementById('auto-mode-card');
                if (el.checked) {
                    card.className = 'bg-gradient-to-tl from-blue-600 to-cyan-400 p-4 rounded-2xl shadow-md border border-blue-500/30 flex flex-col justify-between h-32 text-white';
                    statusEl.parentElement.parentElement.querySelectorAll('svg').forEach(s => s.classList.remove('text-slate-500'));
                    statusEl.parentElement.parentElement.querySelectorAll('svg').forEach(s => s.classList.add('text-white'));
                    statusEl.parentElement.parentElement.querySelectorAll('p').forEach(p => { p.classList.remove('text-slate-800'); p.classList.remove('text-slate-500'); p.classList.add('text-white'); });
                    statusEl.textContent = 'Running';
                } else {
                    card.className = 'bg-slate-50 p-4 rounded-2xl border border-slate-200 flex flex-col justify-between h-32 hover:bg-slate-100 transition-colors';
                    statusEl.parentElement.parentElement.querySelectorAll('svg').forEach(s => s.classList.add('text-slate-500'));
                    statusEl.parentElement.parentElement.querySelectorAll('p').forEach(p => { p.classList.add('text-slate-800'); p.classList.add('text-slate-500'); p.classList.remove('text-white'); });
                    statusEl.textContent = 'Off';
                }
            }
        } else {
            el.checked = !el.checked;
        }
    })
    .catch(() => { el.checked = !el.checked; });
}

// Bind toggle switches
Object.keys(TOGGLE_ADDRESSES).forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener('change', function() { handleToggleSwitch(this); });
});

// ===== Momentary Button =====
function plcMomentary(btn) {
    if (!plcConnected) return;
    const address = btn.dataset.address;

    fetch(PLC_CONFIG.apiUrlCommand, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': PLC_CONFIG.csrfToken },
        body: JSON.stringify({ command: address, value: 1, readback: false })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') {
            setTimeout(() => {
                fetch(PLC_CONFIG.apiUrlCommand, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': PLC_CONFIG.csrfToken },
                    body: JSON.stringify({ command: address, value: 0, readback: false })
                });
            }, 200);
        }
    })
    .catch(err => console.error('Momentary error:', err));
}

// ===== Polling & Monitor =====
function readAllToggles() {
    if (!plcConnected) return;
    Object.entries(TOGGLE_ADDRESSES).forEach(([id, address]) => {
        fetch(PLC_CONFIG.apiUrlReadDevice + '?address=' + address)
        .then(res => res.json())
        .then(data => {
            if (data.status === 'ok') {
                const el = document.getElementById(id);
                const val = data.value === 1;
                if (el && el.checked !== val) el.checked = val;
                // Update monitor
                const monVal = document.getElementById('mon-' + address.toLowerCase());
                const monStatus = document.getElementById('mon-' + address.toLowerCase() + '-status');
                if (monVal) monVal.textContent = data.value;
                if (monStatus) {
                    monStatus.textContent = val ? 'ON' : 'OFF';
                    monStatus.className = val ? 'text-[10px] px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-600 font-bold' : 'text-[10px] px-2 py-0.5 rounded-full bg-red-100 text-red-600 font-bold';
                }
            }
        })
        .catch(() => {});
    });
}

function refreshMonitor() { readAllToggles(); }

function startPolling() {
    if (pollingInterval) clearInterval(pollingInterval);
    readAllToggles();
    pollingInterval = setInterval(readAllToggles, 2000);
}

function stopPolling() {
    if (pollingInterval) { clearInterval(pollingInterval); pollingInterval = null; }
}

// ===== Update Parameters =====
function updateParameters() {
    if (!plcConnected) { alert('Please connect to PLC first'); return; }
    const manualSpeed = document.getElementById('manual-speed').value;
    const autoSpeed = document.getElementById('auto-speed').value;
    const targetPos = document.getElementById('target-position').value;

    fetch(PLC_CONFIG.apiUrlCommand, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': PLC_CONFIG.csrfToken },
        body: JSON.stringify({ command: 'params', manual_speed: manualSpeed, auto_speed: autoSpeed, target_position: targetPos })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') {
            alert('Parameters updated successfully');
        } else {
            alert('Failed: ' + (data.message || 'Unknown error'));
        }
    })
    .catch(err => alert('Error updating parameters'));
}

// ===== Auto-check connection on load =====
document.addEventListener('DOMContentLoaded', function() {
    fetch(PLC_CONFIG.apiUrlConnect)
    .then(res => res.json())
    .then(data => {
        if (data.connected) {
            plcConnected = true;
            updateConnectionUI(true);
            startPolling();
        }
    })
    .catch(() => {});
});