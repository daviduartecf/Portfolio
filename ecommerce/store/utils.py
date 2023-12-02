import json
from .models import *

#Retrieve the products, items, cart and order
def getData(request):
    #Call cartData function
    data = cartData(request)

    #Assign variables
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']

    #Get all products and discount products if any
    products = Product.objects.all()
    discountProducts = DiscountProduct.objects.all()

    #Return dictionary with the data
    return {'products': products, 'discount': discountProducts, 'cartItems': cartItems, 'items': items, 'order': order}

def cartData(request):

    if request.user.is_authenticated:
        try:
            #Attempt to retrieve the customer associated with the authenticated user
            customer = request.user.customer
        except Customer.DoesNotExist:
            #Create a new customer if one doesn't exist for the authenticated user
            customer = Customer.objects.create(user=request.user)

        #Retrieve or create an order for the customer
        order, created = Order.objects.get_or_create(customer = customer, complete=False)

        #Retrieve items, dicount products if any and total quantity of items in the order
        items = order.orderitem_set.all()
        discount = DiscountProduct.objects.all()
        cartItems = order.qnt_total

    else:
        #If the user is not authenticated, retrieve cart data from cookies
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']

    return {'items' : items, 'order' : order, 'cartItems' : cartItems}

#Retrieve cart-related data stored in cookies
def cookieCart(request):
    try:
        #Attempt to load the cart data from the 'cart' cookie
        cart = json.loads(request.COOKIES['cart'])
    except:
        #Set cart to an empty dictionary if the 'cart' cookie is not present or invalid
        cart = {}

    print('cart:', cart)
    #Set number of items to 0 and create empty array for items
    cartItems = 0
    items = []

    #Create new order dict
    order = {'cartTotal' : 0, 'qnt_total' : 0, 'shipping' : False}

    #Iterate through the items in the cart
    for i in cart:
        try:
            #Add the quantity of the item to cart
            cartItems += cart[i]['quantity']
            product = Product.objects.get(id=i)

            #Check if the product is in discount
            try:
                discountProduct = DiscountProduct.objects.get(product=product)
            except DiscountProduct.DoesNotExist:
                discountProduct = None
            
            #et the price based on whether the product is in discount or not
            if discountProduct:
                total = cart[i]['quantity'] * discountProduct.discount_price
            else:
                total = cart[i]['quantity'] * product.price

            #Update the total$ and the quantity total of the order
            order['cartTotal'] += total
            order['qnt_total'] += cart[i]['quantity']

            #Create item dictionay with the product atributes, quantity and value
            item = {
                'product' : {
                    'id' : product.id,
                    'name' : product.name,
                    'price' : product.price,
                    'imageURL' : product.imageURL,
                },
                'quantity' : cart[i]['quantity'],
                'get_total' : total,
            }
            #Append the item to the items array
            items.append(item)

            if product.digital == False:
                order['shipping'] = True

        except:
            pass
        
        order['qnt_total'] = cartItems
    
    return {'cartItems' : cartItems, 'order' : order, 'items' : items, 'cart' : cart}

def guestOrder(request, data):

    print('User is not logged in..')

    print('cookies:' , request.COOKIES)

    #Extract guest user information from the order form data
    name = data['form']['name']
    email = data['form']['email']

    #Retrieve items from the user's cookie cart
    cookieData = cookieCart(request)
    items = cookieData['items']

    #Create or retrieve a customer based on the provided email
    customer, created = Customer.objects.get_or_create(
        email = email,
    )
    customer.name = name
    customer.save()

    # Create a new order for the guest user
    order = Order.objects.create(
        customer = customer,
        complete = False,
    )

    #Iterate through items and create order items for the guest order
    for item in items:
        product = Product.objects.get(id=item['product']['id'])

        orderItem = OrderItem.objects.create(
            product = product,
            order = order,
            quantity = item['quantity'],
        )
    return customer, order
