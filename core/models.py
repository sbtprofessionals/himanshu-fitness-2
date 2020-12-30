from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

class MemeberShipRequest(models.Model):
    order_id = models.CharField(max_length=6, null=False, blank=False)
    name = models.CharField(max_length=20, null=False, blank=False)
    phone = PhoneNumberField(null=False, blank=False)
    email = models.EmailField(null=False, blank=False)

    def __str__(self):
        return self.order_id

class MemeberShipPayment(models.Model):
    id = models.AutoField(primary_key = True)
    order_summary = models.ForeignKey(MemeberShipRequest, on_delete = models.CASCADE)
    # paytm responses 
    currency = models.CharField(max_length=8) # INR
    gateway_name = models.CharField(max_length=25) # WALLET
    response_message = models.TextField() # Txn Success
    bank_name = models.CharField(max_length=25) # WALLET
    Payment_mode = models.CharField(max_length=25)# PPI
    # MID = models.CharField(max_length=8) # VdMxPH61970223458566
    response_code = models.CharField(max_length=3) # 01
    txn_id = models.TextField() #  20200905111212800110168406201874634
    txn_amount = models.CharField(max_length=9) #  2400.00
    order_id = models.IntegerField() #  6556
    status = models.CharField(max_length=12) # TXN_SUCCESS
    bank_txn_id = models.CharField(max_length=12) #  63209779
    txn_date = models.CharField(max_length=23) #  2020-09-05 18:51:59.0
    refund_amount = models.IntegerField(default=0.00) #  0.00
    # test = models.CharField(max_length=23)
    
    def __str__(self):
        return str(self.order_summary)
    