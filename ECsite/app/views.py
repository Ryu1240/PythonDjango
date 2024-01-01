from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login
from .forms import CustomUserCreationForm
from .models import Product
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages 
from .forms import AddToCartForm 

# Create your views here.
def index(request):
    products = Product.objects.all().order_by('-id')
    return render(request, 'app/index.html', {'products':products})

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            input_email = form.cleaned_data['email']
            input_password = form.cleaned_data['password1']
            new_user = authenticate(
                email=input_email,
                password=input_password,
            )
            if new_user is not None:
                login(request, new_user)
                return redirect('app:index')
    else:
        form = CustomUserCreationForm()
    return render(request, 'app/signup.html', {'form':form})

def detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    
    if request.method == "POST":
        add_to_cart_form = AddToCartForm(request.POST)
        if add_to_cart_form.is_valid():
            num = add_to_cart_form.cleaned_data['num']
            if 'cart' in request.session:
                if str(product_id) in request.session['cart']:
                    request.session['cart'][str(product_id)] += num
                else:
                    request.session['cart'][str(product_id)] = num
            else:
                request.session['cart'] = {str(product_id): num}
            messages.success(request, f"{product.name}を{num}個カート入れました!") 
            return redirect('app:detail', product_id=product_id)
        
    add_to_cart_form = AddToCartForm()
    context = {
        'product': product,
        'add_to_cart_form': add_to_cart_form,
    }
    return render(request, 'app/detail.html', context)

@login_required
@require_POST
def toggle_fav_product_status(request):
    product = get_object_or_404(Product, pk=request.POST["product_id"])
    user = request.user
    
    if product in user.fav_products.all(): 
        user.fav_products.remove(product)
    else:
        user.fav_products.add(product)
    return redirect('app:detail', product_id=product.id)

@login_required
def fav_products(request):
    user = request.user
    products = user.fav_products.all()
    return render(request, 'app/index.html', {'products': products})