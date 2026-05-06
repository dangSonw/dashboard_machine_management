from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
import sys

from accounts.models import Machine_Logs
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import TruncMinute, TruncHour, TruncDay, TruncMonth
from django.db.models import Count, Q

# Add scada_fx5u_li to sys.path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scada_fx5u_li'))
import plc_comm_api as plc_comm

@login_required(login_url="/authentication/login")
def home(request):
    # Lấy tổng số lượng bản ghi (đại diện cho tổng số lượng PLC đã chạy)
    total_plc = Machine_Logs.objects.count()
    
    # Điều kiện lỗi
    error_condition = Q(Status='NG')
    
    total_ng = Machine_Logs.objects.filter(error_condition).count()
    total_ok = total_plc - total_ng

    context = {
        'total_plc': total_plc,
        'total_ok': total_ok,
        'total_ng': total_ng,
    }
    return render(request, "home.html", context)


from django.core.paginator import Paginator

@login_required(login_url="/authentication/login")
def list_pcb(request):
    logs_query = Machine_Logs.objects.all().order_by('-id')
    total_logs = logs_query.count()
    
    error_fields = [
        'empty', 'excess_solder', 'exposed_copper', 'misaligned_header',
        'missing_component', 'scratched', 'solder_bridge'
    ]
    
    error_stats = []
    if total_logs > 0:
        for field in error_fields:
            error_count = logs_query.filter(**{field + '__gt': 0}).count()
            percentage = round((error_count / total_logs) * 100, 2)
            error_stats.append({
                'label': field.replace('_', ' ').title(),
                'count': error_count,
                'percentage': percentage
            })
    else:
        for field in error_fields:
            error_stats.append({
                'label': field.replace('_', ' ').title(),
                'count': 0,
                'percentage': 0
            })

    # Pagination logic
    paginator = Paginator(logs_query, 20)  # Show 20 logs per page
    page_number = request.GET.get('page')
    logs = paginator.get_page(page_number)
    
    # Calculate machine_name for breadcrumbs
    machine_name = logs[0].machine.name if logs and logs[0].machine else "Machine Logs"
    
    context = {
        "logs": logs,
        "error_stats": error_stats,
        "total_logs": total_logs,
        "machine_name": machine_name
    }
    return render(request, "list_pcb.html", context)

@login_required(login_url="/authentication/login")
def plc_control(request):
    return render(request, "control_plc.html")

def custom_404(request, exception):
    return render(request, 'page_404.html', status=404)

@csrf_exempt
def api_connect_plc(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ip = data.get('ip') or os.getenv('HOST_PLC')
            port_str = data.get('port') or os.getenv('PORT_TCP')
            
            if not ip or not port_str:
                return JsonResponse({'status': 'error', 'message': 'PLC Connection configuration (IP/Port) is missing in .env'})
                
            port = int(port_str)
            action = data.get('action', 'connect')
            
            if action == 'connect':
                success = plc_comm.connect_plc(ip, port)
                if success:
                    return JsonResponse({'status': 'ok', 'connected': True})
                else:
                    return JsonResponse({'status': 'failed', 'connected': False, 'message': 'Cannot connect (Timeout or invalid IP/Port)'})
            elif action == 'disconnect':
                plc_comm.connected = False
                return JsonResponse({'status': 'ok', 'connected': False})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'ok', 'connected': plc_comm.connected})

@csrf_exempt
def api_plc_status(request):
    if not plc_comm.connected:
        return JsonResponse({'status': 'failed', 'message': 'Not connected'})
    
    try:
        data = plc_comm.read_words()
        if not data:
            data = {}
            
        d100 = plc_comm.read_device('D100')
        m10 = plc_comm.read_device('M10')
        m20 = plc_comm.read_device('M20')
        x304 = plc_comm.read_device('X304')
        m80 = plc_comm.read_device('M80')
        m100 = plc_comm.read_device('M100')
        m5000 = plc_comm.read_device('M5000')
        x10 = plc_comm.read_device('X10')
        x124 = plc_comm.read_device('X124')
        x125 = plc_comm.read_device('X125')
        x100 = plc_comm.read_device('X100')
        x112 = plc_comm.read_device('X112')
        x110 = plc_comm.read_device('X110')
        x117 = plc_comm.read_device('X117')
        x151 = plc_comm.read_device('X151')
        x152 = plc_comm.read_device('X152')
        y1 = plc_comm.read_device('Y1')
        
        d_params = plc_comm.read_device('D300', 20)
        d_params2 = plc_comm.read_device('D500', 3)
        
        status = {
            'status': 'ok',
            'data': data,
            'd100': d100[0] if d100 else 0,
            'm10': m10[0] if m10 else 0,
            'm20': m20[0] if m20 else 0,
            'x304': x304[0] if x304 else 0,
            'm80': m80[0] if m80 else 0,
            'm100': m100[0] if m100 else 0,
            'm5000': m5000[0] if m5000 else 0,
            'x10': x10[0] if x10 else 0,
            'x124': x124[0] if x124 else 0,
            'x125': x125[0] if x125 else 0,
            'x100': x100[0] if x100 else 0,
            'x112': x112[0] if x112 else 0,
            'x110': x110[0] if x110 else 0,
            'x117': x117[0] if x117 else 0,
            'x151': x151[0] if x151 else 0,
            'x152': x152[0] if x152 else 0,
            'y1': y1[0] if y1 else 0,
            'params': {
                'D300': d_params[0] if d_params else 0,
                'D302': d_params[2] if d_params else 0,
                'D304': d_params[4] if d_params else 0,
                'D306': d_params[6] if d_params else 0,
                'D500': d_params2[0] if d_params2 else 0,
                'D502': d_params2[2] if d_params2 else 0,
            }
        }
        return JsonResponse(status)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@csrf_exempt
def api_plc_command(request):
    if not plc_comm.connected:
        return JsonResponse({'status': 'failed', 'message': 'Not connected'})
    
    if request.method == 'POST':
        try:
            import time as _time
            data = json.loads(request.body)
            command = data.get('command')
            value = int(data.get('value', 1))
            readback = data.get('readback', False)
            if not command:
                return JsonResponse({'status': 'error', 'message': 'No command'})
            
            is_pulse = data.get('pulse', False)
            pulse_ms = int(data.get('pulse_ms', 200))

            if is_pulse:
                success, msg = plc_comm.pulse_device(command, pulse_ms)
            else:
                success, msg = plc_comm.write_device(command, [value])
            
            if not success:
                return JsonResponse({
                    'status': 'failed',
                    'command': command,
                    'write_value': value,
                    'message': msg if 'msg' in locals() else 'Write failed'
                })
            
            result = {
                'status': 'ok',
                'command': command,
                'write_value': value,
                'write_success': success,
            }
            
            # Đọc lại để xác nhận (read-back verification)
            if readback:
                _time.sleep(0.05)  # 50ms delay trước khi đọc lại
                try:
                    rb = plc_comm.read_device(command)
                    actual_value = rb[0] if rb else None
                    result['readback_value'] = actual_value
                    result['readback_match'] = (actual_value == value)
                    if actual_value != value:
                        result['readback_warning'] = (
                            f'Wrote {value} but read back {actual_value} — '
                            f'PLC might not have received the command or X address cannot be forced'
                        )
                except Exception as rb_err:
                    result['readback_error'] = str(rb_err)
            
            return JsonResponse(result)
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
            
    return JsonResponse({'status': 'failed'})

@csrf_exempt
def api_plc_read_device(request):
    if not plc_comm.connected:
        return JsonResponse({'status': 'failed', 'message': 'Not connected'})
    
    address = request.GET.get('address', '')
    if not address:
        return JsonResponse({'status': 'error', 'message': 'No address'})
    
    try:
        result = plc_comm.read_device(address)
        value = result[0] if result else 0
        return JsonResponse({'status': 'ok', 'address': address, 'value': value})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@csrf_exempt
def api_plc_write_params(request):
    if not plc_comm.connected:
        return JsonResponse({'status': 'failed', 'message': 'Not connected'})
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            failed_keys = []
            for key, val in data.items():
                if key.startswith('D'):
                    if val == "" or val is None:
                        val = 0
                    success, msg = plc_comm.write_device(key, [int(val)])
                    if not success:
                        failed_keys.append(f"{key}: {msg}")
            
            if failed_keys:
                return JsonResponse({'status': 'error', 'message': "Error writing parameters: " + ", ".join(failed_keys)})
                
            return JsonResponse({'status': 'ok', 'message': 'Parameters updated successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
            
    return JsonResponse({'status': 'failed'})


@login_required(login_url="/authentication/login")
def api_weekly_stats(request):
    now = timezone.now()
    start_time = now - timedelta(days=6)
    start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
    
    logs = Machine_Logs.objects.filter(created__gte=start_time)
    
    error_condition = Q(Status='NG')
    
    grouped_total = logs.annotate(day=TruncDay('created')).values('day').annotate(count=Count('id')).order_by('day')
    grouped_pass = logs.exclude(error_condition).annotate(day=TruncDay('created')).values('day').annotate(count=Count('id')).order_by('day')
    grouped_fail = logs.filter(error_condition).annotate(day=TruncDay('created')).values('day').annotate(count=Count('id')).order_by('day')
    
    total_map = {item['day'].strftime('%d-%m'): item['count'] for item in grouped_total}
    pass_map = {item['day'].strftime('%d-%m'): item['count'] for item in grouped_pass}
    fail_map = {item['day'].strftime('%d-%m'): item['count'] for item in grouped_fail}
    
    labels = []
    data_total = []
    data_pass = []
    data_fail = []
    
    for i in range(6, -1, -1):
        d = now - timedelta(days=i)
        d_str = d.strftime('%d-%m')
        labels.append(d_str)
        data_total.append(total_map.get(d_str, 0))
        data_pass.append(pass_map.get(d_str, 0))
        data_fail.append(fail_map.get(d_str, 0))
        
    return JsonResponse({
        'labels': labels,
        'data_total': data_total,
        'data_pass': data_pass,
        'data_fail': data_fail
    })


@login_required(login_url="/authentication/login")
def api_monthly_stats(request):
    now = timezone.now()
    
    # Get to 12 months ago (start of that month)
    start_date = now
    for _ in range(11):
        start_date = (start_date.replace(day=1) - timedelta(days=1))
    start_date = start_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    logs = Machine_Logs.objects.filter(created__gte=start_date)
    
    error_condition = Q(Status='NG')

    grouped_total = logs.annotate(month=TruncMonth('created')).values('month').annotate(count=Count('id')).order_by('month')
    grouped_pass = logs.exclude(error_condition).annotate(month=TruncMonth('created')).values('month').annotate(count=Count('id')).order_by('month')
    grouped_fail = logs.filter(error_condition).annotate(month=TruncMonth('created')).values('month').annotate(count=Count('id')).order_by('month')
    
    total_map = {item['month'].strftime('%m-%Y'): item['count'] for item in grouped_total if item['month']}
    pass_map = {item['month'].strftime('%m-%Y'): item['count'] for item in grouped_pass if item['month']}
    fail_map = {item['month'].strftime('%m-%Y'): item['count'] for item in grouped_fail if item['month']}
    
    labels = []
    data_total = []
    data_pass = []
    data_fail = []
    
    for i in range(11, -1, -1):
        m = now.month - i
        y = now.year
        if m <= 0:
            m += 12
            y -= 1
            
        m_str = f"{m:02d}-{y}"
        labels.append(m_str)
        data_total.append(total_map.get(m_str, 0))
        data_pass.append(pass_map.get(m_str, 0))
        data_fail.append(fail_map.get(m_str, 0))
        
    return JsonResponse({
        'labels': labels,
        'data_total': data_total,
        'data_pass': data_pass,
        'data_fail': data_fail
    })
