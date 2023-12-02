from .imports import *

#Store view used as homepage
def store(request):
    #Retrieve data using getData function
    context = getData(request)

    #Check if user is logged in
    if request.user.is_authenticated:
            #If so get theuser's first name
            user = request.user
            fname = user.first_name
            #Render the store with data and user's first name
            return render(request, 'store/store.html', {'fname' : fname, **context})
    else:
        #Render the store with only the data
        return render(request, 'store/store.html', context)

#Function to handle user sign-in
def signin(request):
    #Check if the method is post (sent by the login form)
    if request.method == "POST":
        #Retrieve credentials used for login
        username = request.POST['username']
        password = request.POST['password']

        #Use Django's authenticate function
        user = authenticate(username=username, password=password)
        #If authentication was successful, use the login function and redirect store
        if user is not None:
            login(request, user)
            return redirect('store')
        else:
            #User login fails, redirect to store with error message
            messages.error(request, "Bad credentials!", 'user_message')
            return redirect('store')

#Handle the user's logout
def signout (request):
    #Use Django's logout function
    logout(request)
    return redirect('store')

#Handle user's registration
def register(request):
    #Retrieve data using getData function
    context = getData(request)
    cartItems = context['cartItems']
    
    #Handle request via GET
    if request.method == "GET":
        #Redirect to store if user is logged in
        if request.user.is_authenticated:
            customer = request.user.customer
            return redirect('store')
        else:
            #Show registration page 
            return render(request, 'store/register.html', {'cartItems' : cartItems})
    
    #Handle registration process (Form is sent via POST)
    if request.method == "POST":
        #Extract user information from the form
        username = request.POST['username']
        name = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        #Check for existing username and email
        if User.objects.filter(username=username):
            messages.error(request, "Username already exists", 'user_message')
            return redirect('store')

        if User.objects.filter(email=email):
            messages.error(request, "Email already exists", 'user_message')
            return redirect('store')
        
        #Validate username length, password match, and alphanumeric username
        if len(username)>12:
            messages.error(request, "Username be smaller than 12 characters", 'user_message')
            return redirect('store')
        
        if password != password2:
            messages.error(request, "Passwords didn't match!", 'user_message')
            return redirect('store')
        
        if not username.isalnum():  
            messages.error(request, "Username must be alphanumeric", 'user_message')
            return redirect('store')

        #Create user using Django's create_user function
        myuser = User.objects.create_user(username, email, password)
        #Extract first and last name from the user's full name
        name_words = name.split()
        if len(name_words) > 0:
            myuser.first_name = name_words[0]  
            myuser.last_name = name_words[-1] 
        
        myuser.save()

        #Create a customer associated with the user
        customer, created = Customer.objects.get_or_create(user=myuser)
        customer.name = name
        customer.email = email
        customer.save()

        messages.success(request, "Your account has been successfully created!", 'user_message')

        #Welcome email
        subject = "Welcome to DAVIDUARTE'S Django project!"
        message = "Hello " + myuser.first_name + "!! \n" + "Welcome to our store! \n Thank you for visiting our store! \n We will send you the latest news and promotions we have on our website!"
        #Specify the sender and receiver emails
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        #Use the send_mail function to send the email
        send_mail(subject, message, from_email, to_list, fail_silently=True)

        return redirect('store')

def search(request):
    #Retrieve data using getData function
    context = getData(request)

    #Retrieve the search word from the query parameter
    search_str = request.GET.get("search_str", "")
    #Filter products based on the search category
    search_products = Product.objects.filter(category__iexact=search_str)
    #Replace existing 'products' in context with search results
    context['products'] = search_products
 
    if context['products']:
        #In this case the search was for a category that corresponds to the product
        context['products'] = Product.objects.filter(category__iexact=search_str)
        return render(request, 'store/search.html', context)
    #Check if there are products with names containing the search string
    elif (Product.objects.filter(name__icontains=search_str)):
        context['products'] = Product.objects.filter(name__icontains=search_str)
        return render(request, 'store/search.html', context)
    #Handle case where no products are found
    else:
        messages.error(request, "No products found.")
        return render(request, 'store/search.html', context)

#Product detailed view
def productView(request, product_name):
    #Retrieve data using getData function
    context = getData(request)

    #Get the product using the productName that is sent by html via url
    product = get_object_or_404(Product, name__iexact=product_name)

    #Render the template with the product selected in the store
    return render(request, 'store/productview.html', {'product' : product, **context})

#Cart page
def cart(request):
    #Retrieve data using getData function
    context = getData(request)

    return render(request, 'store/cart.html', context)

def checkout(request):
    #Retrieve data using getData function
    context = getData(request)
    
    return render(request, 'store/checkout.html', context)

#Handle adding or removing items in the order
def updateItem(request):
    #Retrieve the data of the html
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    #Get the value to add or remove (if it is from arrows interface, it is set to 1, else it is specified by the user)
    quantity_value = data.get('quantityValue', 1)

    print('Action:', action)
    print('Product:', productId)

    #Get the current customer
    customer = request.user.customer
    #Get the product that is beign clicked
    product = Product.objects.get(id=productId)
    #Create a new order if there isnt any, or get the current order
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    #Create a new orderItem if there isnt any, or get the current orderItem
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    #Handle adding 
    if action == 'add':
        print(quantity_value)
        #Check if the value is a valid number
        if quantity_value is not None:
            #Add the specified quantity
            orderItem.quantity = (orderItem.quantity + int(quantity_value))
        else:
            #Update by 1 (arrows interface)
            orderItem.quantity += 1
    #Handle removing
    elif action == 'remove':
        #Check if the value is a valid number
        if quantity_value is not None:
            #Subtract the specified quantity, ensuring it doesn't go below 0
            orderItem.quantity = max(0, orderItem.quantity - int(quantity_value))
        else:
            #Update by 1 (arrows interface)
            orderItem.quantity -= 1

    orderItem.save()

    #Delete the item of the order if the value reaches 0
    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)

def processOrder(request):
    # Generate a unique transaction ID using the current timestamp
    print("CREATING TRANSACTIO ID")
    transaction_id = datetime.datetime.now().timestamp()
    #Load data from the request body
    data = json.loads(request.body)

    #Check if the user is authenticated
    if request.user.is_authenticated:
        #If authenticated, associate the order with the authenticated customer
        customer = request.user.customer
        #Create order if there isn't any or get the current order
        order, created = Order.objects.get_or_create(customer = customer, complete=False)

    else:
        #If not authenticated, create a guest order using the guestOrder function
        customer, order = guestOrder(request, data)
    
    #Retrieve the total value from the form data
    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    #Check if the received total matches the cart total
    if float(total) == float(order.cartTotal):
        #If both totals match, change complete to True   
        order.complete = True

    order.save()

    #create a shipping address
    if order.shipping == True:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
                zipcode=data['shipping']['zipcode'],
            )
    
    # Create a dictionary to hold both the message and transaction_id
    response_data = {
        'message': 'Payment complete!',
        'transaction_id': str(transaction_id),  # Convert to string if needed
    }

    return JsonResponse(response_data, safe=False)

def transaction_sumary(request):

    context = getData(request)

    # Retrieve the transaction_id from the URL parameters
    transaction_id = request.GET.get('order')

    # Check if transaction_id is present
    if transaction_id:
        # Your logic to fetch order details based on transaction_id
        # For example, you might want to retrieve the Order object:
        try:
            order = Order.objects.get(transaction_id=transaction_id)
            context['order'] = order
            shippingInfo = ShippingAddress.objects.get(order=order)
            return render(request, 'store/transaction_sumary.html', {'shippingInfo': shippingInfo, **context})
        except Order.DoesNotExist:
            # Handle the case where the order is not found
            return HttpResponse("Order not found.")
    else:
        # Handle the case where transaction_id is not present in the URL
        return HttpResponse("Transaction ID is missing.")

# PayPal API Integration Views

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
                            #Total value from the cart
                            "value": total,  
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

            #print(response.text)

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
            print("first step of paypal")
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
            #print("Access Token:", access_token)

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
            print("LAST STEP OF PAYPAL")
            return self.handle_response(response)
        except Exception as e:
            print("Failed to capture order:", str(e))
            raise
