from django.core.management.base import BaseCommand
from app.models import Book
from urllib.parse import quote

class Command(BaseCommand):
    help = "Seed book database with sample data"

    def _image_for(self, name):
                import base64
                safe_name = name[:28]
                svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="800" viewBox="0 0 600 800">
    <defs>
        <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="#111827"/>
            <stop offset="100%" stop-color="#7c3aed"/>
        </linearGradient>
    </defs>
    <rect width="600" height="800" fill="url(#g)"/>
    <circle cx="470" cy="125" r="110" fill="rgba(255,255,255,0.08)"/>
    <circle cx="120" cy="650" r="150" fill="rgba(255,255,255,0.06)"/>
    <text x="50%" y="43%" text-anchor="middle" font-family="Arial, sans-serif" font-size="34" font-weight="700" fill="#ffffff">Bookstore</text>
    <text x="50%" y="52%" text-anchor="middle" font-family="Arial, sans-serif" font-size="22" fill="#e9d5ff">{safe_name}</text>
    <text x="50%" y="90%" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" fill="#f3e8ff">Book cover</text>
</svg>'''
                encoded = base64.b64encode(svg.encode('utf-8')).decode('utf-8')
                return f"data:image/svg+xml;base64,{encoded}"

    def handle(self, *args, **options):
        books = [
            {
                'title': 'Clean Code: A Handbook of Agile Software Craftsmanship',
                'author': 'Robert C. Martin',
                'price': 350000.00,
                'stock': 50,
                'category_id': 1,
                'image_url': self._image_for('Clean Code')
            },
            {
                'title': 'The Pragmatic Programmer',
                'author': 'David Thomas, Andrew Hunt',
                'price': 280000.00,
                'stock': 40,
                'category_id': 1,
                'image_url': self._image_for('The Pragmatic Programmer')
            },
            {
                'title': 'Design Patterns',
                'author': 'Gang of Four',
                'price': 420000.00,
                'stock': 30,
                'category_id': 1,
                'image_url': self._image_for('Design Patterns')
            },
            {
                'title': 'Code Complete',
                'author': 'Steve McConnell',
                'price': 380000.00,
                'stock': 35,
                'category_id': 1,
                'image_url': self._image_for('Code Complete')
            },
            {
                'title': 'Refactoring',
                'author': 'Martin Fowler',
                'price': 320000.00,
                'stock': 40,
                'category_id': 1,
                'image_url': self._image_for('Refactoring')
            },
        ]

        Book.objects.all().delete()

        for data in books:
            obj = Book.objects.create(**data)
            self.stdout.write(self.style.SUCCESS(f'✓ Created book: {obj.title}'))

        self.stdout.write(self.style.SUCCESS(f'\n✓ Seed complete! Total books: {Book.objects.count()}'))
