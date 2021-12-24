import random
import re
from django.conf import settings
from django.db import connection
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext, ugettext_lazy as _
from django import forms
from django.contrib.auth.models import User
from customers.models import *
from wellbeingapp.models import UserProfile
from  django.core.validators import RegexValidator

class ClientRegistrationForm(forms.ModelForm):
    error_messages = {"invalid_domain": _("This domain is already used"),"reserve_keyword":_("This is reserve keyword please try with other domain name")}
    """Form definition for ClientRegistration."""
    alphanumeric = RegexValidator(r'^[0-9a-zA-Z]*$', 'Only alphanumeric characters are allowed and no blank spaces.')
    domain = forms.CharField(max_length=100,validators=[alphanumeric],label="Prefix for domain",required=True)
    company_logo = forms.ImageField(label=_('Company Logo'),required=False)
    pillar = forms.CharField(max_length=100,label="Core Value Pillar Names",required=True,widget=forms.Textarea(attrs={'rows':5,'cols':32}))
    admin_pledge = forms.CharField(max_length=100,label="Pledge Names",required=True,widget=forms.Textarea(attrs={'rows':5,'cols':32}))
    class Meta:
        model = Client
        fields = ('domain','company_name','project_manager_email','company_logo','pillar','admin_pledge')
        
    def __init__(self, *args, **kwargs):
        """ apply css classes to form or models fields """
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            if type(visible.field) in (
                forms.CharField,
                forms.EmailField,
                forms.ImageField,
            ):
                visible.field.widget.attrs["class"] = "form-control w-100"
    def clean_domain(self):
        cd = self.cleaned_data
        print("clean Data: ",cd)
        domain = cd.get("domain").lower() + ".{}".format(settings.MAIN_DOMAIN)
        print("Domain:",domain)
        if Domain.objects.filter(domain=domain):
           
            raise forms.ValidationError(
                self.error_messages["invalid_domain"], code="invalid_domain"
            )
        elif Domain.objects.filter(domain=cd.get("domain").lower()):
            raise forms.ValidationError("Domain already taken")
            
        if cd.get("domain").lower() in ['select','create','from']:
            raise forms.ValidationError(self.error_messages['reserve_keyword'],code="reserve_keyword")
        return domain

    def clean_company_name(self):
        company_name = self.cleaned_data['company_name']
        print("company_name: ",company_name)
        exp = '^[a-zA-Z ]+[0-9 ]*$'
        if not (re.search(exp, company_name)):
            raise forms.ValidationError("Enter Valid Company Name")
        return company_name

    def clean_company_logo(self):
        company_logo = self.cleaned_data['company_logo']
        print("company_logo: ",company_logo)
        if not (company_logo):
            raise forms.ValidationError("Company logo not uploaded")
        return company_logo

    def save(self, commit=True):

        import time
        cd = self.cleaned_data
        schema_name = cd.get("company_name").split(' ')[0].lower()
        print("company_name",schema_name)
        pillar = cd.get("pillar").split('\n')
        admin_pledge = cd.get("admin_pledge").split('\n')
        check = Client.objects.filter(schema_name=schema_name)
        print("check",check)
        for i in check:
            if i.schema_name == schema_name:
                num = random.randint(1,999)
                schema_name = schema_name+str(num)
            else:
                schema_name = schema_name
        
        instance = super(ClientRegistrationForm,self).save(commit=False)
             
        instance.schema_name = schema_name
        if commit:
            try:
                instance.save()
                instance.domains.create(domain=cd.get("domain"))
                for pillar_text in pillar:
                    Pillar.objects.create(client_id=instance, pillar=pillar_text.replace('\r',''))
                for admin_pledge_text in admin_pledge:
                    AdminPledge.objects.create(client_id=instance, admin_pledge=admin_pledge_text.replace('\r',''))
            except Exception as e:
                print("Exception: ",e)
                pass
        return instance