from . import views
from django.urls import path
urlpatterns = [
    path('', views.index, name="home"),
    path('payment', views.payment, name='payment'),
    path('purchase_membership/<int:plan_id>', views.purchase_membership, name='purchase-membership'),
    path('paytm_request_handler', views.req_handler, name='paytm-request-handler'),
    path('order_status', views.order_status, name='order-status'),
    path('contact_via_mail', views.contact_via_mail, name='contact-via-mail')
]
