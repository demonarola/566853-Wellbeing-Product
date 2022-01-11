from django.shortcuts import render ,get_object_or_404, redirect
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from wellbeingapp.serializers import *
from django.contrib.auth import authenticate, login,login as auth_login, logout as auth_logout
from django.contrib.auth.views import LogoutView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.template.response import TemplateResponse
from wellbeingapp.forms import *
from django.contrib import messages
from wellbeingapp.forms import (
    RegisrationForm,
)
from django.db import connection
from requests import get
from django.urls import reverse
from django.contrib.auth import views as auth_view
from django.contrib.auth.models import User
from django.views.generic.edit import UpdateView
from wellbeingapp.models import *
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth import views as auth_view
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
)
from django.views import View
from customers.models import *
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from wellbeingapp.serializers import *



class EmailLoginView(auth_view.LoginView):
    """ Login View """
    form_class = EmailAuthenticationForm
    title ="Company"
    notes = 'This academy registration is for academy use only.An email and password from the academy are needed to set up a teams get it session.'
    is_signup=True
    def get_context_data(self, **kwargs):
        context = super(EmailLoginView, self).get_context_data(**kwargs)
        print("context == ", context['next'])
        # valid = self.get_form().is_valid()
        context['registrationform'] = RegisrationForm(**{'request':self.request})
        context['title']=self.title
        context['notes']=self.notes
        context['is_signup']=self.is_signup
        
        return context
        return render(request,'registration/login.html')

    def get_success_url(self):
        print(self.request.user)
        if self.request.user.is_superuser:
            return reverse("super-admin")
        else:    
            return reverse("wellbeing_pledge")

class TeamAdminRegistrationView(APIView):
    """ Registration view for Team admin only """
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "ta_registration.html"
    form_class = TeamAdminRegistrationForm

    title = "USER REGISTRATION"

    def get(self, request):
        """ render registration template """
        return Response({'form': self.form_class,"title":self.title})
    
    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        url = request.get_host().split(':')[0]
        dom = Domain.objects.get(domain=url).tenant_id
        form = self.form_class(request.POST,request.FILES)
        if not form.is_valid():
            return Response({'form':form,"title":self.title})
        user_data = form.save()
        try:
            print("request.POST.get('email') == ",request.POST.get('email'))
            project_manager_email = Client.objects.get(id=dom, project_manager_email=request.POST.get('email'))
            print("project_manager_email == ",project_manager_email)
            user_data.is_staff = True
            user_data.save()
        except Exception as e:
            print(e)
            user_data.is_staff = False
            user_data.save()
            pass

        username = User.objects.get(email=form.cleaned_data['email']).username
        print("username: ",username)
        password = form.cleaned_data['password1']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(self.request, user)
                self.request.session['url']='wellbeing_pledge'
                return HttpResponseRedirect(redirect_to='/wellbeing_pledge')
        return HttpResponseRedirect(redirect_to="/wellbeing_pledge")

class TeamAdminLogout(LogoutView):
    """ Team admin Logout View """
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        
        # ta_username = self.request.user.username
        # if User.objects.filter(username=ta_username,is_superuser=True).first() != None:
        #     delete_user = User.objects.get(username=ta_username,is_superuser=True)
        #     delete_user.delete()
        auth_logout(request)
        next_page = self.get_next_page()

        if next_page:
            return TemplateResponse(request, "ta_message.html")

        return super().dispatch(request, *args, **kwargs)


class WellbeingPledgeView(LoginRequiredMixin,APIView):
    template_name = "wellbeing_pledge.html"
    renderer_classes = [TemplateHTMLRenderer]
    # title = "Project Manager Screen"
    permission_classes = [IsAuthenticated]

    def get(self, request, **kwargs):
        """ render pledge form """
        is_manager = request.query_params.get('is_manager')
        print(is_manager)
        url = request.get_host().split(':')[0]
        dom = Domain.objects.get(domain=url).tenant_id
        company_id = Client.objects.get(id=dom)
        connection.set_tenant(company_id)
        company_pillar = Pillar.objects.filter(client_id=company_id.id)
        company_pledge_kudo = AdminPledge.objects.filter(client_id=company_id.id)
        
        user = request.user
        form = None
        form = AddPledgeForm()
        user_pledge_form = UserPledgeForm()
        comment_form = AddCommentForm()
        pledge = PledgeDetail.objects.all()
        pledge_comments = PledgeComment.objects.all()
        # for d in pledge:
        #     print(d.admin_pillar.all())

        """ render Add Pledge Kudo form """
        pledge_kudo_form = AddProudForm()
        pledge_kudo = PledgeKudo.objects.all()
        # for i in pledge_kudo:
        #     print("=====",i.pillars.all())
        """ render Add Core Kudo form """
        core_kudo_form = AddCoreKudoForm()
        core_kudo = CoreKudos.objects.all()

        return Response({
                        # "title":self.title,
                        "logo":company_id.company_logo, 
                        "form":form,
                        "pledge":pledge,
                        "user_pledge_form":user_pledge_form,
                        "comment_form":comment_form,
                        "pledge_comments":pledge_comments,
                        "user":user,
                        "company_pillar":company_pillar,
                        "is_manager":is_manager,
                        "pledge_kudo_form":pledge_kudo_form,
                        "pledge_kudo":pledge_kudo,
                        "company_pledge_kudo":company_pledge_kudo,
                        "core_kudo_form":core_kudo_form,
                        "core_kudo":core_kudo,
                        })

    def post(self,request):
        form = AddPledgeForm(request.POST, request.FILES)
        if form.is_valid():
            pledge = form.save(commit=False)
            pledge.created_by = get_object_or_404(User, pk=request.user.id)
            pledge.save()
            pillar_text = request.POST.getlist('pledge_kudo')
            print("\n\n Pillar text == ", pillar_text,"==\n\n")
            for pillar_obj in pillar_text:
                pledge.admin_pledge.add(pillar_obj)
            pledge.save()
            messages.success(request, 'Pledge Created successfully!')
            return HttpResponseRedirect('/wellbeing_pledge')

class EditWellbeingPledgeView(LoginRequiredMixin,APIView):
    template_name = "edit_wellbeing_pledge.html"
    renderer_classes = [TemplateHTMLRenderer]
    title = "Project Manager Screen"
    permission_classes = [IsAuthenticated]

    def get(self, request,pk, *args, **kwargs):
        obj = PledgeDetail.objects.get(id=pk)
        edit_form = EditPledgeForm(instance=obj)
        return Response({'edit_form':edit_form, 'pk':obj.id})

    def post(self,request,pk,*args, **kwargs):
        pledge = PledgeDetail.objects.get(id=pk)
        edit_form = EditPledgeForm(request.POST,request.FILES, instance=pledge)
        if edit_form.is_valid():
            edit_form = edit_form.save(commit=False)
            edit_form.save()
            return HttpResponseRedirect('/wellbeing_pledge')

class PledgeCommentView(LoginRequiredMixin,APIView):
    template_name = "wellbeing_pledge.html"
    renderer_classes = [TemplateHTMLRenderer]
    title = "Project Manager Screen"
    permission_classes = [IsAuthenticated]

    def get(self,request, **kwargs):
        """ render comment form """
        comment_form = AddCommentForm()
        pledge = PledgeComment.objects.all()
        return Response({"comment_form":comment_form})

    def post(self,request,*args, **kwargs):
        """ Save comment """
        pledge_id = request.POST.get('pledge_id')
        form = AddCommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.created_by = get_object_or_404(User, pk=request.user.id)
            comment.pledge = PledgeDetail.objects.get(id=pledge_id)
            comment.save()
            return HttpResponseRedirect('/wellbeing_pledge')

class DeletePledgeCommentView(LoginRequiredMixin,APIView):
    url='/wellbeing_pledge/'
    permission_classes = [IsAuthenticated]

    def get(self,request,id):
        """ render comment form """
        obj = PledgeComment.objects.get(id=id)
        obj.delete()
        return HttpResponseRedirect('/wellbeing_pledge')


class EditPledgeCommentView(LoginRequiredMixin,APIView):
    template_name = "edit_pledge_comment.html"
    renderer_classes = [TemplateHTMLRenderer]
    permission_classes = [IsAuthenticated]
    # title = "Project Manager Screen"

    def get(self, request,pk, *args, **kwargs):
        obj = PledgeComment.objects.get(id=pk)
        edit_comment_form = AddCommentForm(instance=obj)
        return Response({'edit_comment_form':edit_comment_form, 'pk':obj.id})

    def post(self,request,pk,*args, **kwargs):
        comment = PledgeComment.objects.get(id=pk)
        edit_comment_form = AddCommentForm(request.POST, instance=comment)
        if edit_comment_form.is_valid():
            edit_comment_form = edit_comment_form.save(commit=False)
            edit_comment_form.save()
            return HttpResponseRedirect('/wellbeing_pledge')

""" ProudView view for Pledge Kudo """
class ProudView(LoginRequiredMixin,APIView):
    template_name = "proud.html"
    renderer_classes = [TemplateHTMLRenderer]
    title = ""
    permission_classes = [IsAuthenticated]

    def get(self, request, **kwargs):
        """ render proud form """
        
        url = request.get_host().split(':')[0]
        dom = Domain.objects.get(domain=url).tenant_id
        company_id = Client.objects.get(id=dom)
        connection.set_tenant(company_id)
        company_pledge_kudo = AdminPledge.objects.filter(client_id=company_id.id)

        user = request.user
        form = None
        form = AddProudForm()
        pledge_kudo = PledgeKudo.objects.all()
        select_result = self.request.query_params.get('pledge_kudos')
        filter_result = PledgeKudo.objects.filter(pillars=select_result)
        return Response({
                        "title":self.title,
                        "logo":company_id.company_logo, 
                        "form":form,
                        "pledge_kudo":pledge_kudo,
                        "user":user,
                        "company_pledge_kudo":company_pledge_kudo,
                        "selected_pledge":select_result,
                        "filter_result":filter_result,
                        })

    def post(self,request):
        form = AddProudForm(request.POST, request.FILES)
        if form.is_valid():
            proud = form.save(commit=False)
            proud.created_by = get_object_or_404(User, pk=request.user.id)
            proud.save()
            proud_text = request.POST.getlist('pledge_kudo')
            for pillar_obj in proud_text:
                proud.pillars.add(pillar_obj)
            proud.save()
            return HttpResponseRedirect('/wellbeing_pledge')

class DeleteProudView(LoginRequiredMixin,APIView):
    url='/proud/'
    permission_classes = [IsAuthenticated]

    def get(self,request,id):
        """ render comment form """
        obj = PledgeKudo.objects.get(id=id)
        obj.delete()
        return HttpResponseRedirect('/proud')

class EditProudView(LoginRequiredMixin,APIView):
    template_name = "edit_proud.html"
    renderer_classes = [TemplateHTMLRenderer]
    permission_classes = [IsAuthenticated]
    # title = "Project Manager Screen"

    def get(self, request,pk, *args, **kwargs):
        obj = PledgeKudo.objects.get(id=pk)
        edit_proud_form = AddProudForm(instance=obj)
        return Response({'edit_proud_form':edit_proud_form, 'pk':obj.id})

    def post(self,request,pk,*args, **kwargs):
        comment = PledgeKudo.objects.get(id=pk)
        edit_proud_form = AddProudForm(request.POST, instance=comment)
        print(edit_proud_form.errors)
        if edit_proud_form.is_valid():
            edit_proud_form = edit_proud_form.save(commit=False)
            edit_proud_form.save()
            return HttpResponseRedirect('/proud')

class UserPledgeView(LoginRequiredMixin,APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request,*args, **kwargs):
        """ Save comment """
        user_pledge_form = UserPledgeForm(request.POST)
        url = request.get_host().split(':')[0]
        dom = Domain.objects.get(domain=url)
        company_id = Client.objects.get(id=dom.tenant_id)
        connection.set_tenant(company_id)
        print(dom.domain)
        if user_pledge_form.is_valid():
            user_pledge_form = user_pledge_form.save(commit=False)
            user_pledge_form.created_by = get_object_or_404(User, pk=request.user.id)
            user_pledge_form.save()
            subject = render_to_string('email/confirmation_email_subject.txt')

            body = render_to_string('email/confirmation_email_body.html',{'pledge_text': user_pledge_form.pledge_text, 'user':user_pledge_form.created_by, 'dom':dom.domain})
    
            recipients = [company_id.project_manager_email]
            # recipients = ["avh@narola.email"]
            try:
                send_mail(
                    subject,
                    '',
                    settings.EMAIL_HOST_USER,
                    list(set(recipients)),
                    html_message = body,
                )
            except Exception as e:
                print("Error ===",e)
        return HttpResponseRedirect('/wellbeing_pledge')

class ProfileView(LoginRequiredMixin, APIView):
    """ Display Profile Data , also can edit email or change profile picture
    Hit on Change Password will redirect to change password page """
    
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "profile.html"
    permission_classes = [IsAuthenticated]
    success_url = ''
    def get(self, request):
        # survey_id = Survey.objects.get()
        profile = get_object_or_404(UserProfile,user=request.user)
        serializer = UserProfileSerializer(profile)
        return Response({'data':serializer.data})
    
    def post(self, request):
      
        profile = get_object_or_404(UserProfile,user=request.user)
        new_serializer = UserProfileSerializer(profile,
            data=request.data, context={"request": request}
        )
        
        if not new_serializer.is_valid():
            return Response({'data':new_serializer.data,'error':"data is invalid"})
        new_serializer.save()
        # home = '/' if request.user.is_superuser else '/{}/custom'.format(survey_id)
        
        return HttpResponseRedirect('/wellbeing_pledge/')

        # if self.request.session.get('url') == '/':
        #     self.success_url = self.request.session.get('url')
        # else:
        #     self.success_url = self.request.session.get('url')
           
        return HttpResponseRedirect(redirect_to=self.success_url)


class CoreKudoView(LoginRequiredMixin,APIView):
    template_name = "core_kudo.html"
    renderer_classes = [TemplateHTMLRenderer]
    title = ""
    permission_classes = [IsAuthenticated]

    def get(self, request, **kwargs):
        """ render proud form """
        
        url = request.get_host().split(':')[0]
        dom = Domain.objects.get(domain=url).tenant_id
        company_id = Client.objects.get(id=dom)
        connection.set_tenant(company_id)
        pillars = Pillar.objects.filter(client_id=company_id.id)
        print(pillars)
        user = request.user
        form = None
        form = AddCoreKudoForm()
        core_kudos = CoreKudos.objects.all()
        select_result = self.request.query_params.get('core_pillars')
        filter_result = CoreKudos.objects.filter(pillars=select_result)
        return Response({
                        "title":self.title,
                        "logo":company_id.company_logo, 
                        "form":form,
                        "core_kudos":core_kudos,
                        "user":user,
                        "pillars":pillars,
                        "selected_pillar":select_result,
                        "filter_result":filter_result,
                        })

    def post(self,request):
        form = AddCoreKudoForm(request.POST, request.FILES)
        if form.is_valid():
            core_kudo = form.save(commit=False)
            core_kudo.created_by = get_object_or_404(User, pk=request.user.id)
            core_kudo.save()
            core_kudo_text = request.POST.getlist('core_kudos')
            for core_kudo_obj in core_kudo_text:
                core_kudo.pillars.add(core_kudo_obj)
            core_kudo.save()
            return HttpResponseRedirect('/wellbeing_pledge')

class DeleteCoreKudoView(LoginRequiredMixin,APIView):
    url='/core_kudo/'
    permission_classes = [IsAuthenticated]

    def get(self,request,id):
        """ render comment form """
        obj = CoreKudos.objects.get(id=id)
        obj.delete()
        return HttpResponseRedirect('/core_kudo')

class EditCoreKudosView(LoginRequiredMixin,APIView):
    template_name = "edit_core_kudos.html"
    renderer_classes = [TemplateHTMLRenderer]
    permission_classes = [IsAuthenticated]
    # title = "Project Manager Screen"

    def get(self, request,pk, *args, **kwargs):
        obj = CoreKudos.objects.get(id=pk)
        edit_core_kudos_form = AddCoreKudoForm(instance=obj)
        return Response({'edit_core_kudos_form':edit_core_kudos_form, 'pk':obj.id})

    def post(self,request,pk,*args, **kwargs):
        comment = CoreKudos.objects.get(id=pk)
        edit_core_kudos_form = AddCoreKudoForm(request.POST, instance=comment)
        print(edit_core_kudos_form.errors)
        if edit_core_kudos_form.is_valid():
            edit_core_kudos_form = edit_core_kudos_form.save(commit=False)
            edit_core_kudos_form.save()
            return HttpResponseRedirect('/core_kudo')

class EditPledgeKudosPhotoView(LoginRequiredMixin,APIView):
    template_name = "edit_pledge_kudos_photo.html"
    renderer_classes = [TemplateHTMLRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request,pk, *args, **kwargs):
        obj = PledgeKudo.objects.get(id=pk)
        edit_form = EditPledgeKudosPhotoForm(instance=obj)
        return Response({'edit_form':edit_form, 'pk':obj.id})

    def post(self,request,pk,*args, **kwargs):
        pledgekudo = PledgeKudo.objects.get(id=pk)
        edit_form = EditPledgeKudosPhotoForm(request.POST,request.FILES, instance=pledgekudo)
        if edit_form.is_valid():
            edit_form = edit_form.save(commit=False)
            edit_form.save()
            return HttpResponseRedirect('/proud')

class EditCoreKudosPhotoView(LoginRequiredMixin,APIView):
    template_name = "edit_core_kudos_photo.html"
    renderer_classes = [TemplateHTMLRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request,pk, *args, **kwargs):
        obj = CoreKudos.objects.get(id=pk)
        edit_form = EditCoreKudosPhotoForm(instance=obj)
        return Response({'edit_form':edit_form, 'pk':obj.id})

    def post(self,request,pk,*args, **kwargs):
        corekudo = CoreKudos.objects.get(id=pk)
        edit_form = EditCoreKudosPhotoForm(request.POST,request.FILES, instance=corekudo)
        if edit_form.is_valid():
            edit_form = edit_form.save(commit=False)
            edit_form.save()
            return HttpResponseRedirect('/core_kudo')