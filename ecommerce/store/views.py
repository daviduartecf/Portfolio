from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import *
from django.http import JsonResponse
import json
import datetime
from .utils import cookieCart, cartData, guestOrder
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.conf import settings
import requests
import base64
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.core.mail import send_mail


# Create your views here.
def store(request):
    
    data = cartData(request)

    items = data['items']
    order = data['order']
    cartItems = data['cartItems']

    products = Product.objects.all()
    discount_products = DiscountProduct.objects.all()
    context = {'products' : products, 'discount' : discount_products, 'cartItems' : cartItems}

    if request.user.is_authenticated:
            user = request.user
            fname = user.first_name
            return render(request, 'store/store.html', {'fname' : fname, 'products' : products, 'discount' : discount_products, 'cartItems' : cartItems})
    else:
        return render(request, 'store/store.html', context)

def signin(request):

    data = cartData(request)

    items = data['items']
    order = data['order']
    cartItems = data['cartItems']

    products = Product.objects.all()
    discount_products = DiscountProduct.objects.all()

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('store')
        else:
            messages.error(request, "Bad credentials!")
            return redirect('store')
        
def signout (request):
    logout(request)
    return redirect('store')

def register(request):

    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']

    products = Product.objects.all()
    discount_products = DiscountProduct.objects.all()
    
    if request.method == "GET":
        if request.user.is_authenticated:
            customer = request.user.customer
            return redirect('store')
        else:
            return render(request, 'store/register.html', {'cartItems' : cartItems})
    
    
    if request.method == "POST":
        username = request.POST['username']
        name = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if User.objects.filter(username=username):
            messages.error(request, "Username already exists")
            return redirect('store')

        if User.objects.filter(email=email):
            messages.error(request, "Email already exists")
            return redirect('store')
        
        if len(username)>12:
            messages.error(request, "Username be smaller than 12 characters")
            return redirect('store')
        
        if password != password2:
            messages.error(request, "Passwords didn't match!")
            return redirect('store')
        
        if not username.isalnum():
            messages.error(request, "Username must be alphanumeric")
            return redirect('store')


        myuser = User.objects.create_user(username, email, password)
        name_words = name.split()

        if len(name_words) > 0:
            myuser.first_name = name_words[0]  
            myuser.last_name = name_words[-1] 
        
        myuser.save()

        customer, created = Customer.objects.get_or_create(user=myuser)
        customer.name = name
        customer.email = email
        customer.save()

        #messages.success(request, "Your account has been successfully created!")

        #Welcome email

        subject = "Welcome to DAVIDUARTE'S Django project!"
        message = "Hello " + myuser.first_name + "!! \n" + "Welcome to our store! \n Thank you for visiting our store! \n We will send you the latest news and promotions we have on our website!"
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)

        return redirect('store')
    
def search(request):

    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']
    discount_products = DiscountProduct.objects.all()


    search_str = request.GET.get("search_str", "")
    products = Product.objects.filter(category__iexact=search_str)
    print(products)

    if products:
        products = Product.objects.filter(category__iexact=search_str)
        context = {'products' : products, 'cartItems' : cartItems, 'discount' : discount_products}
        return render(request, 'store/search.html', context)
    elif (Product.objects.filter(name__icontains=search_str)):
        products = Product.objects.filter(name__icontains=search_str)
        context = {'products' : products, 'cartItems' : cartItems, 'discount' : discount_products}
        return render(request, 'store/search.html', context)
    else:
        messages.error(request, "No products found.")
        context = {'cartItems' : cartItems, 'discount' : discount_products}
        return render(request, 'store/search.html', context)

def productView(request, product_name):
    
    data = cartData(request)

    items = data['items']
    order = data['order']
    cartItems = data['cartItems']

    discount_products = DiscountProduct.objects.all()
    

    product = get_object_or_404(Product, name__iexact=product_name)
    order_item = OrderItem.objects.filter(product=product)

    context = {'product' : product, 'cartItems' : cartItems, 'discount' : discount_products, 'order_item' : order_item}
    # Render the product information in your template
    return render(request, 'store/productview.html', context)

def cart(request):

    data = cartData(request)

    items = data['items']
    order = data['order']
    cartItems = data['cartItems']

    context = {'items' : items, 'order' : order, 'cartItems' : cartItems, 'cart' : cart}
    return render(request, 'store/cart.html', context)

def checkout(request):

    data = cartData(request)

    items = data['items']
    order = data['order']
    cartItems = data['cartItems']

    context = {'items' : items, 'order' : order, 'cartItems' : cartItems}
    return render(request, 'store/checkout.html', context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    quantity_value = data.get('quantityValue', 1)

    print('Action:', action)
    print('Product:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        print(quantity_value)
        if quantity_value is not None:
            orderItem.quantity = (orderItem.quantity + int(quantity_value))
        else:
            orderItem.quantity += 1
    elif action == 'remove':
        if quantity_value is not None:
            orderItem.quantity = max(0, orderItem.quantity - int(quantity_value))
        else:
            orderItem.quantity -= 1

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer = customer, complete=False)

    else:
        customer, order = guestOrder(request, data)
    
    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if float(total) == float(order.cart_total):   
        order.complete = True
    order.save()

    if order.shipping == True:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
                zipcode=data['shipping']['zipcode'],
            )
    
    return JsonResponse('Payment complete!', safe=False)

# Define constants
BASE_URL = "https://api-m.sandbox.paypal.com"

class CreateOrderView(View):
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve cart information from the request body
            data = json.loads(request.body)
            print(data)
            total = float(data['total'])
            
            # Call the create_order function
            response = self.create_order(total)
            
            # Return the JSON response from the PayPal API
            return JsonResponse(response['jsonResponse'], status=response['httpStatusCode'])
        except Exception as e:
            print("Failed to create order:", str(e))
            return JsonResponse({'error': 'Failed to create order.'}, status=500)

    def create_order(self, total):
        try:
            # Generate an OAuth 2.0 access token
            access_token = self.generate_access_token()
            print("Access Token:", access_token)
            
            # Define the PayPal API endpoint for creating orders
            url = f"{BASE_URL}/v2/checkout/orders"
            
            # Define the payload for creating an order
            payload = {
                "intent": "CAPTURE",
                "purchase_units": [
                    {
                        "amount": {
                            "currency_code": "USD",
                            "value": total,  # Update with the calculated value from the cart
                        },
                    },
                ],
            }
            
            # Make a POST request to create the order
            response = requests.post(
                url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}",
                },
                json=payload,
            )

            print(response.text)

            # Check if the request was successful
            response.raise_for_status()

            order_id = response.json().get("id")

            # Return the response
            return self.handle_response(response)
        except requests.exceptions.RequestException as e:
            print("Failed to create order:", str(e))
            raise

    def generate_access_token(self):
        try:
            # Retrieve PayPal client ID and secret from Django settings
            client_id = settings.PAYPAL_CLIENT_ID
            client_secret = settings.PAYPAL_CLIENT_SECRET

            # Check if client ID and secret are available
            if not client_id or not client_secret:
                raise Exception("MISSING_API_CREDENTIALS")

            # Encode client ID and secret for Basic Authentication
            auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

            auth_header = f"Basic {auth}"


            # Make a POST request to retrieve the access token
            response = requests.post(
                f"{BASE_URL}/v1/oauth2/token",
                headers={
                    "Authorization": auth_header,
                },
                data={"grant_type": "client_credentials"},
            )

            # Check if the request was successful
            response.raise_for_status()

            # Parse and return the access token from the response
            data = response.json()
            return data.get("access_token")
        except requests.HTTPError as e:
            print("Failed to generate Access Token:", e.response.text)
            raise
        except Exception as e:
            print("Failed to generate Access Token:", str(e))
            raise

    def handle_response(self, response):
        try:
            # Parse JSON response or raise an exception with the error message
            json_response = response.json()
            return {
                "jsonResponse": json_response,
                "httpStatusCode": response.status_code,
            }
        except Exception as e:
            # If parsing JSON fails, raise an exception with the error message from the response
            error_message = response.text
            raise Exception(error_message)

class CaptureOrderView(View):
    @csrf_exempt
    def post(self, request, order_id, *args, **kwargs):
        try:
            # Generate an OAuth 2.0 access token
            access_token = self.generate_access_token()
            print("Access Token:", access_token)

            # Call the capture_order function
            response = self.capture_order(order_id, access_token)
            
            # Return the JSON response from the PayPal API
            return JsonResponse(response['jsonResponse'], status=response['httpStatusCode'])
        except Exception as e:
            print("Failed to capture order:", str(e))
            return JsonResponse({'error': 'Failed to capture order.'}, status=500)
    
    def generate_access_token(self):
        try:
            # Retrieve PayPal client ID and secret from Django settings
            client_id = settings.PAYPAL_CLIENT_ID
            client_secret = settings.PAYPAL_CLIENT_SECRET

            # Check if client ID and secret are available
            if not client_id or not client_secret:
                raise Exception("MISSING_API_CREDENTIALS")

            # Encode client ID and secret for Basic Authentication
            auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

            auth_header = f"Basic {auth}"


            # Make a POST request to retrieve the access token
            response = requests.post(
                f"{BASE_URL}/v1/oauth2/token",
                headers={
                    "Authorization": auth_header,
                },
                data={"grant_type": "client_credentials"},
            )

            # Check if the request was successful
            response.raise_for_status()

            # Parse and return the access token from the response
            data = response.json()
            return data.get("access_token")
        except requests.HTTPError as e:
            print("Failed to generate Access Token:", e.response.text)
            raise
        except Exception as e:
            print("Failed to generate Access Token:", str(e))
            raise

    def handle_response(self, response):
        try:
            # Parse JSON response or raise an exception with the error message
            json_response = response.json()
            return {
                "jsonResponse": json_response,
                "httpStatusCode": response.status_code,
            }
        except Exception as e:
            # If parsing JSON fails, raise an exception with the error message from the response
            error_message = response.text
            raise Exception(error_message)

    def capture_order(self, order_id, access_token):
        try:
            # Define the PayPal API endpoint for capturing orders
            url = f"{BASE_URL}/v2/checkout/orders/{order_id}/capture"
            
            # Make a POST request to capture the order
            response = requests.post(
                url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}",
                },
            )

            # Return the response
            return self.handle_response(response)
        except Exception as e:
            print("Failed to capture order:", str(e))
            raise
