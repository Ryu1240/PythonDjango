from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login
from .forms import CustomUserCreationForm
from .models import Product, Sale
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages 
from .forms import AddToCartForm , PurchaseForm
import json
import requests

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

@login_required
def cart(request):
    # セッションから'cart'キーに対応する辞書を取得する。
    # セッションに'cart'キーが存在しない場合は{}(空の辞書)がcart変数に代入される。
    user = request.user
    cart = request.session.get('cart',{})

    # cart_products → Productオブジェクトをキー、購入個数を値として持つ辞書
    # {初期値は空の辞書}
    cart_products = {}
    # total_price → カートない商品の合計金額を表す変数(初期値は0)
    total_price = 0

    # car_productsとtotal_priceを更新する
    for product_id, num in cart.items():
        product = Product.objects.filter(id=product_id).first()
        if product is None:
            continue
        cart_products[product] = num
        total_price += product.price * num
        
    if request.method == 'POST':
        purchase_form = PurchaseForm(request.POST)
        if purchase_form.is_valid():
            # 住所検索ボタンが押された時
            if 'search_address' in request.POST:
                zip_code = request.POST['zip_code']
                address = fetch_address(zip_code)
                # 住所が取得できなかった場合はメッセージを出してリダイレクト
                if not address:
                    messages.warning(request, "住所を取得できませんでした")
                    return redirect('app:cart')
                # 住所が取得できたらフォームの値として入力
                purchase_form = PurchaseForm(
                    initial={'zip_code': zip_code, 'address': address}
                )
            # 購入処理ボタンが押された婆
            if 'buy_product' in request.POST:
                # 住所が入力済みかを確認する。未入力の場合はリダイレクトする
                if not purchase_form.cleaned_data['address']:
                    messages.warning(request, "住所の入力は必須です。")
                    return redirect('app:cart')
                # カートが空じゃないかを確認する。からの場合はリダイレクトする
                if not cart:
                    messages.warning(request, "カートは空です。")
                    return redirect('aoo:cart')
                if total_price > user.point:
                    messages.warning(request, "所持ポイントが足りません。")
                    return redirect('app:cart')
                
                # 各プロダクトのSale情報を保存（売上記録の登録）
                for product, num in cart_products.items():
                    sale = Sale(
                        product=product,
                        user=request.user,
                        amount=num,
                        price=product.price,
                        total_price=num * product.price,
                    )
                    sale.save()
                # 購入した分だけユーザの保有ポイントを減らす
                user.point -= total_price
                user.save()
                
                # セッションから'cart'を削除してカートを空にする
                del request.session['cart']
                messages.success(request, "商品の購入が完了しました！")
                return redirect('app:cart')
    else:
        purchase_form = PurchaseForm()
    context = {
        'purchase_form': purchase_form,
        'cart_products': cart_products,
        'total_price' : total_price,
    }
    return render(request, 'app/cart.html', context)

@login_required
@require_POST
def change_product_amount(request):
    # name="product_id"のフィールドの値を取得（どの商品を増減させるか）
    product_id = request.POST["product_id"]
    # セッションから"cart"情報を取得
    cart_session = request.session['cart']
    
    # セッションの更新
    if product_id in cart_session:
        # 1つ減らすボタンを押された時
        if "action_remove" in request.POST:
            cart_session[product_id] -= 1
        if "action_add" in request.POST:
            cart_session[product_id] += 1
        if cart_session[product_id] <= 0:
            del cart_session[product_id]
    return redirect('app:cart')

def fetch_address(zip_code):
    
    REQUEST_URL = f'http://zipcloud.ibsnet.co.jp/api/search?zipcode={zip_code}'
    response = requests.get(REQUEST_URL)
    response = json.loads(response.text)
    results, api_status = response['results'], response['status']
    
    address = ""
    
    if api_status == 200 and results is not None:
        result = results[0]
        address = result['address1'] + result['address2'] + result['address3']
    return address