import statistics
from django import template
# from wellbeingapp.forms import SurveyForm
from wellbeingapp.models import *
from customers.models import *
from django.db import connection
import mammoth

register = template.Library()


# @register.filter
# def get_project_manager(company_id):
#     company_name = Client.objects.get(id=company_id)
#     connection.set_tenant(company_name)
#     user = User.objects.filter(is_staff=True)
#     return user