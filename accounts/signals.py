from django.db.models.signals import post_save
from .models import Customer
from django.contrib.auth.models import Group
from django.contrib.auth.models import User


def create_customer(sender, instance, created, **kwargs):
    if created:
        Customer.objects.create(
            user = instance,
            name = instance.username,
            email = instance.email
        )
        group = Group.objects.get(name='customer')
        instance.groups.add(group)
        print("Customer is created after user registration.")

post_save.connect(create_customer, sender=User)