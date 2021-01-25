from django.shortcuts import render

# Create your views here.
def page_not_found(request, exception):
    return render(request, '404.html')

def page_error(request):
    return render(request, '500.html')

def permission_denied(request, exception):
    return render(request, '403.html')