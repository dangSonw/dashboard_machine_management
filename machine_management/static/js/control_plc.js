let isConnected = false;
let pollInterval = null;
let isEditingParams = false;
let editTimeout;

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
            alert("Lỗi kết nối: " + data.message);
        }
    })
    .catch(err => alert("Lỗi hệ thống: " + err));
}

function updateConnectUI() {
    const dot = document.getElementById('plc_connection_dot');
    const note = document.getElementById('status_note');
    const connectBtn = document.querySelector('[onclick="toggleConnect()"]');
    if (isConnected) {
        dot.className = "badge badge-success";
        dot.innerText = "Đã kết nối PLC";
        note.innerText = "Sẵn sàng hoạt động...";
        if (connectBtn) {
            connectBtn.className = "btn btn-outline-danger btn-sm";
            connectBtn.innerText = "NGẮT KẾT NỐI";
        }
    } else {
        dot.className = "badge badge-danger";
        dot.innerText = "Chưa kết nối PLC";
        note.innerText = "Hệ thống đang chờ kết nối...";
        if (connectBtn) {
            connectBtn.className = "btn btn-outline-info btn-sm";
            connectBtn.innerText = "KẾT NỐI PLC";
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
            

            
            if (data.m100 !== undefined) {
                $('#val_M100').text(data.m100 ? 'ON' : 'OFF');
                $('#val_M100').removeClass().addClass(data.m100 ? 'badge badge-success' : 'badge badge-secondary').css('font-size', '0.9em');
            }
            if (data.x15 !== undefined) {
                $('#val_X15').text(data.x15 ? 'ON' : 'OFF');
                $('#val_X15').removeClass().addClass(data.x15 ? 'badge badge-success' : 'badge badge-secondary').css('font-size', '0.9em');
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
        console.warn('[PLC Poll] Lỗi kết nối:', err);
    });
}

function sendPlcCommand(address) {
    if(!isConnected) {
        alert("Vui lòng kết nối PLC trước khi gửi lệnh!");
        return;
    }
    const note = document.getElementById('status_note');
    note.innerText = "Đang gửi lệnh tới: " + address + " ...";
    
    fetch('/api/plc/command/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({command: address, value: 1})
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') {
            note.innerText = "Lệnh " + address + " đã thực thi thành công.";
        } else {
            note.innerText = "Lệnh " + address + " thất bại (" + (data.message || 'không rõ lý do') + ")";
        }
    })
    .catch(err => {
        console.warn('[PLC Command] Lỗi:', err);
        note.innerText = "⚠ Lỗi gửi lệnh " + address + ": " + err;
    });
}

function saveParameters() {
    if(!isConnected) {
        alert("Vui lòng kết nối PLC trước khi cập nhật tham số!");
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
    
    document.getElementById('status_note').innerText = "Đang cập nhật tham số...";
    
    fetch('/api/plc/write_params/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(resData => {
        if (resData.status === 'ok') {
            document.getElementById('status_note').innerText = "Đã cập nhật tham số cài đặt thành công.";
            isEditingParams = false; // allow pulling fresh data
        } else {
            document.getElementById('status_note').innerText = "⚠ Lỗi cập nhật: " + (resData.message || 'Thất bại');
        }
    })
    .catch(err => {
        console.warn('[PLC Params] Lỗi:', err);
        document.getElementById('status_note').innerText = "⚠ Lỗi kết nối khi lưu tham số: " + err;
    });
}



const x200State = { isPowering: false };

function onPowerSystem() {
    console.log("onPowerSystem() was called");
    if (!isConnected) {
        alert("Vui lòng kết nối PLC trước khi bật hệ thống!");
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
        btn.innerHTML = '<i class="zmdi zmdi-rotate-right zmdi-hc-spin"></i>&nbsp; ĐANG BẬT HỆ THỐNG...';
    }
    if (led) led.className = 'rounded-circle bg-warning mr-2 shadow-sm';
    if (statusTxt) {
        statusTxt.innerText = 'Đang gửi X200...';
        statusTxt.className = 'font-weight-bold text-warning';
    }
    if (note) note.innerText = 'Đang gửi lệnh ON POWER (X200) tới PLC...';

    debugLog('INFO', 'Bắt đầu lệnh ON POWER → gửi X200 (pulse)');

    fetch('/api/plc/command/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({command: 'X200', pulse: true, pulse_ms: 1500})
    })
    .then(res => res.json())
    .then(data => {
        x200State.isPowering = false;

        if (data.status === 'ok') {
            debugLog('OK', '✅ Lệnh X200 (ON POWER) đã được PLC nhận thành công', data);
            if (led) led.className = 'rounded-circle bg-success mr-2 shadow-sm';
            if (statusTxt) {
                statusTxt.innerText = '✅ HỆ THỐNG ON';
                statusTxt.className = 'font-weight-bold text-success';
            }
            if (note) note.innerText = '✅ X200 ON — Toàn bộ hệ thống đã được bật!';
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = '<i class="zmdi zmdi-check"></i>&nbsp; HỆ THỐNG ĐÃ BẬT (X200)';
                btn.className = 'btn btn-success btn-lg btn-block waves-effect mt-2 shadow';
            }
            setTimeout(() => {
                if (led) led.className = 'rounded-circle bg-info mr-2 shadow-sm';
                if (statusTxt) {
                    statusTxt.innerText = 'HỆ THỐNG SẴN SÀNG';
                    statusTxt.className = 'font-weight-bold text-info';
                }
                if (btn) {
                    btn.innerHTML = '<i class="zmdi zmdi-power"></i>&nbsp; BẬT HỆ THỐNG (X200)';
                    btn.className = 'btn btn-success btn-lg btn-block waves-effect mt-2 shadow';
                }
            }, 6000);

        } else {
            // Thất bại
            const errMsg = `❌ X200 thất bại: ${data.message || 'Không rõ lý do'}`;
            debugLog('ERR', errMsg, data);
            if (led) led.className = 'rounded-circle bg-danger mr-2 shadow-sm';
            if (statusTxt) {
                statusTxt.innerText = '❌ LỖI GỬI X200';
                statusTxt.className = 'font-weight-bold text-danger';
            }
            if (note) note.innerText = errMsg;
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = '<i class="zmdi zmdi-power"></i>&nbsp; BẬT HỆ THỐNG (X200)';
                btn.className = 'btn btn-success btn-lg btn-block waves-effect mt-2 shadow';
            }
        }
    })
    .catch(err => {
        x200State.isPowering = false;
        const errMsg = `❌ Lỗi mạng khi gửi X200: ${err}`;
        debugLog('ERR', errMsg, { error: String(err) });
        if (led) led.className = 'rounded-circle bg-danger mr-2 shadow-sm';
        if (statusTxt) {
            statusTxt.innerText = '❌ LỖI MẠNG';
            statusTxt.className = 'font-weight-bold text-danger';
        }
        if (note) note.innerText = errMsg;
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<i class="zmdi zmdi-power"></i>&nbsp; BẬT HỆ THỐNG (X200)';
            btn.className = 'btn btn-success btn-lg btn-block waves-effect mt-2 shadow';
        }
    });
}

function controlY1(action) {
    if(!isConnected) {
        alert("Vui lòng kết nối PLC trước khi gửi lệnh!");
        return;
    }
    const note = document.getElementById('status_note');
    let payload = {};
    
    if (action === 'start') {
        payload = { command: 'M5001', value: 1 };
        note.innerText = "Đang gửi lệnh BẬT RESET ALARM (M5001=1)...";
        debugLog('INFO', 'Gửi lệnh BẬT RESET ALARM -> M5001=1');
    }
    
    fetch('/api/plc/command/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') {
            note.innerText = "Lệnh Y1 (" + action + ") xử lý xong.";
            debugLog('OK', `Lệnh ${action} thành công`, data);
        } else {
            note.innerText = "❌ Lệnh Y1 thất bại: " + (data.message || '');
            debugLog('ERR', `Lệnh ${action} thất bại`, data);
        }
        setTimeout(readY1State, 300);
    })
    .catch(err => {
        note.innerText = "⚠ Lỗi gửi lệnh " + action + ": " + err;
        debugLog('ERR', `Lỗi network khi gửi ${action}`, err);
    });
}

function pulseCommand(address, ms=500) {
    if(!isConnected) { 
        alert("Vui lòng kết nối PLC trước khi gửi lệnh!"); 
        return; 
    }
    const note = document.getElementById('status_note');
    note.innerText = `Đang gửi lệnh Pulse ${ms}ms -> ${address}...`;
    debugLog('INFO', `Lệnh Pulse ${ms}ms -> ${address}`);
    
    fetch('/api/plc/command/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({command: address, pulse: true, pulse_ms: ms})
    }).then(res => res.json()).then(data => {
        if (data.status === 'ok') note.innerText = `Lệnh Pulse ${address} thành công.`;
    }).catch(err => {
        note.innerText = `⚠ Lỗi gửi lệnh Pulse ${address}: ` + err;
        debugLog('ERR', `Lỗi network khi gửi Pulse ${address}`, err);
    });
}

function pulseLightOff(ms=500) {
    if(!isConnected) { 
        alert("Vui lòng kết nối PLC trước khi gửi lệnh!"); 
        return; 
    }
    const note = document.getElementById('status_note');
    note.innerText = "Đang Pulse nút Light OFF (X152)...";
    debugLog('INFO', 'Pulse nút Light OFF -> Ghi X151=0, Pulse X152');
    
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
        if (data.status === 'ok') note.innerText = "Pulse Light OFF thành công.";
    }).catch(err => {
        note.innerText = "⚠ Lỗi gửi lệnh Pulse Light OFF: " + err;
        debugLog('ERR', 'Lỗi network khi gửi Pulse Light OFF', err);
    });
}

let momentaryBtnState = {};

function controlMomentary(address, state, event) {
    if (event && event.type.startsWith('touch')) {
        if (event.cancelable) event.preventDefault();
    }

    if(!isConnected) {
        if(state === 1) alert("Vui lòng kết nối PLC trước khi gửi lệnh!");
        return;
    }
    
    if (momentaryBtnState[address] === state) return;
    momentaryBtnState[address] = state;
    
    const note = document.getElementById('status_note');
    
    if (state === 1) {
        note.innerText = `Đang gửi lệnh NHẤN nút ( ${address} = 1 )...`;
        debugLog('INFO', `Nhấn nút ${address} -> 1`);
        fetch('/api/plc/command/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({command: address, value: 1})
        }).then(res => res.json()).then(data => {
            if (data.status === 'ok') note.innerText = `Nhấn nút ${address} thành công.`;
        });
    } else {
        note.innerText = `Đang gửi lệnh NHẢ nút ( ${address} = 0 )...`;
        debugLog('INFO', `Nhả nút ${address} -> 0`);
        fetch('/api/plc/command/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({command: address, value: 0})
        }).then(res => res.json()).then(data => {
            if (data.status === 'ok') note.innerText = `Nhả nút ${address} thành công.`;
        });
    }
}

function controlLightOffMomentary(state, event) {
    if (event && event.type.startsWith('touch')) {
        if (event.cancelable) event.preventDefault();
    }

    if(!isConnected) {
        if(state === 1) alert("Vui lòng kết nối PLC trước khi gửi lệnh!");
        return;
    }
    
    if (momentaryBtnState['X152'] === state) return;
    momentaryBtnState['X152'] = state;

    const note = document.getElementById('status_note');

    if (state === 1) {
        note.innerText = "Đang gửi lệnh NHẤN nút Light OFF (X151=0, X152=1)...";
        debugLog('INFO', 'Nhấn nút Light OFF -> X151=0, X152=1');
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
            if (data.status === 'ok') note.innerText = "Nhấn nút Light OFF thành công.";
        });
    } else {
        note.innerText = "Đang gửi lệnh NHẢ nút Light OFF (X152=0)...";
        debugLog('INFO', 'Nhả nút Light OFF -> X152=0');
        fetch('/api/plc/command/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({command: 'X152', value: 0})
        }).then(res => res.json()).then(data => {
            if (data.status === 'ok') note.innerText = "Nhả nút Light OFF thành công.";
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
