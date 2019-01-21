from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404, render
from django.core.exceptions import ObjectDoesNotExist
 
from .serializers import UserSerializer
from django.http import HttpResponseRedirect
 
from .forms import UserCreateForm, UserEditForm
from django.contrib.auth import logout, login, update_session_auth_hash
 
from rest_framework import parsers, renderers
from .serializers import AuthTokenSerializer
from rest_framework.compat import coreapi, coreschema
from rest_framework.response import Response
from .schemas.inspectors import ManualSchema
from rest_framework.views import APIView
 
from django.contrib.auth import get_user_model
 
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import EmailMessage
from django.http import HttpResponse 
from django.contrib.auth.forms import PasswordChangeForm
from .tokens import account_activation_token
from urllib.request import HTTPRedirectHandler
 
 
User=get_user_model()

def index(request):
    return render(request, "index.html")

def Brands(request):
    return render(request, "marcas.html")
     
def Motorcycle(request):
    return render(request, "moto.html") 

def Profile(request):
    return render(request, "perfil.html") 
     
class GetUserView(APIView):
    def post(self, request):
        key = request.data.get('token', '')
        tk = get_object_or_404(Token, key=key)
        return Response(UserSerializer(tk.user, many=False).data)
 
class LogoutView(APIView):
    def post(self, request):
        key = request.data.get('token', '')
        try:
            tk = Token.objects.get(key=key)
            tk.delete()
            logout(request)
        except ObjectDoesNotExist:
            pass
 
        return Response({})
 
class ObtainAuthToken(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializer
    if coreapi is not None and coreschema is not None:
        schema = ManualSchema(
            fields=[
                coreapi.Field(
                    name="email",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="Email",
                        description="Valid email for authentication",
                    ),
                ),
                coreapi.Field(
                    name="password",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="Password",
                        description="Valid password for authentication",
                    ),
                ),
            ],
            encoding="application/json",
        )
 
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        login(request, user)
        return Response({'token': token.key})
 
class ObtainAuthTokenRRSS(APIView):  
    def get(self, request, *args, **kwarsg):
        if(((request.session.has_key('google-oauth2_state')) or 
            (request.session.has_key('github_state')) or 
            (request.session.has_key('facebook_state'))) and
            (request.session.has_key('_auth_user_id'))):
            user = User.objects.get(pk=request.session['_auth_user_id'])
            token, created = Token.objects.get_or_create(user=user)
            request.session['auth-token'] = token.key
        return HttpResponseRedirect(request.GET.get('next', '/'))
 
obtain_auth_token_rrss = ObtainAuthTokenRRSS.as_view()
 
obtain_auth_token = ObtainAuthToken.as_view()
 
def signUp(request):
    if request.method == 'POST':
        formulario = UserCreateForm(request.POST)
        if formulario.is_valid():
            user=formulario.save(commit=False)
            user.is_active = False
            user.save()
 
            # Send an email to the user with the token:
            mail_subject = 'Activate your account.'
            current_site = get_current_site(request)
            uid = urlsafe_base64_encode(force_bytes(user.pk)).decode()
            token = account_activation_token.make_token(user)
            activation_link = "http://{0}/activate/?uid={1}&token={2}".format(current_site, uid, token)
            message = "Thanks you for joining,\n You need to check this link to activate your account:\n {0} \n Best regards. \n Ganimedes team.".format(activation_link)
             
            to_email = formulario.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            return render(request, "confirm_email.html")
 
    else:
        formulario = UserCreateForm()
    return render(request, 'signup.html', {'formulario':formulario})

def edit_user(request):
    if request.method == 'POST':
        formulario = UserEditForm(request.POST, instance=request.user)
        if formulario.is_valid():
            user=formulario.save(commit=False)
            user.save()
            update_session_auth_hash(request, user)
            return render(request, 'index.html')
    else:
        formulario = UserEditForm(instance=request.user)
    return render(request, 'signup.html', {'formulario': formulario })
 
class Activate(APIView):
    def get(self, request):
        uidb64 = request.GET.get('uid')
        token = request.GET.get('token')
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            # activate user:
            user.is_active = True
            user.save()
            return render(request, "acc_active_email.html")

        else:
            return HttpResponse('Activation link is invalid!')
 
    def post(self, request):
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user) # Important, to update the session with the new password
            return HttpResponse('Password changed successfully')
             
def form_login(request):
    return render(request, 'login.html')

