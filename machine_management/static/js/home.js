document.addEventListener("DOMContentLoaded", function() {
    "use strict";



    // Real-time loop to poll PLC for Cycle time or other real-time stats
    setInterval(async function() {
        try {
            const res = await fetch('/api/plc/status/');
            const data = await res.json();
            if (data.status === 'ok') {
                const el = document.getElementById('stat_cycle_time');
                if (el) el.textContent = (data.d100 || 0) + ' ms';
            }
        } catch (err) {
            console.error("Error polling PLC status:", err);
        }
    }, 2000);
});