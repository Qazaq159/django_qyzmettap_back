from django.urls import path
from . import views

urlpatterns = [
    path('orders/', views.create_order, name='create_order'),
    path('my-orders/', views.my_orders, name='list_orders'),
    path('my-orders/<int:pk>/', views.show_order, name='show_order'),
    path('orders/<int:pk>/', views.destroy_order, name='destroy_order'),
    path('orders/<int:pk>/status/', views.UpdateOrderStatusView.as_view(), name='update_order_status'),
    path('current-order/', views.CurrentOrderView.as_view(), name='current_order'),
    path('orders/<int:pk>/reject/', views.reject_order, name='reject_order'),
]
