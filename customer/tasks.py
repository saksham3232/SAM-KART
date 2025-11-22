from .models import Order
from django.utils import timezone
from customer.views import handle_order_status_change

def update_order_statuses():
    orders = Order.objects.all()
    updated_count = 0

    for order in orders:
        if not order.datetime_of_payment:
            continue  # skip if no payment date

        days_passed = (timezone.now().date() - order.datetime_of_payment.date()).days

        # Update based on days
        new_status = None
        if days_passed <= 1:
            new_status = 1  # Not Packed
        elif 2 <= days_passed <= 4:
            new_status = 2  # Ready for Shipment
        elif 5 <= days_passed <= 6:
            new_status = 3  # Shipped
        elif days_passed >= 7:
            new_status = 4  # Delivered

        handle_order_status_change(order, new_status)
        if new_status and order.status != new_status:
            updated_count += 1

    print(f"✅ {updated_count} orders updated based on days passed.")
