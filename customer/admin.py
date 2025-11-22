from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


from .models import Product, Cart, ProductInCart, Order, Deal, Customer, Seller, Contact, ProductInOrder, PremiumProduct, CustomerAdditional
# Register your models here,


from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, SellerAdditional



class SellerAdditionalInline(admin.TabularInline):
    model = SellerAdditional

class CustomerAdditionalInline(admin.TabularInline):
    model = CustomerAdditional


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('email', 'is_staff', 'is_active',)
    list_filter = ('email', 'is_staff', 'is_active',)
    # fieldsets = (
    #     (None, {'fields': ('email', 'password')}),
    #     ('Permissions', {'fields': ('is_staff', 'is_active', 'is_customer', 'is_seller')}),
    # )
    fieldsets = (
        (None, {'fields': ('email', 'name', 'type', 'password', 'phone')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),   #'is_customer' , 'is_seller'
    )
    # add_fieldsets = (
    #     (None, {
    #         'classes': ('wide',),
    #         'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
    #     ),
    # )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'type', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)

    inlines = [
        CustomerAdditionalInline,
        SellerAdditionalInline,
    ]




class SellerAdmin(admin.ModelAdmin):
    inlines = [SellerAdditionalInline]



admin.site.register(CustomUser, CustomUserAdmin)



class ProdutInCartInline(admin.TabularInline):
    model = ProductInCart

class CartInline(admin.TabularInline):
    model = Cart # This is the Cart model, which is a one-to-one relationship with User

class DealInline(admin.TabularInline):
    model = Deal.user.through # This is the through model for the ManyToMany relationship between Deal and User


# class UserAdmin(UserAdmin):
#     model = User
#     list_display = ('username', 'get_cart', 'is_staff', 'is_active',)
#     list_filter = ('username','is_staff', 'is_active', 'is_superuser',)
#     fieldsets = (
#         (None, {'fields': ('username', 'password')}),
#         ('Permissions', {'fields': ('is_staff', ('is_active', 'is_superuser'), )}),
#         ('Important dates', {'fields': ('last_login', 'date_joined')}),
#         ('Advanced options', {
#             'classes' : ('collapse',),
#             'fields': ('groups', 'user_permissions'),
#         }),
#     )
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide', ), # classes for styling
#             'fields': ('username', 'password1', 'password2', 'is_staff', 'is_active', 'is_superuser', 'groups') # fields to add   
#         }),
#     )
#     inlines = [
#         CartInline, DealInline
#     ]
#     def get_cart(self,obj):
#         return obj.cart
#     search_fields = ('username',)
#     ordering = ('username',)




@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    model = Cart
    list_display = ('cart_id', 'user', 'created_on') # here user__is_staff will not work
    list_filter = ('user', 'created_on',)
    fieldsets = (
        (None, {'fields': ('user', 'created_on',)}),
    )
    inlines = [
        ProdutInCartInline
    ]
    # To display only in list_display
    def staff(self, obj):
        return obj.user.is_staff
    
    staff.admin_order_field = 'user__is_staff' # Allows column order sorting
    staff.short_description = 'Staff User' # Renames column head

    # Filtering on side - for some reason, this works
    list_filter = ['user__is_staff', 'created_on'] # with direct foreign key no error but not shown in filters, with function error
    search_fields = ['user__username'] # with direct foreign key no error but not shown in search, with function error


class ProductInOrderInline(admin.TabularInline):
    model = ProductInOrder


@admin.register(Order)
class CartAdmin(admin.ModelAdmin):
    model = Cart
    inlines = (
        ProductInOrderInline,
    )


# class DealAdmin(admin.ModelAdmin):
#     inlines = [
#         DealInline
#     ]
#     exclude = ('user',)


admin.site.register(Product)
admin.site.register(ProductInCart)
# admin.site.register(Order)
admin.site.register(Deal)#, DealAdmin)
# admin.site.register(UserType)
admin.site.register(Customer)
admin.site.register(Seller, SellerAdmin)
admin.site.register(Contact)
admin.site.register(CustomerAdditional)
admin.site.register(SellerAdditional)



from django.contrib.sessions.models import Session
import pprint



class SessionAdmin(admin.ModelAdmin):
    def _session_data(self, obj):
        return pprint.pformat(obj.get_decoded()).replace('\n', '<br>\n')
    _session_data.allow_tags = True
    list_display = ['session_key', '_session_data', 'expire_date']
    readonly_fields = ['_session_data']
    exclude = ['session_data']



admin.site.register(Session, SessionAdmin)

admin.site.register(ProductInOrder)

admin.site.register(PremiumProduct)