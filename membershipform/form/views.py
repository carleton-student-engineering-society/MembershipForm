from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest
import os
import requests
import msal
import uuid
import re
from .models import CarletonEmail, Membership, MembershipUpdateHistory
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import MembershipForm
from datetime import date

def index(request):
    return render(request, "index.html")

def get_membership(user) -> Membership:
    memberships = Membership.objects.filter(user=user)
    if len(memberships) == 0:
        return None
    for m in memberships:
        if not m.expired:
            return m
    return None

def is_member(user) -> bool:
    memberships = Membership.objects.filter(user=user)
    if len(memberships) == 0:
        return False
    for m in memberships:
        if not m.expired:
            return True
    return False

def has_revoked_membership(user):
    m = get_membership(user)
    if m is None:
        return False
    return m.revoked

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

@login_required
def home(request):
    return render(request, "home.html", {"member": is_member(request.user)})

def get_academic_year(today=None):
    if today is None:
        today = date.today()
    # If before May 1st, academic year is previous calendar year
    if today < date(today.year, 5, 1):
        return today.year - 1
    else:
        return today.year

@login_required
def member_signup(request):
    if has_revoked_membership(request.user):
        return HttpResponse("You cannot sign up for a membership at this time.")
    if request.method == "POST":
        form = MembershipForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            address = form.cleaned_data["address"]
            stunum = form.cleaned_data["student_number"]
            program = form.cleaned_data["program"]
            engineer = form.cleaned_data["engineer"]
            
            if not is_member(request.user):
                if not engineer:
                    return HttpResponse("Unfortunately, eng at heart's are unable to sign up for memberships")
                year = get_academic_year()
                membership = Membership(user=request.user, name=name, address=address,
                                        student_number=stunum, program=program,
                                        engineer=engineer, year=year)
            else:
                membership = get_membership(request.user)
                membership.name = name
                membership.address = address
                membership.student_number = stunum
                membership.program = program
                membership.engineer = engineer
            membership.save()
            history_change = MembershipUpdateHistory(membership=membership, change_user=request.user,
                                                     new_name=name, new_address=address,
                                                     new_student_number=stunum, new_program=program,
                                                     new_engineer=engineer, new_revoked=membership.revoked,
                                                     new_paid=membership.paid)
            history_change.save()
            return redirect("/home")
        return render(request, "signup.html", {"form": form, "invalid": True})
    else:
        if not is_member(request.user):
            form = MembershipForm(initial={"name": request.user.first_name + " " + request.user.last_name})
        else:
            m = get_membership(request.user)
            form = MembershipForm(initial={"name": m.name, "address": m.address,
                                  "student_number": m.student_number, "program": m.program,
                                  "engineer": m.engineer})
        return render(request, "signup.html", {"form": form})

@login_required
def member_history(request):
    return render(request, "history.html", {"memberships": Membership.objects.filter(user=request.user)})