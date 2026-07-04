from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os

from accounts.models import Machine_Logs
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import TruncMinute, TruncHour, TruncDay, TruncMonth
from django.db.models import Count, Q

from . import plc_comm_api as plc_comm

@login_required(login_url="/authentication/login")
def home(request):
    # Lấy tổng số lượng bản ghi (đại diện cho tổng số lượng PLC đã chạy)
    total_plc = Machine_Logs.objects.count()
    
    # Điều kiện lỗi: 1 = NG, 0 = OK
    total_ng = Machine_Logs.objects.filter(Status='1').count()
    total_ok = Machine_Logs.objects.filter(Status='0').count()

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
    machine_name = "Machine Logs"
    if logs and logs[0].machine:
        machine_name = logs[0].machine.name
    
    context = {
        "logs": logs,
        "error_stats": error_stats,
        "total_logs": total_logs,
        "machine_name": machine_name
    }
    return render(request, "list_pcb.html", context)



def custom_404(request, exception):
    return render(request, 'page_404.html', status=404)



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




@login_required(login_url="/authentication/login")
def api_weekly_stats(request):
    now = timezone.now()
    start_time = now - timedelta(days=6)
    start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
    
    logs = Machine_Logs.objects.filter(created__gte=start_time)
    
    grouped_total = logs.annotate(day=TruncDay('created')).values('day').annotate(count=Count('id')).order_by('day')
    grouped_pass = logs.filter(Status='0').annotate(day=TruncDay('created')).values('day').annotate(count=Count('id')).order_by('day')
    grouped_fail = logs.filter(Status='1').annotate(day=TruncDay('created')).values('day').annotate(count=Count('id')).order_by('day')
    
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
    
    grouped_total = logs.annotate(month=TruncMonth('created')).values('month').annotate(count=Count('id')).order_by('month')
    grouped_pass = logs.filter(Status='0').annotate(month=TruncMonth('created')).values('month').annotate(count=Count('id')).order_by('month')
    grouped_fail = logs.filter(Status='1').annotate(month=TruncMonth('created')).values('month').annotate(count=Count('id')).order_by('month')
    
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


def blog(request):
    return render(request, "blog.html")


# ========== Real-time API endpoints ==========

@login_required(login_url="/authentication/login")
def api_home_stats(request):
    """API trả về tổng số liệu thống kê cho trang home (realtime)"""
    total_plc = Machine_Logs.objects.count()
    total_ng = Machine_Logs.objects.filter(Status='1').count()
    total_ok = Machine_Logs.objects.filter(Status='0').count()
    
    return JsonResponse({
        'total_plc': total_plc,
        'total_ok': total_ok,
        'total_ng': total_ng,
    })


@login_required(login_url="/authentication/login")
def api_pcb_data(request):
    """API trả về dữ liệu PCB cho trang list_pcb (realtime)"""
    page_number = request.GET.get('page', 1)
    logs_query = Machine_Logs.objects.all().order_by('-id')
    total_logs = logs_query.count()
    
    # Error stats
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
    
    # Paginated logs
    paginator = Paginator(logs_query, 20)
    try:
        page_obj = paginator.page(page_number)
    except:
        page_obj = paginator.page(1)
    
    logs_data = []
    for log in page_obj.object_list:
        logs_data.append({
            'id': log.id,
            'empty': log.empty or 0,
            'excess_solder': log.excess_solder or 0,
            'exposed_copper': log.exposed_copper or 0,
            'misaligned_header': log.misaligned_header or 0,
            'missing_component': log.missing_component or 0,
            'scratched': log.scratched or 0,
            'solder_bridge': log.solder_bridge or 0,
            'processing_time': log.processing_time or 0,
            'Status': log.Status or '0',
            'created': log.created.strftime('%Y-%m-%d %H:%M:%S') if log.created else '',
        })
    
    return JsonResponse({
        'error_stats': error_stats,
        'logs': logs_data,
        'total_logs': total_logs,
        'page': page_obj.number,
        'num_pages': paginator.num_pages,
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'start_index': page_obj.start_index(),
        'end_index': page_obj.end_index(),
    })