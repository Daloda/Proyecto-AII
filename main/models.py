from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from .managers import UserManager
from datetime import date
from django.utils.translation import ugettext_lazy as _


# Create your models here.
class Moto(models.Model):
    modelo = models.CharField(_('Model'),max_length=30)
    fabricante = models.CharField(_('Maker'),max_length=30)
    cilindrada = models.CharField(_('Displacement'),max_length=30)
    potencia_maxima = models.CharField(_('Maximum power'),max_length=30, blank=True)
    periodo_comercializacion = models.CharField(_('Marketing period'),max_length=30, blank=True)
    
    def __str__(self):
        return self.modelo
    
class User(AbstractBaseUser, PermissionsMixin):
    SEX_OPTIONS = (
        ('M', 'Man'),
        ('W', 'Woman'),
        ('N', 'Non-binary'),
    )
    ROL_OPTIONS = (
        ('D', 'Deportivo'),
        ('A','Aventurero'),
        ('R','Rutero'),
    )
    
    email = models.EmailField(_('Email'),unique=True)
    first_name = models.CharField(_('First name'),max_length=30, blank=True)
    last_name = models.CharField(_('Last name'),max_length=60, blank=True)
    birthdate = models.DateField(_('Birthdate'),null=True)
    city = models.CharField(_('City'),max_length=80, blank=True)
    sex = models.CharField(_('Sex'),max_length=1, choices=SEX_OPTIONS, null=True)
    rol = models.CharField(max_length=1, choices=ROL_OPTIONS, null=True)
    moto=models.ManyToManyField(Moto)
    is_active = models.BooleanField(_('Is active'),default=True)
    is_staff = models.BooleanField(_('Is staf'),default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'auth_user'
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def get_full_name(self):
        full_name = '{} {}'.format(self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def age(self):
        today = date.today()
        age = today - self.birthdate
        return age.year
    
    