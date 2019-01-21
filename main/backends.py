from django.contrib.auth.backends import ModelBackend
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class AuthBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        try:
            user = UserModel._default_manager.get_by_natural_key(username)
        except UserModel.DoesNotExist:
            UserModel().set_password(password)
        else:
            is_active = getattr(user, 'is_active', None)
            if user.check_password(password) and is_active:
                token, created = Token.objects.get_or_create(user=user)
                token=token.key
                request.session.flush()
                request.session['auth-token'] = token
                return user