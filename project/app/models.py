from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import BaseUserManager, PermissionsMixin, AbstractBaseUser

class UserRoles(models.TextChoices):
    MAN = 'Man', 'Manager'
    SHOP = 'Shop', 'Shopkeeper'
    CARR = 'Carr', 'Carrier'
    ADM = 'Adm', 'Administrator'


class Manager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', UserRoles.ADM)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have staff permission!')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have superuser permission!')


        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    role = models.CharField(max_length=4, choices=UserRoles.choices)
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField(MaxValueValidator(120))
    email = models.CharField(max_length=254, unique=True)
    #password_hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    is_staff = models.BooleanField(
        default=False,
        help_text='Gives to user access to admin field.'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Indicates if user is active or no.'
    )

    objects = Manager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['role', 'name', 'age']

    def __str__(self):
        return self.email

    # def save(self, *args, **kwargs):
    #     if self.role not in [choice[0] for choice in UserRoles.choices]:
    #         raise ValueError(f'Invalid Role: {self.role}')

    #     if not self.password_hash.startswith('pbkdf2_'):
    #         self.password_hash = make_password(self.password_hash)

    #     super().save(*args, **kwargs)

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
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    contact = models.CharField(max_length=254)
    registration = models.CharField(max_length=128)

class Depot(models.Model):
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    contact = models.CharField(max_length=254)
    registration = models.CharField(max_length=128)

class Carrier(models.Model):
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    contact = models.CharField(max_length=254)
    registration = models.CharField(max_length=128)

class Truck(models.Model):
    carrier = models.ForeignKey(Carrier, on_delete=models.CASCADE)
    plate = models.CharField(max_length=7, unique=True)
    axles_count = models.IntegerField(validators=[MinValueValidator(2),MaxValueValidator(11)])
    cargo_length = models.FloatField(MinValueValidator(0.01))
    cargo_width = models.FloatField(MinValueValidator(0.01))
    cargo_height = models.FloatField(MinValueValidator(0.01))
    max_payload_kg = models.FloatField(MinValueValidator(0.01))
    cargo_volume_m3 = models.FloatField(blank=True, null=True)
    euro = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(7)])
    is_active = models.BooleanField()
    release_year = models.PositiveIntegerField()
    total_trips = models.PositiveIntegerField()
    max_fuel_capacity = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        self.cargo_volume_m3 = self.cargo_length * self.cargo_width * self.cargo_height
        super().save(*args, **kwargs)

class TripStatus(models.TextChoices):
    PLANN = 'Plan', 'Planned'
    IN_TR = 'InTr', 'In_Transit'
    COMP = 'Comp', 'Completed'
    CANC = 'Canc', 'Cancelled'

class Trip(models.Model):
    truck = models.ForeignKey(Truck, on_delete=models.SET_NULL, null=True)
    origin_depot = models.ForeignKey(Depot, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    departure_date = models.DateTimeField(null=True)
    arrival_date = models.DateTimeField(null=True)
    total_loaded_weight_kg = models.FloatField(MinValueValidator(0.01))
    total_loaded_volume_m3 = models.FloatField(MinValueValidator(0.01))
    total_distance_km = models.FloatField()
    carbon_kg_co2 = models.FloatField(null=True)
    status = models.CharField(max_length=4, choices=TripStatus.choices)

    def save(self, *args, **kwargs):
        if self.status not in [choice[0] for choice in TripStatus.choices]:
            raise ValueError(f'Invalid Status: {self.status}')

        super().save(*args, **kwargs)


class OrderStatus(models.TextChoices):
    PEND = 'Pend', 'Pending'
    SCHE = 'Sche', 'Scheduled'
    SHIP = 'Ship', 'Shipped'
    DELI = 'Deli', 'Delivered'
    CANC = 'Canc', 'Cancelled'

class Order(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=4, choices=OrderStatus.choices)
    total_weight_kg = models.FloatField(MinValueValidator(0.0))
    total_volume_m3 = models.FloatField(MinValueValidator(0.0))
    total_boxes = models.PositiveIntegerField()
    scheduled = models.BooleanField()

    def save(self, *args, **kwargs):
        if self.status not in [choice[0] for choice in OrderStatus.choices]:
            raise ValueError(f'Invalid Status: {self.status}')

        super().save(*args, **kwargs)

class Delivery(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    delivered_at = models.DateTimeField(null=True)

class BoxSize(models.TextChoices):
    SMA = 'Sma', 'Small'
    MED = 'Med', 'Medium'
    BIG = 'Big', 'Big'
    LAR = 'Lar', 'Large'
    CUS = 'Cus', 'Custom'

class Box(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    size = models.CharField(max_length=3, choices=BoxSize.choices)
    length = models.FloatField(MinValueValidator(0.01))
    width = models.FloatField(MinValueValidator(0.01))
    height = models.FloatField(MinValueValidator(0.01))
    payload_kg = models.FloatField(MinValueValidator(0.01))
    volume_m3 = models.FloatField(blank=True, null=True)
    was_delivered = models.BooleanField()

    def save(self, *args, **kwargs):
        self.volume_m3 = self.length * self.width * self.height

        if self.size not in [choice[0] for choice in BoxSize.choices]:
            raise ValueError(f'Invalid Size: {self.size}')

        super().save(*args, **kwargs)
