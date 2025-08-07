from django.urls import path
from . import views

urlpatterns = [
    path('place_order/', views.place_order, name='place_order'),
    #path('payments/', views.payments, name='payments'),
    path('buy/<int:id>/', views.buy, name='buy'),
    path('success/<int:id>/',views.success,name='success'),
    path('failure/<int:id>/',views.failure,name='failure'),

    #path('order_complete/', views.order_complete, name='order_complete'),
]
