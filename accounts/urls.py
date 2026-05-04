<<<<<<< HEAD
from django.urls import path
from . import views

urlpatterns = [
    path('user-list/', views.user_list, name='user_list'),
    path('list-pcb/', views.list_pcb, name='list_pcb'),
    path('logs-images/', views.logs_images, name='logs_images'),
    path('serve-log-image/', views.serve_log_image, name='serve_log_image'),
]
=======
from django.urls import path
from . import views

urlpatterns = [
    path('user-list/', views.user_list, name='user_list'),
    path('list-pcb/', views.list_pcb, name='list_pcb'),
    path('logs-images/', views.logs_images, name='logs_images'),
    path('serve-log-image/', views.serve_log_image, name='serve_log_image'),
]
>>>>>>> master
