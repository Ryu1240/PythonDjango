from django.shortcuts import render , get_object_or_404
from .models import Blog

# Create your views here.
def index(request):
    blogs = Blog.objects.order_by('-created_datetime')
    return render(request,'blogs/index.html',{'blogs': blogs})

def detail(request, blog_id):
    blog = get_object_or_404(Blog, id= blog_id)
    return render(request,'blogs/detail.html',{'blog': blog})