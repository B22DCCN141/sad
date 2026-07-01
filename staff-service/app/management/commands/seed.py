from django.core.management.base import BaseCommand
from app.models import Staff

class Command(BaseCommand):
    help = "Seed staff database with sample data"

    def handle(self, *args, **options):
        staffs = [
            {
                'name': 'Admin User',
                'email': 'admin@bookstore.com',
                'password': 'admin123',
                'role': 'admin',
                'phone': '0901111111'
            },
            {
                'name': 'Lê Văn Manager',
                'email': 'manager@bookstore.com',
                'password': 'manager123',
                'role': 'manager',
                'phone': '0902222222'
            },
            {
                'name': 'Ngô Thị Staff One',
                'email': 'staff1@bookstore.com',
                'password': 'staff123',
                'role': 'staff',
                'phone': '0903333333'
            },
            {
                'name': 'Bùi Văn Staff Two',
                'email': 'staff2@bookstore.com',
                'password': 'staff123',
                'role': 'staff',
                'phone': '0904444444'
            },
            {
                'name': 'Võ Thị Support',
                'email': 'support@bookstore.com',
                'password': 'support123',
                'role': 'support',
                'phone': '0905555555'
            },
        ]

        for data in staffs:
            obj, created = Staff.objects.get_or_create(
                email=data['email'],
                defaults=data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created staff: {obj.name} ({obj.role})'))
            else:
                self.stdout.write(f'→ Staff already exists: {obj.name}')

        self.stdout.write(self.style.SUCCESS(f'\n✓ Seed complete! Total staffs: {Staff.objects.count()}'))
