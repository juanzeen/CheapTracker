from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class User(models.Model):
    user_roles = {
        "ADM": "Admin",
        "SHOP": "Shopkeeper",
        "CARR": "Carrier",
    }

    role = models.CharField(max_length=4, choices=user_roles)
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField(MaxValueValidator(120))
    email = models.CharField(max_length=254)
    password_hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

class Address(models.Model):
    street = models.CharField(max_length=150)
    number = models.CharField(max_length=20)
    complement = models.CharField(max_length=100, blank=True, null=True)
    neighborhood = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    cep = models.CharField(max_length=10)
    country = models.CharField(max_length=100, default='Brasil')

class Store(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    contact = models.CharField(max_length=254)
    registration = models.CharField(max_length=128)

class Depot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    contact = models.CharField(max_length=254)
    registration = models.CharField(max_length=128)

class Carrier(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    contact = models.CharField(max_length=254)
    registration = models.CharField(max_length=128)

class Truck(models.Model):
    carrier = models.ForeignKey(Carrier, on_delete=models.CASCADE)
    plate = models.CharField(max_length=7)
    axles_count = models.IntegerField(validators=[MinValueValidator(2),MaxValueValidator(11)])
    cargo_lenght = models.FloatField(MinValueValidator(0.01))
    cargo_widht = models.FloatField(MinValueValidator(0.01))
    cargo_height = models.FloatField(MinValueValidator(0.01))
    max_payload_kg = models.FloatField(MinValueValidator(0.01))
    cargo_volume_m3 = models.FloatField(blank=True, null=True)
    euro = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(7)])
    is_active = models.BooleanField()
    release_year = models.PositiveIntegerField()
    total_trips = models.PositiveIntegerField()
    max_fuel_capacity = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        self.cargo_volume_m3 = self.cargo_lenght * self.cargo_widht * self.cargo_height
        super().save(*args, **kwargs)