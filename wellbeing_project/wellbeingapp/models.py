from django.db import models
from django.contrib.auth.models import User
import numpy as np
from PIL import Image, ImageDraw
from io import BytesIO
from django.core.files.base import ContentFile
# from customers.models import Pillar
from django.db.models import ManyToManyField

# from django.apps import apps
# Pillar = apps.get_model('customers', 'Pillar')

# Create your models here.
class UserProfile(models.Model):
    """ This table is join with User table. User profile picture information is save in it"""

    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to="profilepic/",default='profilepic/default-user.png', null=True, blank=True)

    def save(self, *args, **kwargs):
        # Open the input image as numpy array, convert to RGB
        img=Image.open(self.profile_picture).convert("RGB")
        npImage=np.array(img)
        h,w=img.size
        alpha = Image.new('L', img.size,0)
        draw = ImageDraw.Draw(alpha)
        draw.pieslice([0,0,h,w],0,360,fill=255)
        npAlpha=np.array(alpha)
        npImage=np.dstack((npImage,npAlpha))
        image_data = Image.fromarray(npImage)
        new_image_io = BytesIO()
        image_data.save(new_image_io, format='PNG')
        self.profile_picture.save(
                'crop_image.png',
                content=ContentFile(new_image_io.getvalue()),
                save=False
            )
        super(UserProfile,self).save(*args, **kwargs)
        img.close()
        new_image_io.close()

class PledgeDetail(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    pillars = models.ManyToManyField(to='customers.Pillar',blank=True)
    pledge_text = models.TextField(default='',null=True, blank=True)
    person_name = models.CharField(max_length=200)
    person_photo = models.ImageField(upload_to="personphoto/",default='profilepic/default-user.png')

    def __str__(self):
        return self.pillars


class PledgeComment(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    pledge = models.ForeignKey(PledgeDetail, on_delete=models.CASCADE)
    comment = models.TextField(default='',null=True, blank=True)


class Proud(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    pillars = models.ManyToManyField(to='customers.Pillar',related_name='proud_pillars',blank=True)
    proud_text = models.TextField(default='',null=True, blank=True)


class UserPledge(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    pledge_text = models.TextField(default='',null=True, blank=True)