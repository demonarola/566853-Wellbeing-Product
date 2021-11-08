from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.http import (
    HttpResponse,
    HttpResponseNotFound,
    HttpResponseForbidden,
    HttpResponseRedirect,
)
from rest_framework import generics, viewsets
from customers.models import *

from customers.serializers import *
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.db.models.functions import Lower
from customers.forms import ClientRegistrationForm
from rest_framework.decorators import permission_classes
from django.urls import reverse,reverse_lazy
from requests import get
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
)


def error_403(request, exception=None):
    """ Display 403 Error page"""
    data = {"status": 403, "msg": "Page not found"}
    return TemplateResponse(request, "error.html", data, status=403)


def error_404(request, exception=None):
    """ Display 404 Error page"""
    data = {"status": 404, "msg": "Page not found"}
    return TemplateResponse(request, "error.html", data, status=403)


def error_500(request, exception=None):
    """ Display 500 Error page """
    data = {"status": 500, "msg": "Server Error"}
    return TemplateResponse(request, "error.html", data, status=500)

class AdminView(LoginRequiredMixin, APIView):
    """ Show admin landing page """

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "admin.html"
    permission_classes = [IsAdminUser]

    
    def get(self, request): 
        return Response({"companies":Domain.objects.all().order_by(Lower('tenant__company_name')),"form":ClientRegistrationForm,'title':'Landing Page for the Company'})

   
class RegistrationListView(ListView):
    """ Remove it """
    model = Domain
    template_name = "domain_list.html"

class ProfileView(LoginRequiredMixin, APIView):
    """ Display Profile Data , also can edit email or change profile picture
    Hit on Change Password will redirect to change password page """
    
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "profile.html"
    permission_classes = [IsAuthenticated]
    
    
    def get(self, request):
    
        profile = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile[0])
        
        return Response({'data':serializer.data})
    
    def post(self, request):
        profile = get_object_or_404(UserProfile,user=request.user)        
        new_serializer = UserProfileSerializer(profile,
            data=request.data, context={"request": request}
        )
        if not new_serializer.is_valid():
            return Response({'data':new_serializer.data,'error':"data is invalid"})
        new_serializer.save()
        return HttpResponseRedirect(redirect_to="/")

class CreateTenantView(viewsets.ModelViewSet):
    """ Remove it """
    queryset = Domain.objects.all()
    serializer_class = DomainSerializer
    permission_classes = [IsAdminUser]

 
def company_delete_view(request, pk):
    """ Delete Company/client by domain id """
    company = get_object_or_404(Domain, pk=pk)
    cascade_object = Client.objects.get(domains=company)
    cascade_object._drop_schema(force_drop=True)
    # cascade_object.delete()
    company.delete()
    return HttpResponseRedirect(reverse_lazy('super-admin'))

class SignUpView(CreateView):
    """ Regisration of Client admin with respective domain entry.
    This also create tenant in database for newly register domain """

    model = Domain
    template_name = "registration.html"
    form_class = ClientRegistrationForm

    def get_context_data(self, **kwargs):
        context = super(SignUpView, self).get_context_data(**kwargs)
        context["target"] = reverse("registration")
        return context

    def get_success_url(self):
        return reverse("super-admin")

    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponseRedirect(reverse("login"))
        return super(SignUpView, self).get(request, *args, **kwargs)

class ProfileView(LoginRequiredMixin, APIView):
    """ Display Profile Data , also can edit email or change profile picture
    Hit on Change Password will redirect to change password page """
    
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "profile.html"
    permission_classes = [IsAuthenticated]
    
    
    def get(self, request):
        profile = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile[0])
        
        return Response({'data':serializer.data})
    
    def post(self, request):
        profile = get_object_or_404(UserProfile,user=request.user)        
        new_serializer = UserProfileSerializer(profile,
            data=request.data, context={"request": request}
        )
        if not new_serializer.is_valid():
            return Response({'data':new_serializer.data,'error':"data is invalid"})
        new_serializer.save()
        return HttpResponseRedirect(redirect_to="/")
