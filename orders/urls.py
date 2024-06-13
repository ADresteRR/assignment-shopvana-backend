from django.urls import path
from . import views

urlpatterns = [
    path("get-user-id", views.generate_temporary_user_id, name="get_user_id"),
    path("add-product", views.add_product, name="add_product"),
    path('get-all-products', views.get_all_products, name="get_all_products"),
    path('get-all-options', views.get_all_options, name="get-all-options"),
    path("add-option-list", views.add_option_list, name="add-option-list"),
    path("add-options", views.add_option, name="add_option"),
    path("add-to-cart", views.add_to_cart, name="add_to_cart"),
    path("remove-from-cart", views.remove_from_cart, name="remove_from_cart"),
    path("get-cart-items/<str:temporary_user_id>", views.get_cart_items, name="get_cart_items"),
]