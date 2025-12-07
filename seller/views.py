from django.shortcuts import render, HttpResponse, redirect
from django.views.generic import TemplateView, FormView, CreateView
from django.core.exceptions import ValidationError
from customer.forms import ContactUsForm, RegistrationForm, RegistrationFormSeller2
from django.urls import reverse_lazy
from customer.models import SellerAdditional, CustomUser
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.


def index(request):
    # context = {
    #     'age': 25,
    #     'array': [1, 2, 3, 4, 5],
    #     'dic': {'name': 'Saksham', 'age': 22, 'city': 'Lucknow'}
    # }
    return render(request, 'seller/index.html')



from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.utils.timezone import localtime

class ContactUs(FormView):
    form_class = ContactUsForm
    template_name = 'seller/contactus.html'
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        query = form.cleaned_data.get('query')

        # ✅ Check if query length is less than 10
        if len(query) < 10:
            form.add_error('query', 'Query must be at least 10 characters long')
            return render(self.request, 'customer/contactus2.html', {'form': form})

        # ✅ Save to DB
        form.save()

        # ✅ Prepare email
        subject = '📩 New Contact Form Submission'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = ['sakshammaurya678@gmail.com']
        context = {
            'name': form.cleaned_data.get('name'),
            'email': form.cleaned_data.get('email'),
            'phone': form.cleaned_data.get('phone'),
            'query': query,
            'timestamp': localtime(timezone.now()).strftime('%d %B %Y, %I:%M %p'),
        }

        # ✅ Load HTML template for email
        html_content = render_to_string('customer/email_template.html', context)
        text_content = f"""
        New contact form submission:

        Name: {context['name']}
        Email: {context['email']}
        Phone: {context['phone']}
        Query: {context['query']}
        """

        # ✅ Send email
        email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)

        return super().form_valid(form)


    def form_invalid(self, form):
        query = form.cleaned_data.get('query')
        
        # ✅ Correct condition: show error if query is too short
        if query and len(query) < 10:
            form.add_error('query', 'Query must be at least 10 characters long')
        
        return render(self.request, 'customer/contactus2.html', {'form': form})





class LoginViewUser(LoginView):
    template_name = 'seller/login.html'

    def get_success_url(self):
        return self.get_redirect_url() or reverse_lazy('index')



class SellerLoginView(LoginView):
    template_name = 'seller/sellerlogin.html'  # ✅ Use a different template (you can duplicate the normal one)

    def form_valid(self, form):
        user = form.get_user()
        if CustomUser.Types.SELLER not in user.type:
            form.add_error(None, "You are not authorized to login as a seller.")
            return self.form_invalid(form)
        return super().form_valid(form)


from django.contrib import messages
from django.shortcuts import redirect

class RegisterViewSeller(LoginRequiredMixin, CreateView):
    template_name = 'seller/register.html'
    form_class = RegistrationFormSeller2
    success_url = reverse_lazy('index')
    login_url = reverse_lazy('login')  # Optional: overrides settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if SellerAdditional.objects.filter(user=request.user).exists():
                messages.info(request, "You are already registered as a seller.")
                return redirect('index')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = self.request.user
        if user.Types.SELLER not in user.type:
            user.type.append(user.Types.SELLER)
            user.save()
        form.instance.user = user
        return super().form_valid(form)




class LogoutViewUser(LogoutView):
    # success_url = reverse_lazy('index')
    next_page = reverse_lazy('index')


class RegisterView(CreateView):
    template_name = 'seller/registerbaseuser.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('index')




# seller/views.py

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from customer.models import Product
from customer.forms import ProductForm

class SellerDashboardView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'seller/dashboard.html'
    context_object_name = 'products'

    def get_queryset(self):
        # print("Current User:", self.request.user)
        # print("User Type:", self.request.user.type)
        qs = Product.objects.filter(seller=self.request.user)
        # print("QuerySet count:", qs.count())
        return qs



class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'seller/product_form.html'
    success_url = reverse_lazy('seller-dashboard')

    def form_valid(self, form):
        form.instance.seller = self.request.user
        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'seller/product_form.html'
    success_url = reverse_lazy('seller-dashboard')

    def get_queryset(self):
        return Product.objects.filter(seller=self.request.user)


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'seller/product_confirm_delete.html'
    success_url = reverse_lazy('seller-dashboard')

    def get_queryset(self):
        return Product.objects.filter(seller=self.request.user)

from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.shortcuts import render
from customer.models import Order, ProductInOrder
from customer.views import handle_order_status_change
@login_required
def seller_orders(request):
    # Fetch all product-in-order items for this seller
    seller_items = ProductInOrder.objects.select_related('order', 'product')\
    .filter(product__seller=request.user, order__payment_status=1)\
    .order_by('-order__datetime_of_payment')  # or '-order__created_at'

    # Group items by order
    order_map = {}  # { order: [seller's products in this order] }
    processed_orders = set()

    for item in seller_items:
        order = item.order
        if order not in order_map:
            order_map[order] = []
        order_map[order].append(item)

        # Update order status only once per order
        if order.id not in processed_orders:
            processed_orders.add(order.id)

            if order.datetime_of_payment:
                days_passed = (timezone.now().date() - order.datetime_of_payment.date()).days

                if days_passed <= 1:
                    new_status = 1
                elif 2 <= days_passed <= 4:
                    new_status = 2
                elif 5 <= days_passed <= 6:
                    new_status = 3
                else:
                    new_status = 4

                # ✅ Status change only triggers email/notification
                handle_order_status_change(order, new_status)

    # Dynamically calculate seller’s share of total per order
    for order, items in order_map.items():
        grand_total = 0
        for item in items:
            item.subtotal = item.price * item.quantity
            grand_total += item.subtotal
        order.grand_total = grand_total

    return render(request, 'seller/seller_orders.html', {'order_map': order_map})

from django.views.generic import DetailView

class ProductDetail(DetailView):
    model = Product
    template_name = 'seller/productdetail.html'
    context_object_name = 'product'
