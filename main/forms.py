from django import forms
from django.contrib.auth import get_user_model 
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from nocaptcha_recaptcha.fields import NoReCaptchaField

User=get_user_model()
class UserCreateForm(UserCreationForm):
    SEX_OPTIONS = (
        ('M', _('Man')),
        ('W', _('Woman')),
        ('N', _('Non-binary')),
    )
    ROL_OPTIONS = (
        ('D', 'Deportivo'),
        ('A','Aventurero'),
        ('R','Rutero'),
    )
    aux=_("Format: dd/mm/YYYY"),
  
    first_name = forms.CharField(label=_('First name'),required=False)
    last_name = forms.CharField(label=_('Last name'),required=False)
    email = forms.EmailField(label=_('Email'),required=True)
    birthdate = forms.DateTimeField(label=_('Birthdate'),input_formats=['%d/%m/%Y'], help_text=aux, required=False)
    city = forms.CharField(label=_('City'),required=True)
    sex = forms.ChoiceField(label=_('Sex'),choices=SEX_OPTIONS, required=False)
    rol = forms.ChoiceField(label=_('Role'),choices=ROL_OPTIONS, required=False)
    urlFoto = forms.URLField(label=_("Photo's URL"), required=False)
    captcha = NoReCaptchaField()
  
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "birthdate", "city", "sex", "rol", "urlFoto", "password1", "password2", "captcha")
      
    def save(self, commit=True):
        user = super(UserCreateForm, self).save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        user.birthdate = self.cleaned_data["birthdate"]
        user.city = self.cleaned_data["city"]
        user.sex = self.cleaned_data["sex"]
        user.rol = self.cleaned_data["rol"]
        user.urlFoto = self.cleaned_data["urlFoto"]
  
        if commit:
            user.save()
        return user
  
    #  Validations  
  
    def clean(self, *args, **kwargs):
        cleaned_data = super(UserCreateForm, self).clean(*args, **kwargs)
        email = cleaned_data.get('email', None)
        if email is not None:
            users = User.objects.all()
  
            for u in users:
                if email==u.email:
                    self.add_error('email', _('Email alredy exits'))
                    break
                      
        birthdate= cleaned_data.get('birthdate', None)
        if birthdate is not None:
            now = timezone.now()
              
            if birthdate > now:
                self.add_error('birthdate', _('Future date not posible'))
                
class UserEditForm(UserCreationForm):
    SEX_OPTIONS = (
        ('M', _('Man')),
        ('W', _('Woman')),
        ('N', _('Non-binary')),
    )
    ROL_OPTIONS = (
        ('D', 'Deportivo'),
        ('A','Aventurero'),
        ('R','Rutero'),
    )
    aux=_("Format: dd/mm/YYYY"),
  
    first_name = forms.CharField(label=_('First name'),required=False)
    last_name = forms.CharField(label=_('Last name'),required=False)
    email = forms.EmailField(label=_('Email'),required=True)
    birthdate = forms.DateField(label=_('Birthdate'),input_formats=['%d/%m/%Y'], help_text=aux, required=False)
    city = forms.CharField(label=_('City'),required=True)
    sex = forms.ChoiceField(label=_('Sex'),choices=SEX_OPTIONS, required=False)
    rol = forms.ChoiceField(label=_('Rol'),choices=ROL_OPTIONS, required=False)
    urlFoto = forms.URLField(label=_("Photo's URL"), required=False)
    password1 = forms.CharField(
        label=_("Change password"),
        strip=False,
        widget=forms.PasswordInput,
        help_text=_("Only fill if you want to change your password."),
        required=False,
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput,
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
        required=False,
    )  
  
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "birthdate", "city", "sex", "rol", "urlFoto", "password1", "password2")
      
    def save(self, commit=True):
        user = super(UserEditForm, self).save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        user.birthdate = self.cleaned_data["birthdate"]
        user.city = self.cleaned_data["city"]
        user.sex = self.cleaned_data["sex"]
        user.rol = self.cleaned_data["rol"]
        user.urlFoto = self.cleaned_data["urlFoto"]
  
        if commit:
            user.save()
        return user
  
class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()
  
    class Meta:
        model = User
        fields = ('email', 'password', 'birthdate', 'is_active')
  
    def clean_password(self):
        return self.initial["password"]
  
  
# Formulario sin el campo "captcha" necesario para crear el User desde el panel de administracion
class UserCreateFormAdmin(UserCreationForm):
    SEX_OPTIONS = (
        ('M', _('Man')),
        ('W', _('Woman')),
        ('N', _('Non-binary')),
    )
    ROL_OPTIONS = (
        ('D', 'Deportivo'),
        ('A','Aventurero'),
        ('R','Rutero'),
    )
    aux=_("Format: dd/mm/YYYY"),
  
    first_name = forms.CharField(label=_('First name'),required=False)
    last_name = forms.CharField(label=_('Last name'),required=False)
    email = forms.EmailField(label=_('Email'),required=True)
    birthdate = forms.DateField(label=_('Birthdate'),input_formats=['%d/%m/%Y'], help_text=aux, required=False)
    city = forms.CharField(label=_('City'),required=True)
    sex = forms.ChoiceField(label=_('Sex'),choices=SEX_OPTIONS, required=False)
    rol = forms.ChoiceField(label=_('Rol'),choices=ROL_OPTIONS, required=False)
    urlFoto = forms.URLField(label=_("Photo's URL"), required=False)
  
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "birthdate", "city", "sex", "rol", "urlFoto", "password1", "password2")
      
    def save(self, commit=True):
        user = super(UserCreateFormAdmin, self).save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        user.birthdate = self.cleaned_data["birthdate"]
        user.city = self.cleaned_data["city"]
        user.sex = self.cleaned_data["sex"]
        user.rol = self.cleaned_data["rol"]
        user.urlFoto = self.cleaned_data["urlFoto"]
  
        if commit:
            user.save()
        return user
  
    #  Validations  
      
    def clean(self, *args, **kwargs):
        cleaned_data = super(UserCreateFormAdmin, self).clean(*args, **kwargs)
        email = cleaned_data.get('email', None)
        if email is not None:
            users = User.objects.all()
  
            for u in users:
                if email==u.email:
                    self.add_error('email', _('Email alredy exits'))
                    break
                      
        birthdate= cleaned_data.get('birthdate', None)
        if birthdate is not None:
            now = timezone.now() 
              
            if birthdate > now:
                self.add_error('birthdate', _('Future date not posible'))
                
class SearchForm(forms.Form):
    inputData = forms.CharField(label='Busca una moto')
