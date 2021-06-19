from django.contrib import admin
from .models import Collection, Images, Results , Notification, CustomNotification, ProofImages, ImgConvert, ProofImgConvert
# Register your models here.
admin.site.register(Collection)
admin.site.register(Images)
admin.site.register(Results)
admin.site.register(Notification)  
admin.site.register(CustomNotification)  
admin.site.register(ProofImages)  
admin.site.register(ImgConvert)  
admin.site.register(ProofImgConvert)  