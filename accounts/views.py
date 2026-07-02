import os
import datetime
import mimetypes
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
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
    error_condition = Q(Status='1')
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
    # Prefer project-local log folder: <BASE_DIR>/data_log/LogImage
    base_dir = os.path.join(settings.BASE_DIR, 'data_log', 'LogImage')
    if os.path.exists(base_dir):
        return base_dir

    # Fallbacks (legacy paths)
    legacy_dir = r"D:\LogImage"
    if os.path.exists(legacy_dir):
        return legacy_dir

    return os.path.join(settings.BASE_DIR, 'machine_management', 'static', 'imgs_log')


def _list_image_files(root_dir: str, rel_dir: str):
    abs_dir = os.path.join(root_dir, rel_dir)
    results = []
    if not os.path.isdir(abs_dir):
        return results

    image_exts = ('.png', '.jpg', '.jpeg', '.jfz', '.bmp', '.webp')
    for root, dirs, files in os.walk(abs_dir):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for name in files:
            if name.startswith('.'):
                continue
            if not name.lower().endswith(image_exts):
                continue
            abs_path = os.path.join(root, name)
            try:
                stats = os.stat(abs_path)
                mod_time = datetime.datetime.fromtimestamp(stats.st_mtime)
                results.append(
                    {
                        'name': name,
                        'mod_time': mod_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'rel_path': os.path.relpath(abs_path, root_dir).replace('\\', '/'),
                    }
                )
            except Exception:
                pass

    results.sort(key=lambda x: x['mod_time'], reverse=True)
    return results

def logs_images(request):
    base_dir = get_base_log_dir()
    subpath = request.GET.get('path', '')
    current_path = os.path.abspath(os.path.join(base_dir, subpath))
    
    if not current_path.startswith(os.path.abspath(base_dir)):
        current_path = os.path.abspath(base_dir)
        subpath = ''
        
    parent_path = os.path.dirname(subpath.rstrip('\\/')) if subpath.strip('/\\') else ''
        
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
                    icon = "zmdi-image text-success" if item.lower().endswith(('.png', '.jpg', '.jpeg', '.jfz', '.bmp', '.webp')) else "zmdi-file text-primary"
                    
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
                    'is_image': (not is_dir) and item.lower().endswith(('.png', '.jpg', '.jpeg', '.jfz', '.bmp', '.webp')),
                    'rel_path': rel_path
                })
        except Exception:
            pass
            
    files_info.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))

    # Root split view: show recent images from OK/NG folders nicely
    normalized_subpath = subpath.strip('/\\')
    ok_images = []
    ng_images = []
    ok_total = 0
    ng_total = 0
    if normalized_subpath == '':
        ok_all = _list_image_files(base_dir, 'OK')
        ng_all = _list_image_files(base_dir, 'NG')
        ok_total = len(ok_all)
        ng_total = len(ng_all)
        ok_images = ok_all[:60]
        ng_images = ng_all[:60]

    context = {
        'files': files_info,
        'subpath': subpath,
        'parent_path': parent_path.replace('\\', '/'),
        'ok_images': ok_images,
        'ng_images': ng_images,
        'ok_total': ok_total,
        'ng_total': ng_total,
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
