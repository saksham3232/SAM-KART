from django.db import models

from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager
from django.core.validators import RegexValidator
from django.db.models import Q
# Create your models here.


from django.contrib.auth.models import AbstractUser, AbstractBaseUser
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.models import PermissionsMixin


from .managers import CustomUserManager

from multiselectfield import MultiSelectField


# class UserType(models.Model):
#     CUSTOMER=1
#     SELLER=2
#     TYPE_CHOICES = (
#         (SELLER, 'Seller'),
#         (CUSTOMER, 'Customer'),
#     )
#     id = models.PositiveSmallIntegerField(choices=TYPE_CHOICES, primary_key=True)

#     def __str__(self):
#         return self.get_id_display()


class LowerCaseEmailField(models.EmailField):
    def to_python(self, value):
        """Convert the value to lowercase before saving it to the database."""
        value = super(LowerCaseEmailField, self).to_python(value)
        if isinstance(value, str):
            return value.lower()
        return value



class CustomUser(AbstractBaseUser, PermissionsMixin):
    # username = None
    email = LowerCaseEmailField(_('email address'), unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    # if you require phone number field in your project
    phone_regex = RegexValidator( regex = r'^\d{10}$',message = "phone number should exactly be in 10 digits")
    phone = models.CharField(max_length=255, validators=[phone_regex], blank = True, null=True)  # you can set it unique = True

    # 1
    # is_customer = models.BooleanField(default=True)
    # is_seller = models.BooleanField(default=False)

    # 2.1
    # type = (
    #     (1, 'Seller'),
    #     (2, 'Customer'),
    # )
    # user_type = models.IntegerField(choices=type, default=2)

    # 2.2
    # choices = (
    #     (1, 'Seller'),
    #     (2, 'Customer'),
    # )
    # user_type = MultiSelectField(choices=choices, default=[2], max_length=20, min_count=1, max_count=2)

    # usertype = models.ManyToManyField(UserType)

    class Types(models.TextChoices):
        SELLER = "Seller", "SELLER"
        CUSTOMER = "Customer", "CUSTOMER"

    # Types = (
    #     (1, 'SELLER'),
    #     (2, 'CUSTOMER')
    # )
    # type = models.IntegerField(choices=Types, default=2)

    default_type = Types.CUSTOMER

    # type = models.CharField(_('Type'), max_length=255, choices=Types.choices, default=default_type)
    type = MultiSelectField(choices=Types.choices, default=[], null=True, blank=True)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if self.pk:
            # Get the existing user from DB to compare old vs new type
            old_user = CustomUser.objects.get(pk=self.pk)
            old_types = set(old_user.type or [])
            new_types = set(self.type or [])

            # If Seller was removed, delete SellerAdditional
            if CustomUser.Types.SELLER in old_types and CustomUser.Types.SELLER not in new_types:
                try:
                    self.selleradditional.delete()
                except SellerAdditional.DoesNotExist:
                    pass

            # If Customer was removed, delete CustomerAdditional
            if CustomUser.Types.CUSTOMER in old_types and CustomUser.Types.CUSTOMER not in new_types:
                try:
                    self.customeradditional.delete()
                except CustomerAdditional.DoesNotExist:
                    pass
        else:
            # First-time save: assign default type if not set
            if not self.type:
                self.type = [self.default_type]
            elif self.default_type not in self.type:
                self.type.append(self.default_type)

        super().save(*args, **kwargs)

    


class CustomerAdditional(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    district = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return f"{self.user.email} - Address: {self.get_full_address()}"

    def get_full_address(self):
        return f"{self.street_address}, {self.city}, {self.district}, {self.state} - {self.pincode}"


class SellerAdditional(models.Model):
    user=models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    gst=models.CharField(max_length=15, unique=True)
    warehouse_location=models.CharField(max_length=1000)


    def __str__(self):
        return f"{self.user.email} - GST: {self.gst}, Location: {self.warehouse_location}"


# Model Managers for proxy models
class SellerManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(Q(type__contains=CustomUser.Types.SELLER))


class CustomerManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(Q(type__contains=CustomUser.Types.CUSTOMER))



# Proxy Models. They do not create a separate table in the database.
class Seller(CustomUser):
    default_type = CustomUser.Types.SELLER
    objects = SellerManager()
    class Meta:
        proxy = True

    def sell(self):
        print("Selling products...")

    @property
    def showAdditional(self):
        return self.selleradditional


class Customer(CustomUser):
    default_type = CustomUser.Types.CUSTOMER
    objects = CustomerManager()
    class Meta:
        proxy = True

    def buy(self):
        print("Buying products...")

    @property
    def showAdditional(self):
        return self.customeradditional
    

class Contact(models.Model):
    email = models.EmailField()
    name = models.CharField(max_length=255)  # ✅ must have max_length
    phone_regex = RegexValidator(regex=r'^\d{10}$', message="Phone number must be 10 digits.")
    phone = models.CharField(validators=[phone_regex], max_length=10)  # ✅ must have max_length
    query = models.TextField()


    

# class CustomerAdditional(models.Model):
#     user=models.OneToOneField(CustomUser, on_delete=models.CASCADE)
#     address = models.CharField(max_length=1000)

# class SellerAdditional(models.Model):
#     user=models.OneToOneField(CustomUser, on_delete=models.CASCADE)
#     gst=models.CharField(max_length=15, unique=True)
#     warehouse_location=models.CharField(max_length=1000)



class Product(models.Model):
    CATEGORY_CHOICES = (
        ("ELECTRONICS", "Electronics"),
        ("HOME", "Home"),
        ("FITNESS", "Fitness"),
        ("BOOKS", "Books"),
        ("TOYS", "Toys"),
        ("FURNITURE", "Furniture"),
        ("ACCESSORIES", "Accessories"),
        ("HEALTH", "Health"),
        ("FOOD", "Food"),
        ("STATIONERY", "Stationery"),
        ("OUTDOOR", "Outdoor"),
        ("TOOLS", "Tools"),
        ("DECOR", "Decor"),
        ("OTHER", "Other"),
    )
    seller = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'type__contains': 'Seller'},
        null=True,  # allow null temporarily
        blank=True
    )
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='productimages', default=None, blank=True, null=True)
    price = models.FloatField()
    brand = models.CharField(max_length=1000, default='Unknown')
    date_added = models.DateTimeField(default=timezone.now)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="ELECTRONICS",
    )

    class Meta:
        ordering = ['-price']

    @classmethod
    def updateprice(cls, product_id, price):
        product = cls.objects.filter(product_id=product_id)
        product = product.first()
        product.price = price
        product.save()
        return product
    
    @classmethod
    def create(cls, product_name, price):
        product = Product(product_name=product_name, price=price)
        product.save()
        return product

    def __str__(self):
        return self.product_name
    

class CartManager(models.Manager):
    def create_cart(self, user):
        cart = self.create(user=user)
        # you can perform more operations
        return cart


class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    created_on = models.DateTimeField(default=timezone.now)

    objects = CartManager()


class ProductInCart(models.Model):
    class Meta:
        unique_together = (('cart', 'product'),)

    product_in_cart_id = models.AutoField(primary_key=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()


class Order(models.Model):
    status_choices = (
        (1, 'Not Packed'),
        (2, 'Ready for Shipment'),
        (3, 'Shipped'),
        (4, 'Delivered'),
        (5, 'Cancelled')
    )
    payment_status_choices = (
        (1, 'SUCCESS'),
        (2, 'FAILURE'),
        (3, 'PENDING'),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    status = models.IntegerField(choices=status_choices, default=1)

    total_amount = models.FloatField(default=0.0)
    payment_status = models.IntegerField(choices=payment_status_choices, default=3)
    order_id = models.CharField(unique=True, max_length=100, null=True, blank=True, default=None)
    datetime_of_payment = models.DateTimeField(default=timezone.now)
    # related to razorpay
    razorpay_order_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=100, null=True, blank=True)


    def save(self, *args, **kwargs):
        if self.order_id is None and self.datetime_of_payment and self.id:
            self.order_id = self.datetime_of_payment.strftime('PAY2SAM%Y%m%dODR') + str(self.id)
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return self.user.email + " - " + str(self.id)
    
    def cancel_order(self):
        if self.status in [1, 2]:  # Can cancel if Not Packed or Ready to Ship
            self.status = 5  # 5 = Cancelled
            self.save()
            return True
        return False


class ProductInOrder(models.Model):
    class Meta:
        unique_together = (('order', 'product'),)
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.FloatField()



class Deal(models.Model):
    user = models.ManyToManyField(CustomUser)
    deal_name = models.CharField(max_length=255)


class PremiumProduct(models.Model):
    product_name = models.CharField(max_length=100)
    image = models.ImageField(upload_to = "customer/premiumproductimages", default = None, null = True, blank = True)
    price = models.FloatField()
    brand = models.CharField(max_length=1000)
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.product_name} - Premium"
    
    class Meta:
        permissions = (
            ('can_avail_premium_delivery', 'Can avail premium delivery on premium products'),
            ('can_add_premium_discount', 'Can add premium discount on premium products'),
        )


class CustomPermissions(models.Model):
    class Meta:

        managed = False  # No database table creation or deletion  \
                         # operations will be performed for this model.

        default_permissions = () # disable "add", "change", "delete"
                                 # and "view" default permissions

        # All the custom permissions not related to models on Manufacturer
        permissions = (
            ('accept_order', 'can accept order'),
            ('reject_order', 'can reject order'),
            ('view_order', 'can view order'),
            ('change_order', 'can change order'),
            ('view_return', 'can view return'),
            ('accept_return', 'can accept return'),
            ('reject_return', 'can reject return'),
            ('change_return', 'can change return'),
            ('view_dashboard', 'can view dashboard'),
        )
