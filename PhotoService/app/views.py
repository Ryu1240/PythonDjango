from django.shortcuts import get_object_or_404,redirect,render
from django.contrib.auth.models import User
from .models import Photo

# Create your views here.
def index(request):
    photos = Photo.objects.all().order_by('-created_at')
    return render(request, 'app/index.html', { 'photos' : photos})

def users_detail(request, pk):
    user = get_object_or_404(User, pk =pk)
    return render(request, 'app/users_detail.html', {'user': user})