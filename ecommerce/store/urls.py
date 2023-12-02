from django.urls import path
from . import views
from .views import CreateOrderView, CaptureOrderView


urlpatterns = [
	#Leave as empty string for base url
	path('', views.store, name="store"),
    path('signin', views.signin, name="signin"),
    path('signout', views.signout, name="signout"),
	path('cart/', views.cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),
	path('update_item/', views.updateItem, name="update_item"),
    path('process_order/', views.processOrder, name="process_order"),
    path('register/', views.register, name="register"),
    path('productview/<str:product_name>', views.productView, name="productview"),
    path('search/', views.search, name="search"),
    path('transaction_sumary/', views.transaction_sumary, name='transaction_sumary'),
    path('api/orders', CreateOrderView.as_view(), name='create_order'),
    path('api/orders/<str:order_id>/capture', CaptureOrderView.as_view(), name='capture_order'),
]