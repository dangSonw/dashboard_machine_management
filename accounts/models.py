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
    
    process_time_ms = models.FloatField(null=True, blank=True)
    caminput = models.IntegerField(null=True, blank=True)
    grayfilter = models.IntegerField(null=True, blank=True)
    shape01 = models.IntegerField(null=True, blank=True)
    pos01 = models.IntegerField(null=True, blank=True)
    label01 = models.IntegerField(null=True, blank=True)
    switch01 = models.IntegerField(null=True, blank=True)
    posy01 = models.IntegerField(null=True, blank=True)
    posy02 = models.IntegerField(null=True, blank=True)
    posx01 = models.IntegerField(null=True, blank=True)
    posx02 = models.IntegerField(null=True, blank=True)
    shape02 = models.IntegerField(null=True, blank=True)
    pos02 = models.IntegerField(null=True, blank=True)
    switch02 = models.IntegerField(null=True, blank=True)
    totalarea01 = models.IntegerField(null=True, blank=True)
    numoflabels01 = models.IntegerField(null=True, blank=True)
    resultdisplay = models.IntegerField(null=True, blank=True)
    
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Log ID: {self.id} - Result: {self.resultdisplay}"

class Machine_Logs_Images(models.Model):
    image_url = models.ImageField(upload_to='machine_logs_images')
    machine_log = models.ForeignKey(Machine_Logs, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.machine_log.code_product
