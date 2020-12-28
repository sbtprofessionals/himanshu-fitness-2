from . import views
from django.urls import path
urlpatterns = [
    path('', views.index),
    path('payment', views.payment, name='payment'),
    path('purchase_membership', views.purchase_membership, name='purchase-membership')
]
