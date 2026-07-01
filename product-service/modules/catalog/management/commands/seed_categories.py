"""
Management command: Seed 10 loại danh mục sản phẩm vào database.
Chạy: python manage.py seed_categories

Theo DDD Cach 2 - Category la DU LIEU:
  10 loai danh muc chinh:
    1.  dien-thoai   - Dien thoai (Phone)
    2.  laptop       - Laptop
    3.  thoi-trang   - Thoi trang (Fashion)
    4.  my-pham      - My pham (Cosmetic)
    5.  do-gia-dung  - Do gia dung (Appliance)
    6.  sach         - Sach (Book)
    7.  the-thao     - The thao (Sports)
    8.  do-choi      - Do choi (Toy)
    9.  phu-kien     - Phu kien (Accessories)
    10. thuc-pham    - Thuc pham (Food)
"""
from django.core.management.base import BaseCommand
from modules.catalog.infrastructure.models.product_model import CategoryModel, BrandModel


# 10 product type categories
CATEGORIES = [
    {
        'name': 'Dien thoai',
        'slug': 'dien-thoai',
        'description': 'Smartphones and mobile phones',
    },
    {
        'name': 'Laptop',
        'slug': 'laptop',
        'description': 'Personal computers and laptops',
    },
    {
        'name': 'Thoi trang',
        'slug': 'thoi-trang',
        'description': 'Fashion: clothing, shoes, bags',
    },
    {
        'name': 'My pham',
        'slug': 'my-pham',
        'description': 'Cosmetics, skincare, beauty products',
    },
    {
        'name': 'Do gia dung',
        'slug': 'do-gia-dung',
        'description': 'Home appliances and electronics',
    },
    {
        'name': 'Sach',
        'slug': 'sach',
        'description': 'Books, textbooks, novels',
    },
    {
        'name': 'The thao',
        'slug': 'the-thao',
        'description': 'Sports equipment and activewear',
    },
    {
        'name': 'Do choi',
        'slug': 'do-choi',
        'description': 'Toys and games for children',
    },
    {
        'name': 'Phu kien',
        'slug': 'phu-kien',
        'description': 'Tech accessories: earphones, watches, cases',
    },
    {
        'name': 'Thuc pham',
        'slug': 'thuc-pham',
        'description': 'Food and beverages',
    },
]

BRANDS = [
    {'name': 'Apple',       'slug': 'apple',       'description': 'iPhone, MacBook, iPad, AirPods'},
    {'name': 'Samsung',     'slug': 'samsung',     'description': 'Galaxy phones, TVs, appliances'},
    {'name': 'Xiaomi',      'slug': 'xiaomi',      'description': 'Smartphones, smart home'},
    {'name': 'Dell',        'slug': 'dell',        'description': 'Laptop XPS, Inspiron, Alienware'},
    {'name': 'ASUS',        'slug': 'asus',        'description': 'ROG, ZenBook, VivoBook'},
    {'name': 'Nike',        'slug': 'nike',        'description': 'Sport footwear & apparel'},
    {'name': 'Adidas',      'slug': 'adidas',      'description': 'Sport footwear & apparel'},
    {'name': 'Uniqlo',      'slug': 'uniqlo',      'description': 'Everyday casual fashion'},
    {"name": "L'Oreal",    'slug': 'loreal',      'description': 'Skincare & cosmetics'},
    {'name': 'Anessa',      'slug': 'anessa',      'description': 'Sunscreen & skincare'},
    {'name': 'MAC',         'slug': 'mac-cosmetics','description': 'Professional makeup'},
    {'name': 'Philips',     'slug': 'philips',     'description': 'Home appliances'},
    {'name': 'Panasonic',   'slug': 'panasonic',   'description': 'Electronics & appliances'},
    {'name': 'NXB Tre',     'slug': 'nxb-tre',     'description': 'Book publisher - NXB Tre'},
    {'name': 'Yonex',       'slug': 'yonex',       'description': 'Badminton & tennis equipment'},
    {'name': 'LEGO',        'slug': 'lego',        'description': 'Building block toys'},
    {'name': 'Mattel',      'slug': 'mattel',      'description': 'Barbie, Hot Wheels toys'},
    {'name': 'Trung Nguyen', 'slug': 'trung-nguyen','description': 'Vietnamese coffee brand'},
]


class Command(BaseCommand):
    help = 'Seed 10 product type categories and brands into database'

    def _safe_write(self, msg):
        try:
            self.stdout.write(msg)
        except UnicodeEncodeError:
            self.stdout.write(msg.encode('ascii', errors='replace').decode('ascii'))

    def handle(self, *args, **options):
        self._safe_write('=== Seeding 10 Product Type Categories & Brands ===\n')
        self._seed_brands()
        self._seed_categories()
        self._safe_write(self.style.SUCCESS('\nDone! 10 categories seeded successfully.'))

    def _seed_brands(self):
        self._safe_write('\n[Brands]')
        for b in BRANDS:
            _, created = BrandModel.objects.get_or_create(slug=b['slug'], defaults=b)
            label = 'Created' if created else 'Exists'
            self._safe_write(f'  [{label}] {b["name"]}')

    def _seed_categories(self):
        self._safe_write('\n[10 Product Type Categories]')
        for i, cat in enumerate(CATEGORIES, 1):
            _, created = CategoryModel.objects.get_or_create(
                slug=cat['slug'],
                defaults={
                    'name': cat['name'],
                    'slug': cat['slug'],
                    'description': cat['description'],
                    'parent': None,  # All are root categories
                    'is_active': True,
                }
            )
            label = 'Created' if created else 'Exists'
            self._safe_write(f'  [{i:02d}] [{label}] {cat["slug"]} - {cat["name"]}')
