from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models.signals import post_save

from django.core.files.base import  File
from django.core.files.temp import NamedTemporaryFile
import base64

# Create your models here.
JOB_STATUS = (
    ('Pending', 'P'),
    ('In progress', 'I'),
    ('Finished', 'F')
)


class Images(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    #image= models.ImageField(upload_to="orderimage", blank=True)
    imageby = models.TextField(default= "", null=True, blank=True)
    name = models.TextField(default= "", null=True, blank=True, max_length=120)
    collection_name = models.ForeignKey("Collection", on_delete=models.CASCADE, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    typed = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
        return f'Image Obj: user =  {self.user}, collection name= {self.collection_name.collname}, :id: {self.id}'
  

class ImgConvert(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    #image= models.ImageField(upload_to="orderimage", blank=True)
    imageby = models.FileField(blank= True, null=True, upload_to="convertimages")
    name = models.TextField(default= "", null=True, blank=True, max_length=120) 
    collection_name = models.ForeignKey("Collection", on_delete=models.CASCADE, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    typed = models.BooleanField(default=False, null=True, blank=True)
    code = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f'ImgConvert Obj: user =  {self.user}, collection name= {self.collection_name.collname}, :id: {self.id}'

class ProofImages(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    imageby =  models.TextField(default= "", null=True, blank=True)
    name = models.TextField(default= "", null=True, blank=True, max_length=120)
    collection_name = models.ForeignKey("Collection", on_delete=models.CASCADE, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Image Proof Obj: user =  {self.user}, collection name= {self.collection_name.collname}, :id: {self.id}'

class ProofImgConvert(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    #image= models.ImageField(upload_to="orderimage", blank=True)
    imageby = models.FileField(blank= True, null=True, upload_to="convertproofimages")
    name = models.TextField(default= "", null=True, blank=True, max_length=120) 
    collection_name = models.ForeignKey("Collection", on_delete=models.CASCADE, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
        return f'ProofImgConvert Obj: user =  {self.user}, collection name= {self.collection_name.collname}, :id: {self.id}'

class Results(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    #c_file = models.FileField(upload_to="completed_files", blank=True)
    c_file = models.TextField(default= "", null=True, blank=True)
    ext = models.TextField(default= "", null=True, blank=True, max_length=120)
    name = models.TextField(default= "", null=True, blank=True, max_length=120)
    collection_name = models.ForeignKey("Collection", on_delete=models.CASCADE, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    finished = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
        return f'Result obj: user =  {self.user}, collection name= {self.collection_name.collname}, :id: {self.id}'

 
class Collection(models.Model):
    collname= models.CharField(max_length=20, default="", null = True)
    created_date = models.DateTimeField(default=timezone.now)
    client = models.ForeignKey(settings.AUTH_USER_MODEL,
                           on_delete=models.CASCADE, blank=True, null=True)
    phonenumber = models.IntegerField(null=True, blank=True)
    colldone = models.BooleanField(default=False, null=True, blank=True)
    collection_images = models.ForeignKey(Images, on_delete=models.SET_NULL, blank=True, null=True, related_name="this_images")
    completed_files = models.ForeignKey(Results, on_delete=models.SET_NULL, blank=True, null=True)
    job_status = models.CharField(choices=JOB_STATUS, max_length=11, default="Pending", null=True, blank=True)

    estimated_amount = models.FloatField(null=True, default=0, blank=True)
    
    deposited_amount =  models.FloatField(null=True, default=0, blank=True)
    paid_option =  models.BooleanField(null=True, default=False, blank=True)
    collection_proof = models.ForeignKey(Images, on_delete=models.SET_NULL, blank=True, null=True)

   
    def __str__(self):
        return f'Collection obj: name:{self.collname}, user = {self.client.username},  done : {self.colldone}, :id: {self.id}'

    def completed(self):
        try:
            qs= Results.objects.all().filter(user = self.client, collection_name = self.id)
            files = [{"id":x.id, "file": x.c_file, "name":x.name, "ext":x.ext} for x in qs]
        except Exception as e:
            qs  = None
            files = None
        return files

            
    def proof_imgs(self):
        me = Collection.objects.get(id=self.id)
        dellthis=  ProofImgConvert.objects.all().filter(user = self.client, collection_name = me)
        for b in dellthis:
            b.delete()
          

        fast =  ProofImages.objects.all().filter(user = self.client, collection_name = me).order_by("id")

        for a in fast:
            try:
                tmp = ProofImgConvert.objects.get(user= self.client, collection_name=  me, name=a.name)
            except Exception as e:

                
                fileTemp = NamedTemporaryFile()
                fileTemp.write(base64.b64decode(a.imageby.encode("utf-8")))
                filename = a.name
                file1 = File(fileTemp, name=filename)
                tmp = ProofImgConvert.objects.create(user= self.client, collection_name= me, imageby =file1, name=a.name)
            

        try:
            second_fast =ProofImgConvert.objects.all().filter(user = self.client, collection_name = me).order_by("id")
    
        except:
  
            second_fast =None
        return second_fast
        # try:
        #     print( 'iiiiiiiiiiiresssssssssultsprrrrrrrrrrrrrorof')
        #     qs= ProofImages.objects.all().filter(user = self.client, collection_name = self.id)
        #     imgs = [{"id":x.id, "imageby": x.imageby, "timestamp": x.timestamp, "name":x.name} for x in qs]
        # except Exception as e:
        #     qs  = None
        #     imgs = None
        #     print(e, 'resssssssssultsprrrrrrrrrrrrrorof')
        # print(imgs, 'gggggggggggggggghjjkl')   
        # return imgs




class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    message = models.CharField(max_length= 120, default= "Hello there, welcome to Typewriter. Your Easy solution to getting things done!", null=True, blank=True)
    timestamp  = models.DateTimeField(default=timezone.now)
    viewed = models.BooleanField(default=False)
    def __str__(self):
        return f'{self.user.username} Notfication'
    


class CustomNotification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="noti_user",
                             on_delete=models.CASCADE)
    name =  models.CharField(max_length= 120, null=True, blank=True)
    message = models.CharField(max_length= 120, default= "Hello there, welcome to Typr.", null=True, blank=True)
    target = models.CharField(max_length= 120, null=True, blank=True)
    timestamp  = models.DateTimeField(default=timezone.now)
    viewed = models.BooleanField(default=False)
    def __str__(self):
        return f'{self.user.username} Custom Notfication'


def usernotify_receiver(sender, instance, created, *args, **kwargs):
    if created:
        usernotify = Notification.objects.create(user=instance)

post_save.connect(usernotify_receiver, sender=settings.AUTH_USER_MODEL)