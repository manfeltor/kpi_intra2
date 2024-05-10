from django.shortcuts import render
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash

# Create your views here.

def login1(req):

    if req.method == 'POST':

        formulario1 = AuthenticationForm(req, data=req.POST)
        if formulario1.is_valid():
            data = formulario1.cleaned_data
            usrn = data["username"]
            psw = data["password"]
            user = authenticate(username = usrn, password = psw)
            if user:

                login(req, user)
                return render(req, "loginsuccess.html", {"msg": "1", "usr": usrn})
            else:
                
                return render(req, "loginsuccess.html", {"msg": "0"})

        else:
            
            return render(req, "loginsuccess.html", {"msg": "0"})
                
    else:

        user=req.user
        formulario1 = AuthenticationForm()

        return render(req, "login.html", {"formulario1": formulario1})
    
# def logout(req):

#     return render(req, "logout.html")