import uuid
from django.db import models
from django.contrib.auth.models import User
from django_tenants.models import TenantMixin, DomainMixin



class Client(TenantMixin):
    
    """ This table is used to create company.
    """
    # created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=1000,verbose_name="Company name")
    project_manager_email = models.EmailField(max_length = 254)
    random_url = models.UUIDField(default=str(uuid.uuid4()))
    company_logo = models.ImageField(upload_to="company_logo/")
    created_on = models.DateTimeField(auto_now=True)

class Pillar(models.Model):
    
    """ This table is used to create Core Value Pledge Kudo.
    """
    client_id = models.ForeignKey(Client, on_delete=models.CASCADE,related_name="pillar", null=True)
    pillar = models.CharField(max_length=1000,verbose_name="Pillar")

    def __str__(self):
        return self.pillar

class AdminPledge(models.Model):
    
    """ This table is used to create Pledge Names.
    """
    client_id = models.ForeignKey(Client, on_delete=models.CASCADE,related_name="admin_pledge", null=True)
    admin_pledge = models.CharField(max_length=1000,verbose_name="Admin_pledge")

    def __str__(self):
        return self.admin_pledge

class Domain(DomainMixin):
    pass


class UserProfile(models.Model):
    
    """ This table is used to store profile picture of a registered user 
    This table is join with User table. User profile picture information is save in it"""

    user = models.OneToOneField(User, related_name="profiles", on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to="profilepic/",default='profilepic/default-user.png', null=True, blank=True)
    # company_logo = models.ImageField(upload_to="company_logo/",null=True, blank=True)

