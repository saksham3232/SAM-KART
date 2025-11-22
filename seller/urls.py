from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('signupseller/', views.RegisterViewSeller.as_view(), name='signupseller'),
    path('signup/', views.RegisterView.as_view(), name='signup'),
    path('login/', views.LoginViewUser.as_view(), name='login'),
    path('sellerlogin/', views.SellerLoginView.as_view(), name='sellerlogin'),
    path('logout/', views.LogoutViewUser.as_view(), name='logout'),
    path('contactus/', views.ContactUs.as_view(), name='contactus'),
    path('dashboard/', views.SellerDashboardView.as_view(), name='seller-dashboard'),
    path('product/add/', views.ProductCreateView.as_view(), name='product-add'),
    path('product/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product-edit'),
    path('product/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product-delete'),

    path('orders/', views.seller_orders, name='seller-orders'),
    path('productdetail/<int:pk>/', views.ProductDetail.as_view(), name='productdetail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
