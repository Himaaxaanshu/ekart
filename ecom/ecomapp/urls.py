from django.urls import path
from ecomapp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('register', views.register),
    path('login',views.user_login),
    path('home',views.home),
    path('prod_details<prod_id>', views.product_details),
    path('cart<prod_id>', views.cart),
    path('viewcart',views.viewcart),
    path('updateqty<x><cid>',views.updateqty),
    path('remove<cid>',views.remove),
    path('order<oid>',views.remove_order),
    path('placeorder',views.placeorder),
    path('fetchorder',views.fetchorder),
    path('makepayment',views.makepayment),
    path('paymentsuccess',views.paymentsuccess),
    path('catfilter<cv>', views.catfilter),
    path('search',views.search),
    path('logout',views.user_logout),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)