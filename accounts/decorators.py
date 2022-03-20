from django.shortcuts import redirect
from django.http import HttpResponse

def unauthenticated_user(view_function):
    def wrapper_function(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        else:
            return view_function(request, *args, **kwargs)
    return wrapper_function
    
def allowed_users(allowed_roles=[]):
    def decorator(view_function):
        def wrapper(request, *args, **kwargs):
            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name
            if group in allowed_roles:
                return view_function(request, *args, **kwargs)
            else:
                return HttpResponse("%s is not authorized in this page." %request.user)
        return wrapper
    return decorator


def admin_only(view_function):
    def wrapper(request, *args, **kwargs):
        group = None
        if request.user.groups.exists():
            group = request.user.groups.all()[0].name
        if group == 'customer':
            return redirect('user_page')
        if group == 'admin':
            return view_function(request, *args, **kwargs)
    return wrapper