from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

class MemeberShipRequest(models.Model):
    name = models.CharField(max_length=20)
    phone = PhoneNumberField()
    email = models.EmailField()

    def __str__(self):
        return self.name
    