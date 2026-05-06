import os
import datetime
import mimetypes
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q
from django.conf import settings
from django.http import FileResponse, HttpResponseNotFound
from .models import *


def user_list(request):
    users = User.objects.all()
    context = {'users': users}
    return render(request, 'user_list.html', context)

ERROR_FIELDS = {
    'empty': 'Empty',
    'excess_solder': 'Excess Solder',
    'exposed_copper': 'Exposed Copper',
    'misaligned_header': 'Misaligned Header',
    'missing_component': 'Missing Component',
    'scratched': 'Scratched',
    'solder_bridge': 'Solder Bridge'
}

def list_pcb(request):
    # Lấy toàn bộ logs, sắp xếp theo thời gian mới nhất (lấy tối đa 400 dòng)
    logs = Machine_Logs.objects.all().order_by('-created')
    
    total_logs = Machine_Logs.objects.count()
    error_condition = Q(status='NG')
    total_errors = Machine_Logs.objects.filter(error_condition).count()
    error_percentage = round((total_errors / total_logs * 100), 2) if total_logs > 0 else 0
    
    agg_args = {f"{f}_err": Count('id', filter=Q(**{f"{f}__gt": 0})) for f in ERROR_FIELDS}
    error_counts_dict = Machine_Logs.objects.aggregate(**agg_args)
    
    error_stats = [
        {
            'label': label,
            'count': count,
            'percentage': round((count / total_logs * 100), 2) if total_logs > 0 else 0
        }
        for field, label in ERROR_FIELDS.items()
        if (count := error_counts_dict[f"{field}_err"]) > 0
    ]
    
    # Sort stats descending
    error_stats.sort(key=lambda x: x['count'], reverse=True)
    
    context = {
        'logs': logs,
        'error_stats': error_stats,
        'total_logs': total_logs,
        'total_errors': total_errors,
        'error_percentage': error_percentage,
        'machine_name': 'All Time Logs',
    }
    return render(request, 'list_pcb.html', context)

def get_base_log_dir():
    base_dir = r"D:\LogImage"
    if not os.path.exists(base_dir):
        base_dir = os.path.join(settings.BASE_DIR, 'machine_management', 'static', 'imgs_log')
    return base_dir

def logs_images(request):
    base_dir = get_base_log_dir()
    subpath = request.GET.get('path', '')
    current_path = os.path.abspath(os.path.join(base_dir, subpath))
    
    if not current_path.startswith(os.path.abspath(base_dir)):
        current_path = os.path.abspath(base_dir)
        subpath = ''
        
    parent_path = ''
    if subpath and subpath not in ['\\', '/']:
        parent_path = os.path.dirname(subpath.rstrip('\\/'))
        
    files_info = []
    if os.path.exists(current_path) and os.path.isdir(current_path):
        try:
            for item in os.listdir(current_path):
                if item.startswith('.'): continue
                
                item_path = os.path.join(current_path, item)
                is_dir = os.path.isdir(item_path)
                stats = os.stat(item_path)
                mod_time = datetime.datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                
                size = stats.st_size
                if is_dir:
                    size_str = ""
                    item_type = "File folder"
                    icon = "zmdi-folder text-warning"
                else:
                    ext = os.path.splitext(item)[1].upper()
                    item_type = f"{ext.replace('.', '')} File" if ext else "File"
                    icon = "zmdi-image text-success" if item.lower().endswith(('.png', '.jpg', '.jpeg', '.jfz', '.bmp')) else "zmdi-file text-primary"
                    
                    if size < 1024:
                        size_str = f"{size} B"
                    elif size < 1024 * 1024:
                        size_str = f"{size/1024:.0f} KB"
                    else:
                        size_str = f"{size/(1024*1024):.1f} MB"
                        
                rel_path = os.path.relpath(item_path, base_dir).replace('\\', '/')
                
                files_info.append({
                    'name': item,
                    'is_dir': is_dir,
                    'mod_time': mod_time,
                    'type': item_type,
                    'size': size_str,
                    'icon': icon,
                    'rel_path': rel_path
                })
        except Exception:
            pass
            
    files_info.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))

    context = {
        'files': files_info,
        'subpath': subpath,
        'parent_path': parent_path.replace('\\', '/')
    }
    return render(request, 'logs_images.html', context)

def serve_log_image(request):
    base_dir = get_base_log_dir()
    subpath = request.GET.get('path', '')
    
    if not subpath:
        return HttpResponseNotFound("File not found.")
        
    filepath = os.path.abspath(os.path.join(base_dir, subpath))
    
    if not filepath.startswith(os.path.abspath(base_dir)) or not os.path.exists(filepath) or not os.path.isfile(filepath):
        return HttpResponseNotFound("File not found or access denied.")
        
    content_type, _ = mimetypes.guess_type(filepath)
    if not content_type:
        content_type = 'image/jpeg' if filepath.lower().endswith('.jfz') else 'application/octet-stream'
        
    return FileResponse(open(filepath, 'rb'), content_type=content_type)