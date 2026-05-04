from django.contrib import admin
from django.urls import path, include, re_path
from django.shortcuts import render

from . import views

def page_not_found(request, *args, **kwargs):
    return render(request, 'page_404.html', status=404)

urlpatterns = [
    path('', views.home, name='home'),
    path('list-pcb/', views.list_pcb, name='list-pcb'),
    path('plc-control/', views.plc_control, name='plc-control'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('authentication/', include('authentication.urls')),
    
    # PLC API endpoints
    path('api/plc/connect/', views.api_connect_plc, name='api_connect_plc'),
    path('api/plc/status/', views.api_plc_status, name='api_plc_status'),
    path('api/plc/command/', views.api_plc_command, name='api_plc_command'),
    path('api/plc/write_params/', views.api_plc_write_params, name='api_plc_write_params'),
    path('api/plc/read_device/', views.api_plc_read_device, name='api_plc_read_device'),

    # Stats API endpoints
    path('api/stats/weekly/', views.api_weekly_stats, name='api_weekly_stats'),
    path('api/stats/monthly/', views.api_monthly_stats, name='api_monthly_stats'),
    
    re_path(r'^.*$', page_not_found, name='page_not_found'),
]

handler404 = 'machine_management.views.custom_404'
