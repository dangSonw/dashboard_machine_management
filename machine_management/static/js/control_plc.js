let isConnected = false;
let pollInterval = null;
let isEditingParams = false;
let editTimeout;
let emptyModeState = 0;
let autoModeState = 0;
let manualModeState = 0;
let x100State = 0;
let x112State = 0;
let x110State = 0;
let x117State = 0;
let x124State = 0;
let x125State = 0;
let x151State = 0;

document.addEventListener('DOMContentLoaded', () => {
    $(document).on('focus', 'input[id^="input_D"]', function() {
        isEditingParams = true;
        clearTimeout(editTimeout);
    });
    $(document).on('change', 'input[id^="input_D"]', function() {
        isEditingParams = true;
        clearTimeout(editTimeout);
    });

    // Set current date
    const dateEl = document.getElementById('current-date');
    if (dateEl) {
        const now = new Date();
        const days = ['Chủ nhật', 'Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7'];
        dateEl.textContent = `${days[now.getDay()]}, ${String(now.getDate()).padStart(2,'0')}/${String(now.getMonth()+1).padStart(2,'0')}/${now.getFullYear()}`;
    }
});

function toggleConnect() {
    const action = isConnected ? 'disconnect' : 'connect';
    fetch('/api/plc/connect/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({action: action})
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') {
            isConnected = data.connected;
            updateConnectUI();
            if (isConnected) {
                pollInterval = setInterval(pollPlcStatus, 1000);
            } else {
                clearInterval(pollInterval);
            }
        } else {
            alert("Connection error: " + data.message);
        }
    })
    .catch(err => alert("System error: " + err));
}

function updateConnectUI() {
    const dot = document.getElementById('plc_connection_dot');
    const text = document.getElementById('plc_connection_text');
    const connectBtn = document.getElementById('connect-btn');
    const statusPlc = document.getElementById('status-plc');
    const note = document.getElementById('status_note');

    if (isConnected) {
        if (dot) dot.className = "w-2 h-2 rounded-full bg-green-500";
        if (text) text.innerText = "PLC Connected";
        if (note) note.innerText = "System ready...";
        if (connectBtn) {
            connectBtn.className = "px-4 py-2 text-xs font-bold rounded-full border transition-colors shadow-sm bg-red-600 text-white border-red-600 hover:bg-red-700";
            connectBtn.innerText = "DISCONNECT PLC";
        }
        if (statusPlc) statusPlc.innerText = "Running";
    } else {
        if (dot) dot.className = "w-2 h-2 rounded-full bg-red-500";
        if (text) text.innerText = "PLC Disconnected";
        if (note) note.innerText = "System waiting for connection...";
        if (connectBtn) {
            connectBtn.className = "px-4 py-2 text-xs font-bold rounded-full border transition-colors shadow-sm bg-blue-600 text-white border-blue-600 hover:bg-blue-700";
            connectBtn.innerText = "CONNECT PLC";
        }
        if (statusPlc) statusPlc.innerText = "Standby";
    }
}

const plcDebugLogs = [];
function debugLog(level, msg, data) {
    const now = new Date();
    const ts = now.toTimeString().slice(0, 8);
    const entry = { ts, level, msg, data };
    plcDebugLogs.unshift(entry);
    if (plcDebugLogs.length > 50) plcDebugLogs.pop();
    renderDebugPanel();
    console.log(`[PLC ${level}] ${ts} ${msg}`, data || '');
}

function renderDebugPanel() {
    const panel = document.getElementById('plc-debug-log');
    if (!panel) return;

    const levelConfig = {
        OK:      { icon: '✅', bg: 'bg-blue-100',   text: 'text-blue-700',   border: 'border-blue-200',   label: 'SUCCESS' },
        ERR:     { icon: '❌', bg: 'bg-red-100',    text: 'text-red-700',    border: 'border-red-200',    label: 'ERROR' },
        WARN:    { icon: '⚠️', bg: 'bg-amber-100',  text: 'text-amber-700',  border: 'border-amber-200',  label: 'WARNING' },
        INFO:    { icon: 'ℹ️', bg: 'bg-cyan-100',   text: 'text-cyan-700',   border: 'border-cyan-200',   label: 'INFO' },
        READBACK:{ icon: '🔍', bg: 'bg-purple-100', text: 'text-purple-700', border: 'border-purple-200', label: 'READBACK' }
    };

    const logs = plcDebugLogs.slice(0, 10);
    panel.innerHTML = logs.map(e => {
        const cfg = levelConfig[e.level] || { icon: '•', bg: 'bg-slate-200', text: 'text-slate-700', border: 'border-slate-300', label: 'LOG' };
        return `
            <tr class="hover:bg-slate-100 transition-colors">
                <td class="p-4 text-sm font-semibold text-slate-700">${e.ts}</td>
                <td class="p-4 text-sm text-slate-700">${e.level}</td>
                <td class="p-4 text-sm text-slate-500">${e.msg}</td>
                <td class="p-4">
                    <span class="px-3 py-1 text-[10px] font-bold ${cfg.bg} ${cfg.text} ${cfg.border} rounded-full">${cfg.label}</span>
                </td>
            </tr>`;
    }).join('');
}

// Toggle System Power (X200)
const x200State = { isPowering: false };

function toggleSystemPower(checked) {
    if (!isConnected) {
        alert("Please connect to PLC before sending command!");
        // Reset checkbox
        const cb = document.getElementById('toggle-x200');
        if (cb) cb.checked = false;
        return;
    }
    if (checked) {
        if (x200State.isPowering) return;
        x200State.isPowering = true;

        const card = document.getElementById('system-power-card');
        const statusEl = document.getElementById('status-x200');
        const note = document.getElementById('status_note');

        if (statusEl) statusEl.innerText = 'Turning ON...';
        if (note) note.innerText = 'Sending ON POWER (X200) command to PLC...';
        if (card) card.className = card.className.replace('bg-slate-50', 'bg-gradient-to-tl from-blue-600 to-cyan-400');

        debugLog('INFO', 'Starting ON POWER command → send X200 (pulse)');

        fetch('/api/plc/command/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({command: 'X200', pulse: true, pulse_ms: 1500})
        })
        .then(res => res.json())
        .then(data => {
            x200State.isPowering = false;
            if (data.status === 'ok') {
                debugLog('OK', '✅ X200 (ON POWER) command successfully received by PLC', data);
                if (statusEl) statusEl.innerText = 'SYSTEM ON';
                if (note) note.innerText = '✅ X200 ON — Entire system is turned on!';
            } else {
                debugLog('ERR', '❌ X200 failed', data);
                if (statusEl) statusEl.innerText = 'ERROR';
                if (note) note.innerText = '❌ X200 failed: ' + (data.message || '');
                if (card) card.className = card.className.replace('bg-gradient-to-tl from-blue-600 to-cyan-400', 'bg-slate-50');
                const cb = document.getElementById('toggle-x200');
                if (cb) cb.checked = false;
            }
        })
        .catch(err => {
            x200State.isPowering = false;
            debugLog('ERR', '❌ Network error sending X200', { error: String(err) });
            if (statusEl) statusEl.innerText = 'NETWORK ERROR';
            if (note) note.innerText = '❌ Network error: ' + err;
            if (card) card.className = card.className.replace('bg-gradient-to-tl from-blue-600 to-cyan-400', 'bg-slate-50');
            const cb = document.getElementById('toggle-x200');
            if (cb) cb.checked = false;
        });
    } else {
        // Power off
        if (!isConnected) return;
        const note = document.getElementById('status_note');
        const statusEl = document.getElementById('status-x200');
        const card = document.getElementById('system-power-card');
        if (note) note.innerText = 'Sending RESET command (M5001)...';
        debugLog('INFO', 'Power OFF → Sending reset M5001');

        fetch('/api/plc/command/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({command: 'M5001', value: 1})
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'ok') {
                debugLog('OK', 'System power OFF reset sent', data);
                if (statusEl) statusEl.innerText = 'Inactive';
                if (note) note.innerText = '✅ System turned off.';
                if (card) card.className = card.className.replace('bg-gradient-to-tl from-blue-600 to-cyan-400', 'bg-slate-50');
            }
        });
    }
}

// Toggle Auto Mode (M10)
function toggleAutoMode(checked) {
    if (!isConnected) {
        alert("Please connect to PLC before sending command!");
        const cb = document.getElementById('toggle-m10');
        if (cb) cb.checked = false;
        return;
    }
    const note = document.getElementById('status_note');
    const newState = checked ? 1 : 0;

    note.innerText = `Sending ${checked ? 'ON' : 'OFF'} Auto Mode command (M10)...`;
    debugLog('INFO', `Toggle Auto Mode (M10) → ${newState}`);

    fetch('/api/plc/command/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({command: 'M10', value: newState})
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') {
            autoModeState = newState;
            note.innerText = `Auto Mode (M10=${newState}) OK.`;
        } else {
            note.innerText = `❌ Auto Mode failed: ${data.message || ''}`;
            const cb = document.getElementById('toggle-m10');
            if (cb) cb.checked = !checked;
        }
    })
    .catch(err => {
        note.innerText = `⚠ Error: ` + err;
        debugLog('ERR', `Network error sending M10`, err);
        const cb = document.getElementById('toggle-m10');
        if (cb) cb.checked = !checked;
    });
}

// Toggle Empty Mode (X304)
function toggleEmptyMode(checked) {
    if (!isConnected) {
        alert("Please connect to PLC before sending command!");
        const cb = document.getElementById('toggle-x304');
        if (cb) cb.checked = false;
        return;
    }
    const note = document.getElementById('status_note');
    const newState = checked ? 1 : 0;

    note.innerText = `Sending ${checked ? 'ON' : 'OFF'} Empty Mode command (X304)...`;
    debugLog('INFO', `Toggle Empty Mode (X304) → ${newState}`);

    fetch('/api/plc/command/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({command: 'X304', value: newState})
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') {
            emptyModeState = newState;
            note.innerText = `Empty Mode (X304=${newState}) OK.`;
        } else {
            note.innerText = `❌ Empty Mode failed: ${data.message || ''}`;
            const cb = document.getElementById('toggle-x304');
            if (cb) cb.checked = !checked;
        }
    })
    .catch(err => {
        note.innerText = `⚠ Error: ` + err;
        debugLog('ERR', `Network error sending X304`, err);
        const cb = document.getElementById('toggle-x304');
        if (cb) cb.checked = !checked;
    });
}

// Send simple PLC command as bool
function sendPlcCommandBool(address, checked) {
    if (!isConnected) {
        alert("Please connect to PLC before sending command!");
        const cb = document.getElementById('toggle-' + address.toLowerCase());
        if (cb) cb.checked = false;
        return;
    }
    const note = document.getElementById('status_note');
    const value = checked ? 1 : 0;
    note.innerText = `Sending ${address} = ${value}...`;

    fetch('/api/plc/command/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({command: address, value: value})
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') {
            note.innerText = `${address}=${value} executed successfully.`;
        } else {
            note.innerText = `${address} failed: ${data.message || ''}`;
            const cb = document.getElementById('toggle-' + address.toLowerCase());
            if (cb) cb.checked = !checked;
        }
    })
    .catch(err => {
        note.innerText = `⚠ Error sending ${address}: ` + err;
        const cb = document.getElementById('toggle-' + address.toLowerCase());
        if (cb) cb.checked = !checked;
    });
}

// Control Servo (X110 ON / X117 OFF)
function controlServo(checked) {
    if (!isConnected) {
        alert("Please connect to PLC before sending command!");
        const cb = document.getElementById('toggle-servo');
        if (cb) cb.checked = false;
        return;
    }
    const note = document.getElementById('status_note');
    const statusEl = document.getElementById('status-servo');
    const led = document.getElementById('status-servo-led');
    const address = checked ? 'X117' : 'X110';

    note.innerText = `Sending SERVO ${checked ? 'ON' : 'OFF'} command (${address})...`;
    debugLog('INFO', `Servo ${checked ? 'ON' : 'OFF'} → ${address}`);

    fetch('/api/plc/command/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({command: address, pulse: true, pulse_ms: 200})
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') {
            if (statusEl) statusEl.innerText = checked ? 'On' : 'Off';
            if (led) led.className = `w-1.5 h-1.5 rounded-full ${checked ? 'bg-green-500' : 'bg-slate-300'}`;
            note.innerText = `Servo ${checked ? 'ON' : 'OFF'} OK.`;
        } else {
            note.innerText = `Servo command failed: ${data.message || ''}`;
            const cb = document.getElementById('toggle-servo');
            if (cb) cb.checked = !checked;
        }
    })
    .catch(err => {
        note.innerText = `⚠ Error: ` + err;
        debugLog('ERR', `Network error sending servo command`, err);
        const cb = document.getElementById('toggle-servo');
        if (cb) cb.checked = !checked;
    });
}

// Momentary control (hold to activate)
function controlMomentary(address, state, event) {
    if (event && event.type.startsWith('touch')) {
        if (event.cancelable) event.preventDefault();
    }

    if (!isConnected) {
        if (state === 1) alert("Please connect to PLC before sending command!");
        return;
    }

    const note = document.getElementById('status_note');

    if (state === 1) {
        note.innerText = `Sending PRESS (${address} = 1)...`;
        debugLog('INFO', `Press ${address} → 1`);
        fetch('/api/plc/command/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({command: address, value: 1})
        }).then(res => res.json()).then(data => {
            if (data.status === 'ok') note.innerText = `${address} pressed OK.`;
        });
    } else {
        note.innerText = `Sending RELEASE (${address} = 0)...`;
        debugLog('INFO', `Release ${address} → 0`);
        fetch('/api/plc/command/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({command: address, value: 0})
        }).then(res => res.json()).then(data => {
            if (data.status === 'ok') note.innerText = `${address} released OK.`;
        });
    }
}

// Light OFF (X151=0 then X152 momentary)
function controlLightOffMomentary(state, event) {
    if (event && event.type.startsWith('touch')) {
        if (event.cancelable) event.preventDefault();
    }

    if (!isConnected) {
        if (state === 1) alert("Please connect to PLC before sending command!");
        return;
    }

    const note = document.getElementById('status_note');

    if (state === 1) {
        note.innerText = "Sending LIGHT OFF (X151=0, X152=1)...";
        debugLog('INFO', 'Press LIGHT OFF → X151=0, X152=1');
        fetch('/api/plc/command/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({command: 'X151', value: 0})
        }).then(() => {
            return fetch('/api/plc/command/', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({command: 'X152', value: 1})
            });
        }).then(res => res.json()).then(data => {
            if (data.status === 'ok') note.innerText = "Light OFF pressed OK.";
        });
    } else {
        note.innerText = "Releasing LIGHT OFF (X152=0)...";
        debugLog('INFO', 'Release LIGHT OFF → X152=0');
        fetch('/api/plc/command/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({command: 'X152', value: 0})
        }).then(res => res.json()).then(data => {
            if (data.status === 'ok') note.innerText = "Light OFF released OK.";
        });
    }
}

// Save Parameters
function saveParameters() {
    if (!isConnected) {
        alert("Please connect to PLC before updating parameters!");
        return;
    }
    const data = {
        D500: document.getElementById('input_D500').value,
        D502: document.getElementById('input_D502').value,
        D300: document.getElementById('input_D300').value,
        D302: document.getElementById('input_D302').value,
        D304: document.getElementById('input_D304').value,
        D306: document.getElementById('input_D306').value,
    };

    document.getElementById('status_note').innerText = "Updating parameters...";

    fetch('/api/plc/write_params/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(resData => {
        if (resData.status === 'ok') {
            document.getElementById('status_note').innerText = "Parameters updated successfully.";
            isEditingParams = false;
        } else {
            document.getElementById('status_note').innerText = "⚠ Update error: " + (resData.message || 'Failed');
        }
    })
    .catch(err => {
        document.getElementById('status_note').innerText = "⚠ Connection error: " + err;
    });
}

// Poll PLC Status
function pollPlcStatus() {
    if (!isConnected) return;
    fetch('/api/plc/status/')
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') {
            // Update D values
            if (data.data) {
                $('#val_cycle_time').text(data.data.cycle !== undefined ? data.data.cycle : 0);
                $('#val_D10').text(data.data.in !== undefined ? data.data.in : 0);
                $('#val_D14').text(data.data.ok !== undefined ? data.data.ok : 0);
                $('#val_D16').text(data.data.ng !== undefined ? data.data.ng : 0);
                $('#val_D12').text(data.data.out !== undefined ? data.data.out : 0);
                $('#val_D20').text(data.data.rate !== undefined ? data.data.rate : 0);
            }

            // Auto Mode (M10)
            if (data.m10 !== undefined) {
                autoModeState = data.m10 ? 1 : 0;
                const cb = document.getElementById('toggle-m10');
                if (cb && !cb.matches(':active')) cb.checked = !!data.m10;
                const statusM10 = document.getElementById('status-m10');
                if (statusM10) statusM10.innerText = data.m10 ? 'Running' : 'Off';
                const card = document.getElementById('auto-mode-card');
                if (card) {
                    if (data.m10) {
                        card.className = "bg-gradient-to-tl from-blue-600 to-cyan-400 p-4 rounded-2xl shadow-md border border-blue-500/30 flex flex-col justify-between h-32 text-white";
                    } else {
                        card.className = "bg-slate-50 p-4 rounded-2xl border border-slate-200 flex flex-col justify-between h-32 hover:bg-slate-100 transition-colors";
                    }
                }
            }

            // Manual Mode (M20)
            if (data.m20 !== undefined) {
                manualModeState = data.m20 ? 1 : 0;
                const cb = document.getElementById('toggle-m20');
                if (cb && !cb.matches(':active')) cb.checked = !!data.m20;
                const statusM20 = document.getElementById('status-m20');
                if (statusM20) statusM20.innerText = data.m20 ? 'Running' : 'Off';
                const card = document.getElementById('manual-mode-card');
                if (card) {
                    if (data.m20) {
                        card.className = "bg-gradient-to-tl from-blue-600 to-cyan-400 p-4 rounded-2xl shadow-md border border-blue-500/30 flex flex-col justify-between h-32 text-white";
                    } else {
                        card.className = "bg-slate-50 p-4 rounded-2xl border border-slate-200 flex flex-col justify-between h-32 hover:bg-slate-100 transition-colors";
                    }
                }
            }

            // Empty Mode (X304)
            if (data.x304 !== undefined) {
                emptyModeState = data.x304 ? 1 : 0;
                const cb = document.getElementById('toggle-x304');
                if (cb && !cb.matches(':active')) cb.checked = !!data.x304;
                const statusX304 = document.getElementById('status-x304');
                if (statusX304) statusX304.innerText = data.x304 ? 'On' : 'Off';
                const card = document.getElementById('empty-mode-card');
                if (card) {
                    if (data.x304) {
                        card.className = "bg-gradient-to-tl from-blue-600 to-cyan-400 p-4 rounded-2xl shadow-md border border-blue-500/30 flex flex-col justify-between h-32 text-white";
                    } else {
                        card.className = "bg-slate-50 p-4 rounded-2xl border border-slate-200 flex flex-col justify-between h-32 hover:bg-slate-100 transition-colors";
                    }
                }
            }

            // X100 (ORIGIN)
            if (data.x100 !== undefined) {
                x100State = data.x100 ? 1 : 0;
                const el = document.getElementById('status-x100');
                if (el) el.innerText = data.x100 ? 'Active' : 'Ready';
            }

            // X112 (STEP RUN)
            if (data.x112 !== undefined) {
                x112State = data.x112 ? 1 : 0;
                const el = document.getElementById('status-x112');
                if (el) el.innerText = data.x112 ? 'Active' : 'Ready';
            }

            // X110 (JOG UP / Servo OFF)
            if (data.x110 !== undefined) {
                x110State = data.x110 ? 1 : 0;
                if (!data.x110 && data.x117) {
                    // Servo is ON when X117 is active
                }
            }

            // X117 (JOG DOWN / Servo ON)
            if (data.x117 !== undefined) {
                x117State = data.x117 ? 1 : 0;
                const isServoOn = !!data.x117;
                const cb = document.getElementById('toggle-servo');
                if (cb && !cb.matches(':active')) cb.checked = isServoOn;
                const statusServo = document.getElementById('status-servo');
                if (statusServo) statusServo.innerText = isServoOn ? 'On' : 'Off';
                const led = document.getElementById('status-servo-led');
                if (led) led.className = `w-1.5 h-1.5 rounded-full ${isServoOn ? 'bg-green-500' : 'bg-slate-300'}`;
            }

            // X125 (START)
            if (data.x125 !== undefined) {
                x125State = data.x125 ? 1 : 0;
                const el = document.getElementById('status-x125');
                if (el) el.innerText = data.x125 ? 'Active' : 'Ready';
            }

            // X124 (STOP)
            if (data.x124 !== undefined) {
                x124State = data.x124 ? 1 : 0;
                const el = document.getElementById('status-x124');
                if (el) el.innerText = data.x124 ? 'Active' : 'Standby';
            }

            // X151 (LIGHT ON)
            if (data.x151 !== undefined) {
                x151State = data.x151 ? 1 : 0;
            }

            // Parameters
            if (data.params && !isEditingParams) {
                let activeElem = document.activeElement;
                if (activeElem.id !== 'input_D500') $('#input_D500').val(data.params.D500);
                if (activeElem.id !== 'input_D502') $('#input_D502').val(data.params.D502);
                if (activeElem.id !== 'input_D300') $('#input_D300').val(data.params.D300);
                if (activeElem.id !== 'input_D302') $('#input_D302').val(data.params.D302);
                if (activeElem.id !== 'input_D304') $('#input_D304').val(data.params.D304);
                if (activeElem.id !== 'input_D306') $('#input_D306').val(data.params.D306);
            }

        } else if (data.status === 'failed') {
            isConnected = false;
            updateConnectUI();
            clearInterval(pollInterval);
        }
    })
    .catch(err => {
        console.warn('[PLC Poll] Connection error:', err);
    });
}

// Send PLC command (generic)
function sendPlcCommand(address) {
    if (!isConnected) {
        alert("Please connect to PLC before sending command!");
        return;
    }
    const note = document.getElementById('status_note');
    note.innerText = "Sending command to: " + address + " ...";

    fetch('/api/plc/command/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({command: address, value: 1})
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') {
            note.innerText = "Lệnh " + address + " executed successfully.";
        } else {
            note.innerText = "Lệnh " + address + " failed (" + (data.message || 'unknown') + ")";
        }
    })
    .catch(err => {
        note.innerText = "⚠ Error sending " + address + ": " + err;
    });
}

// Suppress unhandled promise rejections from extensions
window.addEventListener('unhandledrejection', function(event) {
    if (!event.reason) {
        event.preventDefault();
        return;
    }
    var reasonStr = (event.reason.stack || String(event.reason)).toLowerCase();
    if (reasonStr.includes('onboarding') ||
        reasonStr.includes('extension') ||
        reasonStr.includes('rejectfunction') ||
        reasonStr.includes('chrome-extension') ||
        event.reason.toString().includes('chrome-extension')) {
        event.preventDefault();
        return;
    }
    console.warn('[PLC] Unhandled Promise Rejection:', event.reason);
    event.preventDefault();
});