from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profileimg = models.ImageField(
        upload_to='profile_images',
        default='blank-profile-picture.png'
    )
    location = models.CharField(max_length=100, blank=True)
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.user.username

class Machine(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name



class Machine_Logs(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, null=True, blank=True)
    processing_time = models.FloatField(null=True, blank=True, help_text="Thời gian xử lý")
    
    empty = models.IntegerField(null=True, blank=True, help_text="Lỗi trống (empty)")
    empty_Conf = models.FloatField(null=True, blank=True)
    
    excess_solder = models.IntegerField(null=True, blank=True, help_text="Lỗi hàn dư")
    excess_solder_Conf = models.FloatField(null=True, blank=True)
    
    exposed_copper = models.IntegerField(null=True, blank=True, help_text="Lỗi hở đồng")
    exposed_copper_Conf = models.FloatField(null=True, blank=True)
    
    misaligned_header = models.IntegerField(null=True, blank=True, help_text="Lỗi lệch header")
    misaligned_header_Conf = models.FloatField(null=True, blank=True)
    
    missing_component = models.IntegerField(null=True, blank=True, help_text="Số lượng linh kiện bị thiếu")
    missing_component_Conf = models.FloatField(null=True, blank=True, help_text="Độ tin cậy khi phát hiện linh kiện bị thiếu")
    
    scratched = models.IntegerField(null=True, blank=True, help_text="Lỗi trầy xước")
    scratched_Conf = models.FloatField(null=True, blank=True)
    
    solder_bridge = models.IntegerField(null=True, blank=True, help_text="Lỗi cầu hàn")
    solder_bridge_Conf = models.FloatField(null=True, blank=True)
    
    Status = models.CharField(max_length=100, null=True, blank=True)
    
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Log ID: {self.id} - Status: {self.Status}"

class Machine_Logs_Images(models.Model):
    image_url = models.ImageField(upload_to='machine_logs_images')
    machine_log = models.ForeignKey(Machine_Logs, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Image for Log {self.machine_log.id}"
