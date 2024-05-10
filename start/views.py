from django.shortcuts import render

# Create your views here.

def base(req):

    if req.user.groups.filter(name='management').exists():

        return render(req, "landing_management.html")
    
    else:
        
        return render(req, "landing.html")


def construccion(req):
    
    return render(req, "construction.html")