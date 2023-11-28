import json
from .models import *

def cartData(request):

    if request.user.is_authenticated:
        try:
            customer = request.user.customer
        except Customer.DoesNotExist:
            customer = Customer.objects.create(user=request.user)
        order, created = Order.objects.get_or_create(customer = customer, complete=False)
        items = order.orderitem_set.all()
        discount = DiscountProduct.objects.all()
        cartItems = order.qnt_total

    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']

    return {'items' : items, 'order' : order, 'cartItems' : cartItems}

def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}

    print('cart:', cart)
    cartItems = 0
    items = []

    order = {'cart_total' : 0, 'qnt_total' : 0, 'shipping' : False}

    for i in cart:
        try:
            cartItems += cart[i]['quantity']
            product = Product.objects.get(id=i)

            try:
                discount_product = DiscountProduct.objects.get(product=product)
            except DiscountProduct.DoesNotExist:
                discount_product = None
            if discount_product:
                total = cart[i]['quantity'] * discount_product.discount_price
            else:
                total = cart[i]['quantity'] * product.price

            order['cart_total'] += total
            order['qnt_total'] += cart[i]['quantity']

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

    name = data['form']['name']
    email = data['form']['email']

    cookieData = cookieCart(request)
    items = cookieData['items']

    customer, created = Customer.objects.get_or_create(
        email = email,
    )
    customer.name = name
    customer.save()

    order = Order.objects.create(
        customer = customer,
        complete = False,
    )

    for item in items:
        product = Product.objects.get(id=item['product']['id'])

        orderItem = OrderItem.objects.create(
            product = product,
            order = order,
            quantity = item['quantity'],
        )
    return customer, order
