from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest
import os
import requests
import msal
import uuid
import re
from .models import CarletonEmail
from django.contrib.auth.models import User
from django.contrib.auth import login


def index(request):
    return render(request, "index.html")

def signin(request):
    if request.user.is_authenticated:
        return redirect("/home")
    AUTHORITY = "https://login.microsoftonline.com/common"
    app = msal.ConfidentialClientApplication(os.environ.get("MSAL_CLIENTID"), authority=AUTHORITY,
                                             client_credential=os.environ.get("MSAL_SECRET"))
    SCOPE = ["User.Read"]
    url = app.get_authorization_request_url(SCOPE, state=str(uuid.uuid4()), redirect_uri=request.build_absolute_uri("/callback"))
    return redirect(url)

def callback(request):
    params = request.GET
    if 'code' not in params or 'state' not in params or 'session_state' not in params:
        return HttpResponseBadRequest("Missing code and session state! " +
                                      "You probably are signed in using your personal Microsoft account. "
                                      "Clear your cookies and if the issue persists contact technical@cses.carleton.ca")
    code = params['code']
    # state = params['state']
    # session_state = params['session_state']
    AUTHORITY = "https://login.microsoftonline.com/common"
    app = msal.ConfidentialClientApplication(os.environ.get("MSAL_CLIENTID"), authority=AUTHORITY,
                                             client_credential=os.environ.get("MSAL_SECRET"))
    SCOPE = ["User.Read"]
    token = app.acquire_token_by_authorization_code(code, SCOPE, redirect_uri=request.build_absolute_uri("/callback"))
    access_token = token["access_token"]
    user = requests.get("https://graph.microsoft.com/v1.0/me", headers={"Authorization": "Bearer " + access_token}).json()
    email = user["userPrincipalName"]
    first_name = user["givenName"]
    last_name = user["surname"]
    user = User.objects.filter(email=email).first()
    if user != None:
        cmail = CarletonEmail.objects.get(user=user)
        cmail.access_token = access_token
        cmail.refresh_token = token['refresh_token']
        cmail.save()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect("/home")

    username = re.sub(r'[^a-zA-Z0-9\-\s]', '', (first_name + "-" + last_name))
    user = User.objects.create_user(username, email, first_name=first_name, last_name=last_name)
    user.save()
    cmail = CarletonEmail.objects.create(user=user, access_token=access_token, refresh_token=token["refresh_token"])
    cmail.save()
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    return redirect("/home")
def home(request):
    pass