from django.core.management.base import BaseCommand
from app.models import Electronic
from urllib.parse import quote


class Command(BaseCommand):
    help = "Seed sample electronics"

    def _image_for(self, name):
                import base64
                safe_name = name[:28]
                svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="800" viewBox="0 0 600 800">
    <defs>
        <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="#0f172a"/>
            <stop offset="100%" stop-color="#0ea5e9"/>
        </linearGradient>
    </defs>
    <rect width="600" height="800" fill="url(#g)"/>
    <rect x="92" y="110" width="416" height="580" rx="34" fill="rgba(255,255,255,0.08)" stroke="rgba(255,255,255,0.14)"/>
    <text x="50%" y="42%" text-anchor="middle" font-family="Arial, sans-serif" font-size="32" font-weight="700" fill="#ffffff">Bookstore</text>
    <text x="50%" y="51%" text-anchor="middle" font-family="Arial, sans-serif" font-size="22" fill="#cffafe">{safe_name}</text>
    <text x="50%" y="88%" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" fill="#e0f2fe">Electronics</text>
</svg>'''
                encoded = base64.b64encode(svg.encode('utf-8')).decode('utf-8')
                return f"data:image/svg+xml;base64,{encoded}"

    def handle(self, *args, **options):
        samples = [
            {
                "name": "iPhone 15",
                "brand": "Apple",
                "model_number": "A3090",
                "category": "phone",
                "description": "Apple smartphone with A16 chip",
                "price": 22990000,
                "image_url": self._image_for("iPhone 15"),
                "stock": 20,
                "warranty_months": 12,
                "is_active": True,
            },
            {
                "name": "Galaxy S24",
                "brand": "Samsung",
                "model_number": "SM-S921B",
                "category": "phone",
                "description": "Samsung flagship phone",
                "price": 19990000,
                "image_url": self._image_for("Galaxy S24"),
                "stock": 30,
                "warranty_months": 12,
                "is_active": True,
            },
            {
                "name": "MacBook Air M3",
                "brand": "Apple",
                "model_number": "MBA-M3-13",
                "category": "laptop",
                "description": "Lightweight laptop for work and study",
                "price": 29990000,
                "image_url": self._image_for("MacBook Air M3"),
                "stock": 12,
                "warranty_months": 12,
                "is_active": True,
            },
            {
                "name": "Dell XPS 13",
                "brand": "Dell",
                "model_number": "XPS13-9340",
                "category": "laptop",
                "description": "Premium ultrabook with OLED display",
                "price": 32990000,
                "image_url": self._image_for("Dell XPS 13"),
                "stock": 10,
                "warranty_months": 24,
                "is_active": True,
            },
            {
                "name": "Sony WH-1000XM5",
                "brand": "Sony",
                "model_number": "WH1000XM5",
                "category": "audio",
                "description": "Noise-canceling wireless headphones",
                "price": 8990000,
                "image_url": self._image_for("Sony WH-1000XM5"),
                "stock": 50,
                "warranty_months": 12,
                "is_active": True,
            },
        ]

        created_count = 0
        for data in samples:
            _, created = Electronic.objects.update_or_create(
                brand=data["brand"],
                name=data["name"],
                model_number=data["model_number"],
                defaults=data,
            )
            if created:
                created_count += 1

        total = Electronic.objects.count()
        self.stdout.write(self.style.SUCCESS(f"Seed complete. Created: {created_count}, Total: {total}"))
