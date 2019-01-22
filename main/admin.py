from django.contrib import admin
from django.contrib.auth import get_user_model 
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from main.models import Moto, Marca

from .forms import UserCreateFormAdmin, UserChangeForm


User=get_user_model()
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreateFormAdmin
 
    SEX_OPTIONS = (
        ('M', 'Man'),
        ('W', 'Woman'),
        ('N', 'Non-binary'),
    )
    list_display = ('email', 'first_name','last_name','city','birthdate', 'sex', 'is_staff')
    list_filter = ('is_staff',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('birthdate','city','sex', 'first_name','last_name'),}),
        ('Permissions', {'fields': ('is_staff',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'birthdate','city','sex', 'first_name','last_name', 'password1', 'password2')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

admin.site.register(User, UserAdmin)
admin.site.unregister(Group)

admin.site.register(Moto)
admin.site.register(Marca)


