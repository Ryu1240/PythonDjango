from django.shortcuts import get_object_or_404,redirect,render

# Create your views here.
def index(request):
    return render(request, 'app/index.html')