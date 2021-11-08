import random
from django import forms
from django.contrib.auth.models import User
from customers.models import *
from wellbeingapp.models import *
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext, gettext_lazy as _
from django.forms.widgets import Widget, PasswordInput
from django.template import loader
from django.utils.safestring import mark_safe
from django.forms import ModelForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout

class PasswordFieldWidget(PasswordInput):
    """ Custom password field widget to display """

    template_name = "password_field_widget.html"

    def format_value(self, value):
        return value

    def get_context(self, name, value, attrs):
        context = super(PasswordFieldWidget, self).get_context(name, value, attrs)
        context["widget"] = {
            "name": name,
            "is_hidden": self.is_hidden,
            "required": self.is_required,
            "value": value,
            "attrs": self.build_attrs(self.attrs, attrs),
            "template_name": self.template_name,
        }
        return context

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(template)



def get_user(email):
    try:
        return User.objects.get(email=email.lower()).username
    except User.DoesNotExist:
        return None

class ProfilePictureWidget(Widget):
    """ Custom Profile picture widget to display """

    template_name = "widget.html"

    def format_value(self, value):
        return value

    def value_from_datadict(self, data, files, name):
        "File widgets take data from FILES, not POST"
        return files.get(name)

    def get_context(self, name, value, attrs):
        context = {}
        context["widget"] = {
            "name": name,
            "is_hidden": self.is_hidden,
            "required": self.is_required,
            "value": self.format_value(value),
            "attrs": self.build_attrs(self.attrs, attrs),
            "template_name": self.template_name,
        }
        return context

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(template)

class EmailAuthenticationForm(AuthenticationForm):
    """
    Override the default AuthenticationForm to force email-as-username behavior.
    """

    email = forms.EmailField(label="Email", max_length=254)
    message_incorrect_password = "Password is incorrect"
    message_inactive = "user is inactive"

    def __init__(self, request=None, *args, **kwargs):
        super(EmailAuthenticationForm, self).__init__(request, *args, **kwargs)
        del self.fields["username"]
        self.fields.keyOrder = ["email", "password"]

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        print("email == ", email)
        
        if email and password:
            username = get_user(email)
            self.user_cache = authenticate(username=username, password=password)
            print("-----+++++",self.user_cache)
            # try:
            #     user = User.objects.get(email=email)
            #     pledge_id = self.request.get_full_path().split('=')[1].split('/')[1]
            #     print("pledge_id: ",pledge_id)
            #     pledge = PledgeDetail.objects.get(pledge_id=pledge_id)
            #     print("pledge: ",pledge)
            #     Assign.objects.get_or_create(user=user, pledge=pledge)
            # except Exception as e:
            #     print(e)
            try:
                if self.request.get_full_path().split('=')[1]:
                    print("Inside if",self.request.get_full_path())
                    self.request.session['url'] = self.request.get_full_path().split('=')[1]
                else:
                    self.request.session['url'] = '/'
            except Exception as e:
                self.request.session['url'] = '/'
    
            if self.user_cache is None:
                raise forms.ValidationError(self.message_incorrect_password)
            if not self.user_cache.is_active:
                raise forms.ValidationError(self.message_inactive)
        print("Last ===")
        return self.cleaned_data

class RegisrationForm(UserCreationForm):
    """ Registration form for Client  as admin """
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    first_name = forms.CharField(
        max_length=30, required=False, help_text="Optional.", label="Name"
    )
    email = forms.EmailField(
        max_length=254, help_text="Required. Inform a valid email address."
    )
    profile_picture = forms.ImageField(widget=ProfilePictureWidget,required=False,label='')    

    group = forms.ChoiceField(widget=forms.RadioSelect,
        required=False
    )
    ip_address = forms.CharField(max_length=128, label='',
        widget=forms.HiddenInput(),
        required = False)

    class Meta:
        model = User
        fields = (
            "first_name",
            "email",
            "group",
            "password1",
            "password2",
            "profile_picture",
            "ip_address",
        )
        

    def __init__(self, *args, **kwargs):
        """ apply css classes to form or models fields """
        self.request = kwargs.pop('request', None)
        
        group_choices = self.group_choices()
        self.is_superuser = kwargs.pop('is_superuser',False)
        self.is_staff = kwargs.pop('is_staff',False) 
        super(RegisrationForm, self).__init__(*args, **kwargs)
        self.fields['group'].choices = group_choices
        
        self.fields['password1'].widget = PasswordFieldWidget(attrs={'name':'password1'})
        self.fields['password2'].widget = PasswordFieldWidget(attrs={'name':'password2'})
        # self.fields['ip_address'].widget = HiddenInput()
        # self.fields['profile_picture'].value = self.request.FILES.get('profile_picture',None)
       
        if not group_choices:
            self.fields.pop('group')
        
        for visible in self.visible_fields():
            if type(visible.field) in (
                forms.CharField,
                forms.EmailField,
                forms.ImageField,
            ):
                visible.field.widget.attrs["class"] = "form-control w-100"        

 

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1").strip()
        password2 = self.cleaned_data.get("password2").strip()
       
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def group_choices(self):
        try:
            
            args = self.request.GET['next'].split('/') if self.request else []
            if args[1]:
                
                survey_obj = Survey.objects.filter(survey_id=args[1]).first() 
                if survey_obj:
                    
                    return [(group.id, group.name) for group in  SurveySessionGroup.objects.filter(survey_id=survey_obj) if group.name != 'None' and group.name !='none']
            return []
        except Exception as e:
            return []
    
    
    @classmethod
    def get_username(cls, email):
        username = email.split("@")[0]
        while username:
            if not User.objects.filter(username=username).exists():
                return username
            username = username + "{:03d}".format(random.randrange(1, 999))


    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email.lower()):          
            raise forms.ValidationError("Email already registered.Please click on SignIn button to continue.")
        return self.cleaned_data['email'].lower()

    
    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        if not first_name:
            raise forms.ValidationError("Please Enter First Name")
        return first_name


    def clean_ip_address(self):
        ip_address = self.cleaned_data['ip_address']
        print('Ip==',ip_address)
        return ip_address

    def clean_group(self):
        group = self.cleaned_data['group']
        if group == '':
            raise forms.ValidationError("Please Select any one group")
        return group

    
    def clean_profile_picture(self):
        # profile_picture = self.cleaned_data["profile_picture"]
        profile_picture = self.request.FILES.get('profile_picture','profilepic/default-user.png')
        return profile_picture

    

    def save(self, commit=True):
        cd = self.cleaned_data
        group = cd.get("group")
        print('---',cd.get('ip_address'))
        instance = super(RegisrationForm, self).save(commit=False)
        instance.username = RegisrationForm.get_username(instance.email)
        # instance.is_superuser= self.is_superuser
        # instance.is_staff = self.is_staff
        if commit:
          
            instance.save()
            if group:
                group =  SurveySessionGroup.objects.get(id=cd.get("group"))
                group.user_list.add(instance)
            else:
                group = ''

            profile_object = UserProfile.objects.create(
                **{"user": instance, "profile_picture": cd.get("profile_picture","profilepic/default-user.png"),"ip_address":cd.get('ip_address')}
            )

            profile_object.save()

            
            args = self.request.GET['next'].split('/') if self.request else []
            survey = Survey.objects.get(survey_id=args[1])
            session_type = Survey.objects.get(survey_id=args[1]).session_type
            
            if session_type == 'no_vote'  or session_type == 'action_items' or session_type == 'threaded_discussions' or session_type == 'Ideas' or session_type == 'survey':
                
                survey_assign = survey.assign.create(user=instance, is_submit=False,survey=survey)
                survey_assign.save()
        return instance

class TeamAdminRegistrationForm(UserCreationForm):
    """ Registration form for Team admin  as admin """
    first_name = forms.CharField(
        max_length=30, required=False, help_text="Optional.", label="Name"
    )
    email = forms.EmailField(
        max_length=254, help_text="Required. Inform a valid email address.",
    )
    # profile_picture = forms.ImageField(widget=ProfilePictureWidget,required=False,label='')
    profile_picture = forms.ImageField(label=_('Profile Picture'),required=False)    
    #company_logo = forms.ImageField(required=False)    

    

    class Meta:
        
        model = User
        fields = (
            #"company_logo",
            "first_name",
            "email",
            "profile_picture",
            "password1",
            "password2",
            
        )
        

    def __init__(self, *args, **kwargs):
        """ apply css classes to form or models fields """
        self.request = kwargs.pop('request', None)
        self.is_superuser = kwargs.pop('is_superuser',False)
        self.is_staff = kwargs.pop('is_staff',False) 
        super(TeamAdminRegistrationForm, self).__init__(*args, **kwargs)
        
        self.fields['password1'].widget = PasswordFieldWidget(attrs={'name':'password1'})
        self.fields['password2'].widget = PasswordFieldWidget(attrs={'name':'password2'})
        self.fields['email'].widget = forms.EmailInput(
            attrs={
                'class': 'form-control w-100',
                'autocomplete':'off'
            }
        )
        
        for visible in self.visible_fields():
            if type(visible.field) in (
                forms.CharField,
                forms.EmailField,
                forms.ImageField,
            ):
                visible.field.widget.attrs["class"] = "form-control w-100"
        
    
    @classmethod
    def get_username(cls, email):
        username = email.split("@")[0]
        while username:
            if not User.objects.filter(username=username).exists():
                return username
            username = username + "{:03d}".format(random.randrange(1, 999))


    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        if not first_name:
            raise forms.ValidationError("Please Enter First Name")
        return first_name

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1").strip()
        password2 = self.cleaned_data.get("password2").strip()
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2


    def clean_email(self):
        email = self.cleaned_data['email']
       
        if User.objects.filter(email=email.lower()):          
            raise forms.ValidationError("Email already registered, please do Sign In")
        return self.cleaned_data['email'].lower()
    
    # def clean_profile_picture(self):
    #     profile_picture = self.cleaned_data["profile_picture"]
        
    def clean_profile_picture(self):
        profile_picture = self.cleaned_data['profile_picture']
        return profile_picture

    # def clean_company_logo(self):
    #     company_logo = self.cleaned_data["company_logo"]
       
        # return company_logo


    def save(self, commit=True):
        cd = self.cleaned_data
        instance = super(TeamAdminRegistrationForm, self).save(commit=False)
        instance.username = TeamAdminRegistrationForm.get_username(instance.email)
        # instance.is_superuser= self.is_superuser
        instance.is_staff = True
        if commit:
            instance.save()
           
            profile_object = UserProfile.objects.create(
                **{"user": instance, "profile_picture": cd.get("profile_picture","profilepic/default-user.png")}
            )
            profile_object.save()
        return instance

class AddPledgeForm(forms.ModelForm):
    pledge_text = forms.CharField(required=True, widget=forms.Textarea(attrs={'rows':7,'placeholder': 'Enter pledge text'}))
    person_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'cols':25,'placeholder': 'Enter person name'}))
    person_photo = forms.ImageField(label=_('Person Photo'))
    class Meta:
        model = PledgeDetail
        fields = ['pledge_text','person_name','person_photo']
        exclude = ['created_by']

    def clean_person_photo(self):
        person_photo = self.cleaned_data['person_photo']
        print("person_photo: ",person_photo)
        if not (person_photo):
            raise forms.ValidationError("Person photo not uploaded")
        return person_photo

class UserPledgeForm(forms.ModelForm):
    pledge_text = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Enter pledge text'}))
    class Meta:
        model = UserPledge
        fields = ['pledge_text']
        exclude = ['created_by']

class EditPledgeForm(forms.ModelForm):
    pledge_text = forms.CharField(widget=forms.Textarea())
    class Meta:
        model = PledgeDetail
        fields = ['pledge_text',]
        exclude = ['created_by','person_name','person_photo','pillars']

class AddCommentForm(forms.ModelForm):
    comment = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Enter comment'}))
    class Meta:
        model = PledgeComment
        fields = ['comment']
        exclude = ['created_by','pledge']

class AddProudForm(forms.ModelForm):
    proud_text = forms.CharField(widget=forms.Textarea(attrs={'rows':8,'cols':25,'placeholder': 'Enter proud text'}))
    class Meta:
        model = Proud
        fields = ['proud_text']
        exclude = ['created_by']

