let isConnected = false;
let pollInterval = null;
let isEditingParams = false;
let editTimeout;
let emptyModeState = 0;
let autoModeState = 0;

document.addEventListener('DOMContentLoaded', () => {
    $(document).on('focus', 'input[id^="input_D"]', function() {
        isEditingParams = true;
        clearTimeout(editTimeout);
    });
    $(document).on('change', 'input[id^="input_D"]', function() {
        isEditingParams = true;
        clearTimeout(editTimeout);
    });
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
    const note = document.getElementById('status_note');
    const connectBtn = document.querySelector('[onclick="toggleConnect()"]');
    if (isConnected) {
        dot.className = "badge badge-success";
        dot.innerText = "PLC Connected";
        note.innerText = "System ready...";
        if (connectBtn) {
            connectBtn.className = "btn btn-outline-danger btn-sm";
            connectBtn.innerText = "DISCONNECT";
        }
    } else {
        dot.className = "badge badge-danger";
        dot.innerText = "PLC Disconnected";
        note.innerText = "System waiting for connection...";
        if (connectBtn) {
            connectBtn.className = "btn btn-outline-info btn-sm";
            connectBtn.innerText = "CONNECT PLC";
        }
    }
}



const plcDebugLogs = [];
function debugLog(level, msg, data) {
    const now = new Date();
    const ts = now.toTimeString().slice(0,8) + '.' + String(now.getMilliseconds()).padStart(3,'0');
    const entry = { ts, level, msg, data };
    plcDebugLogs.unshift(entry);  // Mới nhất lên đầu
    if (plcDebugLogs.length > 50) plcDebugLogs.pop();
    renderDebugPanel();
    console.log(`[PLC ${level}] ${ts} ${msg}`, data || '');
}

function renderDebugPanel() {
    const panel = document.getElementById('plc-debug-log');
    if (!panel) return;
    panel.innerHTML = plcDebugLogs.slice(0, 20).map(e => {
        const icons = { OK: '✅', ERR: '❌', WARN: '⚠️', INFO: 'ℹ️', READBACK: '🔍' };
        const colors = { OK: '#00e676', ERR: '#ef5350', WARN: '#ff9800', INFO: '#42a5f5', READBACK: '#ce93d8' };
        const icon = icons[e.level] || '•';
        const color = colors[e.level] || '#ccc';
        let detail = '';
        if (e.data) {
            detail = '<span style="color:#aaa;font-size:0.85em;"> → ' +
                JSON.stringify(e.data).replace(/</g,'&lt;') + '</span>';
        }
        return `<div style="border-bottom:1px solid #333;padding:3px 0;">
            <span style="color:#888;font-size:0.8em;">${e.ts}</span>
            <span style="color:${color};margin:0 4px;">${icon}</span>
            <span style="color:#eee;">${e.msg}</span>${detail}
        </div>`;
    }).join('');
}



function pollPlcStatus() {
    if (!isConnected) return;
    fetch('/api/plc/status/')
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') {
            if(data.data) {
                $('#val_cycle_time').text(data.data.cycle !== undefined ? data.data.cycle : 0);
                $('#val_D10').text(data.data.in !== undefined ? data.data.in : 0);
                $('#val_D14').text(data.data.ok !== undefined ? data.data.ok : 0);
                $('#val_D16').text(data.data.ng !== undefined ? data.data.ng : 0);
                $('#val_D12').text(data.data.out !== undefined ? data.data.out : 0);
                $('#val_D20').text(data.data.rate !== undefined ? data.data.rate : 0);
            }
            

            
            if (data.m10 !== undefined) {
                autoModeState = data.m10 ? 1 : 0;
                $('#val_M10').text(data.m10 ? 'M10 ON' : 'M10 OFF');
                $('#val_M10').removeClass().addClass(data.m10 ? 'badge badge-success' : 'badge badge-secondary').css('font-size', '0.7em');
            }
            if (data.m20 !== undefined) {
                $('#val_M20').text(data.m20 ? 'M20 ON' : 'M20 OFF');
                $('#val_M20').removeClass().addClass(data.m20 ? 'badge badge-success' : 'badge badge-secondary').css('font-size', '0.7em');
            }
            if (data.x304 !== undefined) {
                emptyModeState = data.x304 ? 1 : 0;
                $('#val_X304').text(data.x304 ? 'X304 ON' : 'X304 OFF');
                $('#val_X304').removeClass().addClass(data.x304 ? 'badge badge-success' : 'badge badge-secondary').css('font-size', '0.7em');
            }
            if (data.m100 !== undefined) {
                $('#val_M100').text(data.m100 ? 'ON' : 'OFF');
                $('#val_M100').removeClass().addClass(data.m100 ? 'badge badge-success' : 'badge badge-secondary').css('font-size', '0.9em');
            }
            if (data.x10 !== undefined) {
                $('#val_X10').text(data.x10 ? 'ON' : 'OFF');
                $('#val_X10').removeClass().addClass(data.x10 ? 'badge badge-success' : 'badge badge-secondary').css('font-size', '0.7em');
            }
            if (data.x124 !== undefined) {
                $('#val_X124').text(data.x124 ? 'ON' : 'OFF');
                $('#val_X124').removeClass().addClass(data.x124 ? 'badge badge-success' : 'badge badge-secondary').css('font-size', '0.7em');
                $('#val_X124_menu').text(data.x124 ? 'X124 ON' : 'X124 OFF');
                $('#val_X124_menu').removeClass().addClass(data.x124 ? 'badge badge-success' : 'badge badge-secondary').css('font-size', '0.7em');
            }
            if (data.x125 !== undefined) {
                $('#val_X125').text(data.x125 ? 'ON' : 'OFF');
                $('#val_X125').removeClass().addClass(data.x125 ? 'badge badge-success' : 'badge badge-secondary').css('font-size', '0.9em');
                $('#val_X125_menu').text(data.x125 ? 'X125 ON' : 'X125 OFF');
                $('#val_X125_menu').removeClass().addClass(data.x125 ? 'badge badge-success' : 'badge badge-secondary').css('font-size', '0.7em');
            }
            if (data.x100 !== undefined) {
                $('#val_X100_servo').text(data.x100 ? 'X100 ON' : 'X100 OFF');
                $('#val_X100_servo').removeClass().addClass(data.x100 ? 'badge badge-success' : 'badge badge-secondary').css('font-size', '0.7em');
            }
            if (data.x112 !== undefined) {
                $('#val_X112_servo').text(data.x112 ? 'X112 ON' : 'X112 OFF');
                $('#val_X112_servo').removeClass().addClass(data.x112 ? 'badge badge-success' : 'badge badge-secondary').css('font-size', '0.7em');
            }
            if (data.x110 !== undefined) {
                $('#val_X110_servo').text(data.x110 ? 'X110 ON' : 'X110 OFF');
                $('#val_X110_servo').removeClass().addClass(data.x110 ? 'badge badge-success' : 'badge badge-secondary').css('font-size', '0.7em');
            }
            if (data.x117 !== undefined) {
                $('#val_X117_servo').text(data.x117 ? 'X117 ON' : 'X117 OFF');
                $('#val_X117_servo').removeClass().addClass(data.x117 ? 'badge badge-success' : 'badge badge-secondary').css('font-size', '0.7em');
            }
            if (data.x151 !== undefined) {
                $('#val_X151_light').text(data.x151 ? 'X151 ON' : 'X151 OFF');
                $('#val_X151_light').removeClass().addClass(data.x151 ? 'badge badge-success' : 'badge badge-secondary').css('font-size', '0.7em');
            }
            if (data.x152 !== undefined) {
                $('#val_X152_light').text(data.x152 ? 'X152 ON' : 'X152 OFF');
                $('#val_X152_light').removeClass().addClass(data.x152 ? 'badge badge-success' : 'badge badge-secondary').css('font-size', '0.7em');
            }
            if (data.y1 !== undefined) {
                $('#val_Y1').text(data.y1 ? 'ON' : 'OFF');
                $('#val_Y1').removeClass().addClass(data.y1 ? 'badge badge-success' : 'badge badge-secondary').css('font-size', '0.9em');
            }
            
            
            if(data.params && !isEditingParams) {
                let activeElem = document.activeElement;
                if(activeElem.id !== 'input_D500') $('#input_D500').val(data.params.D500);
                if(activeElem.id !== 'input_D502') $('#input_D502').val(data.params.D502);
                if(activeElem.id !== 'input_D300') $('#input_D300').val(data.params.D300);
                if(activeElem.id !== 'input_D302') $('#input_D302').val(data.params.D302);
                if(activeElem.id !== 'input_D304') $('#input_D304').val(data.params.D304);
                if(activeElem.id !== 'input_D306') $('#input_D306').val(data.params.D306);
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

function sendPlcCommand(address) {
    if(!isConnected) {
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
            note.innerText = "Lệnh " + address + " failed (" + (data.message || 'unknown reason') + ")";
        }
    })
    .catch(err => {
        console.warn('[PLC Command] Error:', err);
        note.innerText = "⚠ Error sending command " + address + ": " + err;
    });
}

function saveParameters() {
    if(!isConnected) {
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
            isEditingParams = false; // allow pulling fresh data
        } else {
            document.getElementById('status_note').innerText = "⚠ Update error: " + (resData.message || 'Failed');
        }
    })
    .catch(err => {
        console.warn('[PLC Params] Error:', err);
        document.getElementById('status_note').innerText = "⚠ Connection error while saving parameters: " + err;
    });
}



const x200State = { isPowering: false };

function onPowerSystem() {
    console.log("onPowerSystem() was called");
    if (!isConnected) {
        alert("Please connect to PLC before turning on the system!");
        return;
    }
    if (x200State.isPowering) return;

    x200State.isPowering = true;

    const btn       = document.getElementById('btn-x200-power');
    const led       = document.getElementById('led-x200');
    const statusTxt = document.getElementById('x200-status-text');
    const card      = document.getElementById('x200-power-card');
    const note      = document.getElementById('status_note');

    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="zmdi zmdi-rotate-right zmdi-hc-spin"></i>&nbsp; TURNING ON SYSTEM...';
    }
    if (led) led.className = 'w-4 h-4 rounded-full bg-yellow-500 mr-3 shadow-sm';
    if (statusTxt) {
        statusTxt.innerText = 'Sending X200...';
        statusTxt.className = 'mb-0 font-bold text-yellow-500 dark:text-yellow-400';
    }
    if (note) note.innerText = 'Sending ON POWER (X200) command to PLC...';

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
            if (led) led.className = 'w-4 h-4 rounded-full bg-green-500 mr-3 shadow-sm';
            if (statusTxt) {
                statusTxt.innerText = '✅ SYSTEM ON';
                statusTxt.className = 'mb-0 font-bold text-green-500';
            }
            if (note) note.innerText = '✅ X200 ON — Entire system is turned on!';
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = '<i class="fas fa-check"></i>&nbsp; SYSTEM TURNED ON (X200)';
            }
            setTimeout(() => {
                if (led) led.className = 'w-4 h-4 rounded-full bg-blue-500 mr-3 shadow-sm';
                if (statusTxt) {
                    statusTxt.innerText = 'SYSTEM READY';
                    statusTxt.className = 'mb-0 font-bold text-blue-500';
                }
                if (btn) {
                    btn.innerHTML = '<i class="fa fa-power-off mr-2"></i> SYSTEM POWER ON';
                }
            }, 6000);

        } else {
            // Failed
            const errMsg = `❌ X200 failed: ${data.message || 'Không rõ lý do'}`;
            debugLog('ERR', errMsg, data);
            if (led) led.className = 'w-4 h-4 rounded-full bg-red-500 mr-3 shadow-sm';
            if (statusTxt) {
                statusTxt.innerText = '❌ ERROR SENDING X200';
                statusTxt.className = 'mb-0 font-bold text-red-500';
            }
            if (note) note.innerText = errMsg;
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = '<i class="zmdi zmdi-power"></i>&nbsp; SYSTEM POWER ON (X200)';
                btn.className = 'btn btn-success btn-lg btn-block waves-effect mt-2 shadow';
            }
        }
    })
    .catch(err => {
        x200State.isPowering = false;
        const errMsg = `❌ Network error sending X200: ${err}`;
        debugLog('ERR', errMsg, { error: String(err) });
        if (led) led.className = 'rounded-circle bg-danger mr-2 shadow-sm';
        if (statusTxt) {
            statusTxt.innerText = '❌ NETWORK ERROR';
            statusTxt.className = 'font-weight-bold text-danger';
        }
        if (note) note.innerText = errMsg;
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<i class="zmdi zmdi-power"></i>&nbsp; SYSTEM POWER ON (X200)';
            btn.className = 'btn btn-success btn-lg btn-block waves-effect mt-2 shadow';
        }
    });
}

function controlY1(action) {
    if(!isConnected) {
        alert("Please connect to PLC before sending command!");
        return;
    }
    const note = document.getElementById('status_note');
    let payload = {};
    
    if (action === 'start') {
        payload = { command: 'M5001', value: 1 };
        note.innerText = "Sending TURN ON ALARM RESET command (M5001=1)...";
        debugLog('INFO', 'Send TURN ON ALARM RESET command -> M5001=1');
    }
    
    fetch('/api/plc/command/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') {
            note.innerText = "Y1 command (" + action + ") processed.";
            debugLog('OK', `${action} command successful`, data);
        } else {
            note.innerText = "❌ Lệnh Y1 failed: " + (data.message || '');
            debugLog('ERR', `Lệnh ${action} failed`, data);
        }
        setTimeout(readY1State, 300);
    })
    .catch(err => {
        note.innerText = "⚠ Error sending command " + action + ": " + err;
        debugLog('ERR', `Network error sending ${action}`, err);
    });
}

function pulseCommand(address, ms=500) {
    if(!isConnected) { 
        alert("Please connect to PLC before sending command!"); 
        return; 
    }
    const note = document.getElementById('status_note');
    note.innerText = `Sending Pulse command ${ms}ms -> ${address}...`;
    debugLog('INFO', `Pulse command ${ms}ms -> ${address}`);
    
    fetch('/api/plc/command/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({command: address, pulse: true, pulse_ms: ms})
    }).then(res => res.json()).then(data => {
        if (data.status === 'ok') note.innerText = `Pulse command ${address} successful.`;
    }).catch(err => {
        note.innerText = `⚠ Error sending command Pulse ${address}: ` + err;
        debugLog('ERR', `Network error sending Pulse ${address}`, err);
    });
}

function pulseLightOff(ms=500) {
    if(!isConnected) { 
        alert("Please connect to PLC before sending command!"); 
        return; 
    }
    const note = document.getElementById('status_note');
    note.innerText = "Pulsing Light OFF button (X152)...";
    debugLog('INFO', 'Pulse Light OFF button -> Write X151=0, Pulse X152');
    
    // First turn off X151
    fetch('/api/plc/command/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({command: 'X151', value: 0})
    }).then(() => {
        // Then pulse X152
        return fetch('/api/plc/command/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({command: 'X152', pulse: true, pulse_ms: ms})
        });
    }).then(res => res.json()).then(data => {
        if (data.status === 'ok') note.innerText = "Pulse Light OFF successful.";
    }).catch(err => {
        note.innerText = "⚠ Error sending command Pulse Light OFF: " + err;
        debugLog('ERR', 'Network error sending Pulse Light OFF', err);
    });
}

let momentaryBtnState = {};

function controlMomentary(address, state, event) {
    if (event && event.type.startsWith('touch')) {
        if (event.cancelable) event.preventDefault();
    }

    if(!isConnected) {
        if(state === 1) alert("Please connect to PLC before sending command!");
        return;
    }
    
    if (momentaryBtnState[address] === state) return;
    momentaryBtnState[address] = state;
    
    const note = document.getElementById('status_note');
    
    if (state === 1) {
        note.innerText = `Sending PRESS button command ( ${address} = 1 )...`;
        debugLog('INFO', `Press button ${address} -> 1`);
        fetch('/api/plc/command/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({command: address, value: 1})
        }).then(res => res.json()).then(data => {
            if (data.status === 'ok') note.innerText = `Press button ${address} successful.`;
        });
    } else {
        note.innerText = `Sending RELEASE button command ( ${address} = 0 )...`;
        debugLog('INFO', `Release button ${address} -> 0`);
        fetch('/api/plc/command/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({command: address, value: 0})
        }).then(res => res.json()).then(data => {
            if (data.status === 'ok') note.innerText = `Release button ${address} successful.`;
        });
    }
}

function controlLightOffMomentary(state, event) {
    if (event && event.type.startsWith('touch')) {
        if (event.cancelable) event.preventDefault();
    }

    if(!isConnected) {
        if(state === 1) alert("Please connect to PLC before sending command!");
        return;
    }
    
    if (momentaryBtnState['X152'] === state) return;
    momentaryBtnState['X152'] = state;

    const note = document.getElementById('status_note');

    if (state === 1) {
        note.innerText = "Sending PRESS button command Light OFF (X151=0, X152=1)...";
        debugLog('INFO', 'Press button Light OFF -> X151=0, X152=1');
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
            if (data.status === 'ok') note.innerText = "Press button Light OFF successful.";
        });
    } else {
        note.innerText = "Sending RELEASE button command Light OFF (X152=0)...";
        debugLog('INFO', 'Release button Light OFF -> X152=0');
        fetch('/api/plc/command/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({command: 'X152', value: 0})
        }).then(res => res.json()).then(data => {
            if (data.status === 'ok') note.innerText = "Release button Light OFF successful.";
        });
    }
}

function readY1State() {
    pollPlcStatus();
}

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

function toggleAutoMode() {
    if(!isConnected) {
        alert("Please connect to PLC before sending command!");
        return;
    }
    const note = document.getElementById('status_note');
    const newState = autoModeState === 1 ? 0 : 1;
    
    note.innerText = `Sending ${newState === 1 ? 'ON' : 'OFF'} Auto Mode command (M10)...`;
    debugLog('INFO', `Toggle Auto Mode (M10) -> ${newState}`);
    
    fetch('/api/plc/command/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({command: 'M10', value: newState})
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') {
            note.innerText = `Auto Mode command (M10=${newState}) successful.`;
            autoModeState = newState;
        } else {
            note.innerText = `❌ Auto Mode command failed: ${data.message || ''}`;
        }
    })
    .catch(err => {
        note.innerText = `⚠ Error sending command Auto Mode: ` + err;
        debugLog('ERR', `Network error sending M10`, err);
    });
}

function toggleEmptyMode() {
    if(!isConnected) {
        alert("Please connect to PLC before sending command!");
        return;
    }
    const note = document.getElementById('status_note');
    const newState = emptyModeState === 1 ? 0 : 1;
    
    note.innerText = `Sending ${newState === 1 ? 'ON' : 'OFF'} Empty Mode command (X304)...`;
    debugLog('INFO', `Toggle Empty Mode (X304) -> ${newState}`);
    
    fetch('/api/plc/command/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({command: 'X304', value: newState})
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') {
            note.innerText = `Empty Mode command (X304=${newState}) successful.`;
            emptyModeState = newState; // update state instantly
        } else {
            note.innerText = `❌ Empty Mode command failed: ${data.message || ''}`;
        }
    })
    .catch(err => {
        note.innerText = `⚠ Error sending command Empty Mode: ` + err;
        debugLog('ERR', `Network error sending X304`, err);
    });
}

