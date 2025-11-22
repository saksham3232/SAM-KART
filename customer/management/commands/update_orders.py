from django.core.management.base import BaseCommand
from customer.tasks import update_order_statuses

class Command(BaseCommand):
    help = 'Update order status based on days passed'

    def handle(self, *args, **kwargs):
        update_order_statuses()
        self.stdout.write(self.style.SUCCESS("✅ Order statuses updated."))
