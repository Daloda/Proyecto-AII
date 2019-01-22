from django.contrib.auth import get_user_model
from django.contrib.auth import logout, login, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage
from django.http import HttpResponse 
from django.http import HttpResponseRedirect
 
from .forms import UserCreateForm, UserEditForm, SearchForm

from django.shortcuts import get_object_or_404, render
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from rest_framework import parsers, renderers
from rest_framework.authtoken.models import Token
from rest_framework.compat import coreapi, coreschema
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from main.models import Marca, Moto, User, Rating
from main import models

from .schemas.inspectors import ManualSchema
from .serializers import AuthTokenSerializer
from .serializers import UserSerializer
from .tokens import account_activation_token
from .mods import post

from whoosh.index import open_dir
from whoosh.qparser import MultifieldParser
from whoosh import qparser
from AII2Project.settings import INDEX_PATH

import shelve
from main.recommendations import getRecommendedItems


def index(request):
    return render(request, "index.html")


def Brands(request):
    if request.method=='GET':
        form = SearchForm(request.GET, request.FILES)
        if form.is_valid():
            inputData = form.cleaned_data['inputData']
            ix=open_dir(INDEX_PATH)
            with ix.searcher() as searcher:
                query = MultifieldParser(["modelo","marcaNombre"], ix.schema, group = qparser.AndGroup).parse(str(inputData))
                results = searcher.search(query, limit=None)
                return render(request, "modelos.html", {"form": form, "modelos": results})

    marcas = Marca.objects.all()
    form=SearchForm()
    return render(request, "marcas.html", {"form": form, "marcas": marcas})

     
def Models(request, nombreMarcaURL):
    if request.method=='GET':
        form = SearchForm(request.GET, request.FILES)
        if form.is_valid():
            inputData = form.cleaned_data['inputData']
            ix=open_dir(INDEX_PATH)
            with ix.searcher() as searcher:
                query = MultifieldParser(["modelo","marcaNombre"], ix.schema, group = qparser.AndGroup).parse(str(inputData))
                results = searcher.search(query, limit=None)
                modelos = []
                for result in results:
                    if (str(result.get("marcaNombre")) == str(nombreMarcaURL)):
                        modelos.append(result)
                return render(request, "modelos.html", {"form": form, "modelos": modelos})
            
    modelos = []
    modelosTotales = Moto.objects.all()
    for moto in modelosTotales:
        if (str(moto.marcaNombre) == str(nombreMarcaURL)):
            modelos.append(moto)
            
    form=SearchForm()     
    return render(request, 'modelos.html', {"form": form,'modelos':modelos})


def Motorcycle(request,idMoto):
    motoSalida = None
    modelosTotales = Moto.objects.all()
    for moto in modelosTotales:
        if (str(moto.id) == str(idMoto)):
            motoSalida = moto            
    return render(request, 'moto.html', {'moto': motoSalida})


def Profile(request):
    return render(request, "perfil.html") 

def Users(request):
    usuarios = User.objects.all()
    return render(request, "usuarios.html", {"usuarios": usuarios})

def Ratings(request, motoId, value):
    if (request.session.has_key('_auth_user_id')):
        uid = request.session.get('_auth_user_id')
        token = request.session.get('auth-token')
        user = post(entry_point='/getuser/', json={'token': token})
        user_id = user.get('id', None)
        if not user_id or str(user_id) != str(uid):
            return Response(
                {"message": "voter id is not authorized"},
                status=status.HTTP_401_UNAUTHORIZED)
        else:
            userRat = models.User.objects.get(pk=user_id)
            mot = Moto.objects.get(pk=motoId)
            rat = Rating(usuario=userRat, moto=mot, rating=int(value))
            rat.save()
    return render(request, "moto.html", {'moto': mot})


def recommendedMotos(request):
    if (request.session.has_key('_auth_user_id')):
        idUser = request.session.get('_auth_user_id')
#         user = models.User.objects.get(pk=idUser)
        shelf = shelve.open("dataRS.dat")
        Prefs = shelf['Prefs']
        SimItems = shelf['SimItems']
        shelf.close()
        rankings = getRecommendedItems(Prefs, SimItems, int(idUser))
        recommended = rankings[:3]
        items = []
        for re in recommended:
            item = Moto.objects.get(pk=re[1])
            items.append(item)
        return render(request,'modelos.html', {'modelos': items, 'recommend': True})
    else:
        return render(request, "index.html")


User=get_user_model()

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
            user = formulario.save(commit=False)
            user.is_active = False
            user.save()
 
            # Send an email to the user with the token:
            mail_subject = 'Activate your account.'
            current_site = get_current_site(request)
            uid = urlsafe_base64_encode(force_bytes(user.pk)).decode()
            token = account_activation_token.make_token(user)
            activation_link = "http://{0}/activate/?uid={1}&token={2}".format(current_site, uid, token)
            message = "Thanks you for joining,\n You need to check this link to activate your account:\n {0} \n Best regards. \n Group 2 team.".format(activation_link)
             
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
            user = formulario.save(commit=False)
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
            update_session_auth_hash(request, user)  # Important, to update the session with the new password
            return HttpResponse('Password changed successfully')

             
def form_login(request):
    return render(request, 'login.html')

