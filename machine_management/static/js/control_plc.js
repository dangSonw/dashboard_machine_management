// ===== Toggle Address Mapping =====
const TOGGLE_ADDRESSES = {
    'sys-power': 'X200',
    'auto-mode': 'X300',
    'manual-mode': 'X301',
    'empty-mode': 'X304',
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
let isDragging = false;
let dragStartX = 0;
let dragged = false;
const DRAG_THRESHOLD = 30;

function updateConnectionUI(connected, message) {
    const detail = document.getElementById('connection-detail');
    const switchEl = document.getElementById('plc-connect-switch');
    const label = document.getElementById('plc-connect-label');

    if (connected) {
        detail.textContent = message || 'PLC connection active';
        detail.className = 'text-[10px] text-emerald-500 font-medium';
        switchEl.checked = true;
        label.textContent = 'ON';
    } else {
        detail.textContent = message || 'Click to connect';
        detail.className = 'text-[10px] text-slate-400';
        switchEl.checked = false;
        label.textContent = 'OFF';
    }
}

// ===== Activate Manual Mode as default when PLC connected =====
function activateManualMode() {
    const address = TOGGLE_ADDRESSES['manual-mode'];
    const el = document.getElementById('manual-mode');
    if (!address || !el) return;

    fetch(PLC_CONFIG.apiUrlCommand, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': PLC_CONFIG.csrfToken },
        body: JSON.stringify({ command: address, value: 1, readback: true })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') {
            el.checked = true;
            updateToggleCardVisual('manual-mode', true);
            // Ensure auto-mode is OFF
            const autoEl = document.getElementById('auto-mode');
            const autoAddr = TOGGLE_ADDRESSES['auto-mode'];
            if (autoEl) {
                autoEl.checked = false;
                fetch(PLC_CONFIG.apiUrlCommand, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': PLC_CONFIG.csrfToken },
                    body: JSON.stringify({ command: autoAddr, value: 0, readback: true })
                })
                .then(r => r.json())
                .then(d => { if (d.status === 'ok') updateToggleCardVisual('auto-mode', false); })
                .catch(() => {});
            }
        }
    })
    .catch(() => {});
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
            activateManualMode();
        } else {
            plcConnected = false;
            updateConnectionUI(false, 'Failed: ' + (data.message || 'Unable to connect'));
            alert('PLC connection failed: ' + (data.message || 'Unable to connect'));
        }
    })
    .catch(err => {
        plcConnected = false;
        updateConnectionUI(false, 'Connection error');
        alert('PLC connection failed: Connection error');
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
    if (dragged) { dragged = false; return; }
    if (this.checked) { connectPLC(); }
    else { disconnectPLC(); }
});

// ===== Drag Support for PLC Toggle =====
const plcToggle = document.getElementById('plc-connect-switch');
const plcToggleWrapper = document.querySelector('.plc-toggle-wrapper');

if (plcToggle && plcToggleWrapper) {
    plcToggleWrapper.addEventListener('mousedown', function(e) {
        if (e.target.tagName === 'INPUT') return;
        isDragging = true;
        dragStartX = e.clientX;
        dragged = false;
        plcToggleWrapper.style.cursor = 'grabbing';
        e.preventDefault();
    });

    document.addEventListener('mousemove', function(e) {
        if (!isDragging) return;
        const deltaX = e.clientX - dragStartX;
        if (Math.abs(deltaX) > DRAG_THRESHOLD) {
            dragged = true;
            const shouldBeChecked = deltaX > 0;
            if (plcToggle.checked !== shouldBeChecked) {
                plcToggle.checked = shouldBeChecked;
                plcToggle.dispatchEvent(new Event('change'));
            }
            isDragging = false;
            plcToggleWrapper.style.cursor = 'pointer';
        }
    });

    document.addEventListener('mouseup', function() {
        if (isDragging) {
            isDragging = false;
            plcToggleWrapper.style.cursor = 'pointer';
            if (!dragged) {
                plcToggle.checked = !plcToggle.checked;
                plcToggle.dispatchEvent(new Event('change'));
            }
        }
    });

    plcToggleWrapper.style.cursor = 'pointer';
}

// ===== Update Toggle Card Visual Style =====
function updateToggleCardVisual(id, isOn) {
    const card = document.getElementById(id + '-card');
    const icon = document.getElementById(id + '-icon');
    const statusEl = document.getElementById(id + '-status');
    const label = document.getElementById(id + '-label');
    if (!card) return;

    if (id === 'sys-power') {
        if (isOn) {
            card.className = 'bg-gradient-to-tl from-emerald-600 to-teal-400 p-4 rounded-2xl shadow-md border border-emerald-500/30 flex flex-col justify-between h-32 hover:shadow-lg transition-all';
            if (icon) { icon.classList.remove('text-slate-500', 'dark:text-slate-400'); icon.classList.add('text-white'); }
            if (label) { label.classList.remove('text-slate-800', 'dark:text-white'); label.classList.add('text-white'); }
            if (statusEl) { statusEl.textContent = 'Running'; statusEl.classList.remove('text-slate-500', 'dark:text-slate-400'); statusEl.classList.add('text-white/80'); }
        } else {
            card.className = 'bg-slate-50 dark:bg-slate-800 p-4 rounded-2xl border border-slate-200 dark:border-slate-700 flex flex-col justify-between h-32 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors';
            if (icon) { icon.classList.remove('text-white'); icon.classList.add('text-slate-500', 'dark:text-slate-400'); }
            if (label) { label.classList.remove('text-white'); label.classList.add('text-slate-800', 'dark:text-white'); }
            if (statusEl) { statusEl.textContent = 'Inactive'; statusEl.classList.remove('text-white/80'); statusEl.classList.add('text-slate-500', 'dark:text-slate-400'); }
        }
    } else if (id === 'manual-mode') {
        if (isOn) {
            card.className = 'bg-gradient-to-tl from-orange-600 to-amber-400 p-4 rounded-2xl shadow-md border border-orange-500/30 flex flex-col justify-between h-32 hover:shadow-lg transition-all';
            if (icon) { icon.classList.remove('text-slate-500', 'dark:text-slate-400'); icon.classList.add('text-white'); }
            if (label) { label.classList.remove('text-slate-800', 'dark:text-white'); label.classList.add('text-white'); }
            if (statusEl) { statusEl.textContent = 'Active'; statusEl.classList.remove('text-slate-500', 'dark:text-slate-400'); statusEl.classList.add('text-white/80'); }
        } else {
            card.className = 'bg-slate-50 dark:bg-slate-800 p-4 rounded-2xl border border-slate-200 dark:border-slate-700 flex flex-col justify-between h-32 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors';
            if (icon) { icon.classList.remove('text-white'); icon.classList.add('text-slate-500', 'dark:text-slate-400'); }
            if (label) { label.classList.remove('text-white'); label.classList.add('text-slate-800', 'dark:text-white'); }
            if (statusEl) { statusEl.textContent = 'Off'; statusEl.classList.remove('text-white/80'); statusEl.classList.add('text-slate-500', 'dark:text-slate-400'); }
        }
    } else if (id === 'auto-mode') {
        if (isOn) {
            card.className = 'bg-gradient-to-tl from-blue-600 to-cyan-400 p-4 rounded-2xl shadow-md border border-blue-500/30 flex flex-col justify-between h-32 text-white';
            if (icon) { icon.classList.remove('text-slate-500', 'dark:text-slate-400'); icon.classList.add('text-white'); }
            if (label) { label.classList.remove('text-slate-800', 'dark:text-white'); label.classList.add('text-white'); }
            if (statusEl) { statusEl.textContent = 'Running'; statusEl.classList.remove('text-slate-500', 'dark:text-slate-400'); statusEl.classList.add('text-white/80'); }
        } else {
            card.className = 'bg-slate-50 dark:bg-slate-800 p-4 rounded-2xl border border-slate-200 dark:border-slate-700 flex flex-col justify-between h-32 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors';
            if (icon) { icon.classList.remove('text-white'); icon.classList.add('text-slate-500', 'dark:text-slate-400'); }
            if (label) { label.classList.remove('text-white'); label.classList.add('text-slate-800', 'dark:text-white'); }
            if (statusEl) { statusEl.textContent = 'Off'; statusEl.classList.remove('text-white/80'); statusEl.classList.add('text-slate-500', 'dark:text-slate-400'); }
        }
    } else {
        // Generic toggle (manual-mode, empty-mode, servo-on)
        if (statusEl) statusEl.textContent = isOn ? 'Active' : 'Inactive';
    }
}

// ===== Toggle Switch PLC Control =====
// ===== Mutual Exclusion Map (when key is ON -> force all values to OFF) =====
const TOGGLE_EXCLUSIONS = {
    'auto-mode':  ['manual-mode'],
    'manual-mode': ['auto-mode']
};

// ===== Extra OFF commands: when key is ON -> write 0 to these addresses =====
const TOGGLE_OFF_COMMANDS = {
    'auto-mode': ['M20']
};

function handleToggleSwitch(el) {
    if (!plcConnected) { el.checked = !el.checked; alert('Please connect to PLC first'); return; }
    const address = el.dataset.address;
    const value = el.checked ? 1 : 0;

    fetch(PLC_CONFIG.apiUrlCommand, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': PLC_CONFIG.csrfToken },
        body: JSON.stringify({ command: address, value: value, readback: true })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') {
            updateToggleCardVisual(el.id, el.checked);

            // Mutual exclusion: force linked toggles OFF
            if (value === 1 && TOGGLE_EXCLUSIONS[el.id]) {
                TOGGLE_EXCLUSIONS[el.id].forEach(otherId => {
                    const otherEl = document.getElementById(otherId);
                    const otherAddress = TOGGLE_ADDRESSES[otherId];
                    // Always send OFF regardless of UI state
                    if (otherEl) {
                        otherEl.checked = false;
                        fetch(PLC_CONFIG.apiUrlCommand, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': PLC_CONFIG.csrfToken },
                            body: JSON.stringify({ command: otherAddress, value: 0, readback: true })
                        })
                        .then(r => r.json())
                        .then(d => { if (d.status === 'ok') updateToggleCardVisual(otherId, false); })
                        .catch(() => {});
                    }
                });
            }
            // Extra OFF commands (e.g. write 0 to M20 when auto-mode ON)
            if (value === 1 && TOGGLE_OFF_COMMANDS[el.id]) {
                TOGGLE_OFF_COMMANDS[el.id].forEach(addr => {
                    fetch(PLC_CONFIG.apiUrlCommand, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': PLC_CONFIG.csrfToken },
                        body: JSON.stringify({ command: addr, value: 0, readback: false })
                    }).catch(() => {});
                });
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

// ===== Pulse Button (rising edge only: write 1, no auto-reset) =====
function plcPulse(btn) {
    if (!plcConnected) { alert('Please connect to PLC first'); return; }
    const address = btn.dataset.address;

    btn.disabled = true;
    btn.classList.add('opacity-60', 'cursor-not-allowed');

    fetch(PLC_CONFIG.apiUrlCommand, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': PLC_CONFIG.csrfToken },
        body: JSON.stringify({ command: address, value: 1, readback: false })
    })
    .then(res => res.json())
    .then(data => {
        setTimeout(() => {
            btn.disabled = false;
            btn.classList.remove('opacity-60', 'cursor-not-allowed');
        }, 500);
    })
    .catch(err => {
        console.error('Pulse error:', err);
        btn.disabled = false;
        btn.classList.remove('opacity-60', 'cursor-not-allowed');
    });
}

// ===== Momentary Button =====
function plcMomentary(btn) {
    if (!plcConnected) { alert('Please connect to PLC first'); return; }
    const address = btn.dataset.address;
    const statusEl = btn.closest('div').querySelector('[id$="-status"]');

    // Disable button & show pressing state
    btn.disabled = true;
    btn.classList.add('opacity-60', 'cursor-not-allowed');
    if (statusEl) statusEl.textContent = 'Resetting...';

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
                })
                .then(() => {
                    if (statusEl) statusEl.textContent = 'Done';
                    setTimeout(() => {
                        btn.disabled = false;
                        btn.classList.remove('opacity-60', 'cursor-not-allowed');
                        if (statusEl) statusEl.textContent = 'Ready';
                    }, 1000);
                });
            }, 200);
        } else {
            btn.disabled = false;
            btn.classList.remove('opacity-60', 'cursor-not-allowed');
            if (statusEl) statusEl.textContent = 'Failed';
            setTimeout(() => { if (statusEl) statusEl.textContent = 'Ready'; }, 1500);
        }
    })
    .catch(err => {
        console.error('Momentary error:', err);
        btn.disabled = false;
        btn.classList.remove('opacity-60', 'cursor-not-allowed');
        if (statusEl) statusEl.textContent = 'Error';
        setTimeout(() => { if (statusEl) statusEl.textContent = 'Ready'; }, 1500);
    });
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
                if (el && el.checked !== val) {
                    el.checked = val;
                    // Sync card visual when PLC value changes externally
                    updateToggleCardVisual(id, val);
                }
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
            activateManualMode();
        }
    })
    .catch(() => {});
});