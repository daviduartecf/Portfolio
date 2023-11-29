var updateBtns = document.getElementsByClassName('update-cart')

for (var i = 0; i < updateBtns.length; i++){
    updateBtns[i].addEventListener('click', function(){
        var productId = this.dataset.product
        var action = this.dataset.action
        console.log('productId:', productId, 'action:', action)

        var isAddToCartButton = document.getElementById('add-qty');

        if(isAddToCartButton) {
            var quantityValue = parseInt(document.getElementById('quantity-value').innerText);
        }
        else {
            var quantityValue = 1;
        }

        console.log('USER:', user)
        if (user == 'AnonymousUser'){
            addCookieItem(productId, action, quantityValue)
        }
        else{
            updateUserOrder(productId, action, quantityValue)
        }
        })
    }

function addCookieItem(productId, action, quantityValue) {
    console.log("Not logged");

    

    // Check if the button is the "Add to Cart" button based on its ID
    var isAddToCartButton = document.getElementById('add-qty'); // Replace 'add-to-cart-btn' with the actual ID

    if (isAddToCartButton) {
        // Special rule for the "Add to Cart" button
        if (action == 'add') {
            if (cart[productId] == undefined) {
                cart[productId] = { 'quantity': quantityValue }
            } else {
                cart[productId]['quantity'] += quantityValue;
            }
        }
    } else {
        // Standard behavior for other update-cart buttons
        if (action == 'add') {
            if (cart[productId] == undefined) {
                cart[productId] = { 'quantity': 1 }
            } else {
                cart[productId]['quantity'] += 1;
            }
        }
    }

    if (action == 'remove') {
        cart[productId]['quantity'] -= quantityValue;

        if (cart[productId]['quantity'] <= 0) {
            console.log("remove item");
            delete cart[productId];
        }
    }

    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/";

    console.log('Cart:', cart);
    location.reload();
}

function updateUserOrder(productId, action, quantityValue){
    console.log('User is authenticated, sending data...')

    var url = '/update_item/'

    fetch(url, {
        method:'POST',
        headers:{
            'Content-Type':'application/json',
            'X-CSRFToken': csrftoken,
        },
        body:JSON.stringify({'productId' : productId, 'action' : action, 'quantityValue': quantityValue})
    })

    .then((response) =>{
        return response.json()
    })

    .then((data) =>{
        console.log('data:', data)
        location.reload()
    })
}