from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
#from phone_field import PhoneField
# Create your models here.

GENDER_STATUS = (
    ('Male', 'M'),
    ('Female', 'F'),
    ('Unknown', 'U')
)

class Temp(models.Model):
    number = models.IntegerField(blank=True, null=True)
    username = models.TextField(default= "", max_length=20)
    gender = models.CharField(choices=GENDER_STATUS, max_length=11, default="Unknown", null=True, blank=True)


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    bio = models.TextField(default= "", max_length=120, null=True, blank=True)
    timestamp = models.DateTimeField(default = timezone.now)
    updated = models.DateTimeField(auto_now= True)
    #phonenumber = PhoneNumberField()#blank=True, help_text='Contact phone number', null=True, unique=True)
    phonenumber = models.IntegerField(blank=True, null=True)
    gender = models.CharField(choices=GENDER_STATUS, max_length=11, default="Unknown", null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'




def userprofile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        userprofile = Profile.objects.create(user=instance)



post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL)
