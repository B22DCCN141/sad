from django.core.management.base import BaseCommand
from app.models import Customer

class Command(BaseCommand):
    help = "Seed customer database with sample data"

    def handle(self, *args, **options):
        customers = [
            {
                'name': 'Nguyễn Văn A',
                'email': 'nguyenvana@example.com',
                'password': 'password123',
                'phone': '0901234567',
                'address': '123 Nguyen Hue, HCMC, Vietnam'
            },
            {
                'name': 'Trần Thị B',
                'email': 'tranthib@example.com',
                'password': 'password123',
                'phone': '0912345678',
                'address': '456 Le Loi, Hanoi, Vietnam'
            },
            {
                'name': 'Phạm Văn C',
                'email': 'phamvanc@example.com',
                'password': 'password123',
                'phone': '0923456789',
                'address': '789 Tran Hung Dao, Da Nang, Vietnam'
            },
            {
                'name': 'Đinh Thị D',
                'email': 'dinhithid@example.com',
                'password': 'password123',
                'phone': '0934567890',
                'address': '321 Pasteur, HCMC, Vietnam'
            },
            {
                'name': 'Hoàng Văn E',
                'email': 'hoangvane@example.com',
                'password': 'password123',
                'phone': '0945678901',
                'address': '654 Ly Thuong Kiet, Hanoi, Vietnam'
            },
        ]

        for data in customers:
            obj, created = Customer.objects.get_or_create(
                email=data['email'],
                defaults=data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created customer: {obj.name}'))
            else:
                self.stdout.write(f'→ Customer already exists: {obj.name}')

        self.stdout.write(self.style.SUCCESS(f'\n✓ Seed complete! Total customers: {Customer.objects.count()}'))
