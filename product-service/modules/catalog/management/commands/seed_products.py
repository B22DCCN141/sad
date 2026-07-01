"""
Management command: Seed sample products for each of the 10 product types.
Run: python manage.py seed_products

Structure:
  ProductService
  ├── Dien thoai (Phone)      → 3 products
  ├── Laptop                  → 3 products
  ├── Thoi trang (Fashion)    → 3 products
  ├── My pham (Cosmetic)      → 3 products
  ├── Do gia dung (Appliance) → 3 products
  ├── Sach (Book)             → 3 products
  ├── The thao (Sports)       → 3 products
  ├── Do choi (Toy)           → 3 products
  ├── Phu kien (Accessories)  → 3 products
  └── Thuc pham (Food)        → 3 products
  Total: 30 sample products
"""
import copy
from urllib.parse import quote

from django.core.management.base import BaseCommand
from modules.catalog.infrastructure.models.product_model import (
    ProductModel, CategoryModel, BrandModel
)

# =============================================================================
# PRODUCTS organized by category slug
# Each category has 3 sample products
# attributes (JSONB) are flexible per product type - DDD Method 2 core concept
# =============================================================================

PRODUCTS_BY_CATEGORY = {

    # ─────────────────────────────────────────────────────────────────────────
    # 1. DIEN THOAI (Phone)
    #    attributes: ram, storage, screen_size, os, chip, camera, battery, color
    # ─────────────────────────────────────────────────────────────────────────
    'dien-thoai': [
        {
            'name': 'iPhone 15 Pro Max',
            'description': 'Apple flagship with A17 Pro chip, 48MP camera, Titanium design.',
            'price': 32990000,
            'stock': 50,
            'brand_slug': 'apple',
            'image_url': 'https://store.storeimages.cdn-apple.com/iphone-15-pro-max.jpg',
            'attributes': {
                'ram': '8GB',
                'storage': '256GB',
                'screen_size': '6.7 inch',
                'os': 'iOS 17',
                'chip': 'Apple A17 Pro',
                'camera': '48MP + 12MP + 12MP',
                'battery': '4422 mAh',
                'color': 'Natural Titanium',
                'warranty': '12 months',
            },
        },
        {
            'name': 'Samsung Galaxy S24 Ultra',
            'description': 'Samsung flagship with built-in S Pen, 200MP camera, Galaxy AI.',
            'price': 29990000,
            'stock': 35,
            'brand_slug': 'samsung',
            'image_url': 'https://images.samsung.com/galaxy-s24-ultra.jpg',
            'attributes': {
                'ram': '12GB',
                'storage': '512GB',
                'screen_size': '6.8 inch',
                'os': 'Android 14',
                'chip': 'Snapdragon 8 Gen 3',
                'camera': '200MP + 12MP + 50MP + 10MP',
                'battery': '5000 mAh',
                'color': 'Titanium Black',
                's_pen': True,
                'warranty': '12 months',
            },
        },
        {
            'name': 'Xiaomi 14 Ultra',
            'description': 'Xiaomi pro photography phone with Leica Summilux lens, Snapdragon 8 Gen 3.',
            'price': 22990000,
            'stock': 25,
            'brand_slug': 'xiaomi',
            'image_url': 'https://i01.appmifile.com/xiaomi-14-ultra.jpg',
            'attributes': {
                'ram': '16GB',
                'storage': '512GB',
                'screen_size': '6.73 inch',
                'os': 'Android 14 (HyperOS)',
                'chip': 'Snapdragon 8 Gen 3',
                'camera': '50MP Leica Summilux x4',
                'battery': '5000 mAh',
                'color': 'White',
                'warranty': '12 months',
            },
        },
    ],

    # ─────────────────────────────────────────────────────────────────────────
    # 2. LAPTOP
    #    attributes: ram, storage, cpu, gpu, screen, battery, os, weight
    # ─────────────────────────────────────────────────────────────────────────
    'laptop': [
        {
            'name': 'MacBook Pro 14 inch M4',
            'description': 'Apple MacBook Pro with M4 chip, Liquid Retina XDR, up to 17h battery.',
            'price': 52990000,
            'stock': 20,
            'brand_slug': 'apple',
            'image_url': 'https://store.storeimages.cdn-apple.com/macbook-pro-14-m4.jpg',
            'attributes': {
                'ram': '16GB',
                'storage': '512GB SSD',
                'cpu': 'Apple M4',
                'gpu': 'Apple M4 10-core GPU',
                'screen': '14.2 inch Liquid Retina XDR',
                'battery': 'Up to 17 hours',
                'os': 'macOS Sequoia',
                'weight': '1.55 kg',
                'warranty': '12 months',
            },
        },
        {
            'name': 'Dell XPS 15 9530',
            'description': 'Dell premium laptop with OLED 3.5K display, RTX 4060, Intel Core i9.',
            'price': 45990000,
            'stock': 15,
            'brand_slug': 'dell',
            'image_url': 'https://i.dell.com/xps-15-9530.jpg',
            'attributes': {
                'ram': '32GB DDR5',
                'storage': '1TB NVMe SSD',
                'cpu': 'Intel Core i9-13900H',
                'gpu': 'NVIDIA GeForce RTX 4060 8GB',
                'screen': '15.6 inch OLED 3.5K 60Hz',
                'battery': '86Wh',
                'os': 'Windows 11 Home',
                'weight': '1.86 kg',
                'warranty': '12 months',
            },
        },
        {
            'name': 'ASUS ROG Zephyrus G14 2024',
            'description': 'Ultimate gaming laptop: AMD Ryzen 9, RTX 4070, AniMe Matrix LED lid.',
            'price': 41990000,
            'stock': 18,
            'brand_slug': 'asus',
            'image_url': 'https://dlcdnwebimgs.asus.com/rog-zephyrus-g14.jpg',
            'attributes': {
                'ram': '32GB DDR5',
                'storage': '1TB NVMe SSD',
                'cpu': 'AMD Ryzen 9 8945HS',
                'gpu': 'NVIDIA GeForce RTX 4070 8GB',
                'screen': '14 inch OLED 2.8K 120Hz',
                'battery': '73Wh',
                'os': 'Windows 11 Home',
                'weight': '1.65 kg',
                'rgb': 'AniMe Matrix LED',
                'warranty': '24 months',
            },
        },
    ],

    # ─────────────────────────────────────────────────────────────────────────
    # 3. THOI TRANG (Fashion)
    #    attributes: size, color, material, gender, style, fit
    # ─────────────────────────────────────────────────────────────────────────
    'thoi-trang': [
        {
            'name': "Nike Air Force 1 '07 - White",
            'description': 'Classic Nike Air Force 1 sneaker with Air cushioning, synthetic leather upper.',
            'price': 2790000,
            'stock': 100,
            'brand_slug': 'nike',
            'image_url': 'https://static.nike.com/air-force-1-07-white.png',
            'attributes': {
                'size': '42',
                'color': 'White/White',
                'material': 'Synthetic leather',
                'gender': 'Unisex',
                'sole': 'Rubber',
                'style': 'Lifestyle sneaker',
                'care': 'Wipe with damp cloth',
            },
        },
        {
            'name': 'Adidas Ultraboost 22 Running',
            'description': 'High-performance running shoe with Boost midsole and Primeknit upper.',
            'price': 3590000,
            'stock': 80,
            'brand_slug': 'adidas',
            'image_url': 'https://assets.adidas.com/ultraboost-22.jpg',
            'attributes': {
                'size': '43',
                'color': 'Core Black/Carbon',
                'material': 'Primeknit+ upper',
                'gender': 'Male',
                'sole': 'Continental Rubber',
                'style': 'Running',
                'technology': 'Boost midsole',
            },
        },
        {
            'name': 'Uniqlo Pique Polo Shirt (Men)',
            'description': 'Classic pique polo shirt in breathable cotton, versatile for office and casual.',
            'price': 490000,
            'stock': 200,
            'brand_slug': 'uniqlo',
            'image_url': 'https://image.uniqlo.com/polo-shirt.jpg',
            'attributes': {
                'size': 'L',
                'color': 'Navy Blue',
                'material': 'Cotton Pique 100%',
                'gender': 'Male',
                'fit': 'Regular Fit',
                'care': 'Machine wash 40C',
                'collar': 'Polo collar',
            },
        },
    ],

    # ─────────────────────────────────────────────────────────────────────────
    # 4. MY PHAM (Cosmetic)
    #    attributes: volume, skin_type, key_ingredient, usage, expiry, country
    # ─────────────────────────────────────────────────────────────────────────
    'my-pham': [
        {
            'name': "L'Oreal Revitalift Serum Vitamin C 12%",
            'description': '12% pure Vitamin C serum to brighten skin, reduce dark spots, anti-aging.',
            'price': 680000,
            'stock': 120,
            'brand_slug': 'loreal',
            'image_url': 'https://product.hstatic.net/loreal-serum-vitc.jpg',
            'attributes': {
                'volume': '30ml',
                'skin_type': 'All skin types',
                'key_ingredient': 'Vitamin C 12%, Hyaluronic Acid',
                'expiry': '36 months from manufacture',
                'usage': 'Morning & evening after toner',
                'country': 'France',
                'spf': False,
            },
        },
        {
            'name': 'Anessa Perfect UV Sunscreen SPF50+',
            'description': 'Japanese sunscreen with super waterproof formula, SPF50+ PA++++.',
            'price': 490000,
            'stock': 150,
            'brand_slug': 'anessa',
            'image_url': 'https://product.hstatic.net/anessa-sunscreen.jpg',
            'attributes': {
                'volume': '60ml',
                'skin_type': 'All skin types',
                'key_ingredient': 'AquaBooster EX technology',
                'spf': 'SPF50+ PA++++',
                'expiry': '36 months',
                'usage': 'Apply before sun exposure',
                'country': 'Japan',
                'waterproof': True,
            },
        },
        {
            'name': 'MAC Ruby Woo Lipstick',
            'description': 'MAC iconic matte red lipstick, long-lasting, full coverage.',
            'price': 750000,
            'stock': 90,
            'brand_slug': 'mac-cosmetics',
            'image_url': 'https://www.maccosmetics.com/ruby-woo.jpg',
            'attributes': {
                'weight': '3g',
                'color': 'Ruby Woo (Classic Red)',
                'finish': 'Matte',
                'skin_type': 'All skin types',
                'key_ingredient': 'Vitamin E, Castor Oil',
                'expiry': '24 months',
                'usage': 'Apply directly or with lip brush',
                'country': 'USA',
                'waterproof': False,
            },
        },
    ],

    # ─────────────────────────────────────────────────────────────────────────
    # 5. DO GIA DUNG (Appliance)
    #    attributes: capacity/power, functions, color, warranty, weight
    # ─────────────────────────────────────────────────────────────────────────
    'do-gia-dung': [
        {
            'name': 'Philips HD3030 Rice Cooker 1.8L',
            'description': 'Philips 1.8L rice cooker with steam technology to preserve vitamins.',
            'price': 890000,
            'stock': 60,
            'brand_slug': 'philips',
            'image_url': 'https://philips.com.vn/hd3030.jpg',
            'attributes': {
                'capacity': '1.8 liters',
                'power': '700W',
                'functions': ['Cook rice', 'Keep warm', 'Cook porridge'],
                'color': 'White',
                'warranty': '24 months',
                'weight': '1.7 kg',
                'voltage': '220V',
            },
        },
        {
            'name': 'Xiaomi Mi Air Purifier 4 Pro',
            'description': 'Smart air purifier with OLED display, HEPA H13 filter, 60m2 coverage.',
            'price': 3290000,
            'stock': 40,
            'brand_slug': 'xiaomi',
            'image_url': 'https://mi.com/air-purifier-4-pro.jpg',
            'attributes': {
                'coverage': '60 m2',
                'cadr': '500 m3/h',
                'filter': 'HEPA H13',
                'display': 'OLED touch screen',
                'noise': '32dB (sleep mode)',
                'warranty': '12 months',
                'weight': '5.3 kg',
                'smart': True,
                'app': 'Mi Home / Xiaomi Home',
            },
        },
        {
            'name': 'Panasonic NN-ST34H Microwave 25L',
            'description': 'Panasonic 800W microwave 25L with turntable and defrost function.',
            'price': 2190000,
            'stock': 30,
            'brand_slug': 'panasonic',
            'image_url': 'https://panasonic.net/nn-st34h.jpg',
            'attributes': {
                'capacity': '25 liters',
                'power': '800W',
                'functions': ['Heat', 'Defrost', 'Auto cook'],
                'color': 'Silver/Black',
                'warranty': '12 months',
                'weight': '10.5 kg',
                'voltage': '220V',
                'turntable': True,
            },
        },
    ],

    # ─────────────────────────────────────────────────────────────────────────
    # 6. SACH (Book)
    #    attributes: author, publisher, pages, language, isbn, genre, year
    # ─────────────────────────────────────────────────────────────────────────
    'sach': [
        {
            'name': 'Dac Nhan Tam - Dale Carnegie',
            'description': 'Classic self-help book on interpersonal skills and winning friends.',
            'price': 86000,
            'stock': 300,
            'brand_slug': 'nxb-tre',
            'image_url': 'https://product.hstatic.net/dac-nhan-tam.jpg',
            'attributes': {
                'author': 'Dale Carnegie',
                'translator': 'Nguyen Van Phuoc',
                'publisher': 'NXB Tre',
                'pages': 320,
                'language': 'Vietnamese',
                'isbn': '9786041115743',
                'genre': 'Self-help',
                'year': 2023,
            },
        },
        {
            'name': 'Nha Gia Kim - Paulo Coelho',
            'description': 'World renowned novel about following your personal legend.',
            'price': 79000,
            'stock': 250,
            'brand_slug': 'nxb-tre',
            'image_url': 'https://product.hstatic.net/nha-gia-kim.jpg',
            'attributes': {
                'author': 'Paulo Coelho',
                'translator': 'Le Thi Thanh Tam',
                'publisher': 'NXB Hoi Nha Van',
                'pages': 228,
                'language': 'Vietnamese',
                'isbn': '9786041216099',
                'genre': 'Novel / Philosophy',
                'year': 2022,
            },
        },
        {
            'name': 'Atomic Habits - James Clear',
            'description': 'Proven framework for building good habits and breaking bad ones.',
            'price': 105000,
            'stock': 180,
            'brand_slug': 'nxb-tre',
            'image_url': 'https://product.hstatic.net/atomic-habits.jpg',
            'attributes': {
                'author': 'James Clear',
                'translator': 'Nguyen Viet Hung',
                'publisher': 'NXB Lao Dong',
                'pages': 376,
                'language': 'Vietnamese',
                'isbn': '9786043390964',
                'genre': 'Self-help / Productivity',
                'year': 2023,
            },
        },
    ],

    # ─────────────────────────────────────────────────────────────────────────
    # 7. THE THAO (Sports)
    #    attributes: sport_type, size/weight, material, level, gender
    # ─────────────────────────────────────────────────────────────────────────
    'the-thao': [
        {
            'name': 'Yonex Astrox 88D Pro Badminton Racket',
            'description': 'Professional badminton racket 4U, Rotational Generator System.',
            'price': 4290000,
            'stock': 45,
            'brand_slug': 'yonex',
            'image_url': 'https://yonex.com/astrox-88d-pro.jpg',
            'attributes': {
                'sport': 'Badminton',
                'weight': '4U (80-84g)',
                'balance': 'Head-heavy',
                'flex': 'Stiff',
                'material': 'High Modulus Graphite',
                'level': 'Professional',
                'max_tension': '30 lbs',
                'country': 'Japan',
            },
        },
        {
            'name': 'Nike React Infinity Run Flyknit 3',
            'description': 'Running shoe with React foam for maximum energy return, injury reduction.',
            'price': 3290000,
            'stock': 70,
            'brand_slug': 'nike',
            'image_url': 'https://static.nike.com/react-infinity-run-fk3.png',
            'attributes': {
                'sport': 'Running',
                'size': '43',
                'color': 'Blue / White',
                'material': 'Flyknit upper + React foam sole',
                'weight': '279g (size 10)',
                'gender': 'Male',
                'drop': '9mm heel-to-toe drop',
                'surface': 'Road',
            },
        },
        {
            'name': 'Adidas Predator League FG Football Boot',
            'description': 'Football boots with Zone Skin texture for better ball control.',
            'price': 2190000,
            'stock': 55,
            'brand_slug': 'adidas',
            'image_url': 'https://assets.adidas.com/predator-league-fg.jpg',
            'attributes': {
                'sport': 'Football',
                'size': '43',
                'color': 'Black / Gold',
                'material': 'Synthetic upper',
                'upper': 'Zone Skin texture',
                'sole': 'FG (Firm Ground)',
                'gender': 'Male',
                'country': 'China',
            },
        },
    ],

    # ─────────────────────────────────────────────────────────────────────────
    # 8. DO CHOI (Toy)
    #    attributes: age_range, material, pieces, theme, brand
    # ─────────────────────────────────────────────────────────────────────────
    'do-choi': [
        {
            'name': 'LEGO City Police Station 60316',
            'description': 'LEGO City Police Station with 5 minifigures, vehicles, and accessories.',
            'price': 2490000,
            'stock': 35,
            'brand_slug': 'lego',
            'image_url': 'https://www.lego.com/city-police-station-60316.jpg',
            'attributes': {
                'pieces': 668,
                'age_range': '6+ years',
                'theme': 'LEGO City',
                'minifigures': 5,
                'material': 'ABS plastic',
                'set_number': '60316',
                'country': 'Denmark',
                'gender': 'Unisex',
            },
        },
        {
            'name': 'Barbie Dreamhouse 2023',
            'description': 'Barbie Dreamhouse 3-story with elevator, pool, and 75 accessories.',
            'price': 3990000,
            'stock': 20,
            'brand_slug': 'mattel',
            'image_url': 'https://www.mattel.com/barbie-dreamhouse-2023.jpg',
            'attributes': {
                'height': '120 cm',
                'floors': 3,
                'rooms': 8,
                'accessories': 75,
                'age_range': '3+ years',
                'material': 'ABS plastic',
                'includes': 'Elevator, pool, slide',
                'gender': 'Female',
            },
        },
        {
            'name': 'LEGO Technic Bugatti Bolide 42151',
            'description': 'LEGO Technic Bugatti Bolide racing car replica with 905 pieces.',
            'price': 1890000,
            'stock': 25,
            'brand_slug': 'lego',
            'image_url': 'https://www.lego.com/technic-bugatti-bolide.jpg',
            'attributes': {
                'pieces': 905,
                'age_range': '10+ years',
                'theme': 'LEGO Technic',
                'scale': '1:8',
                'material': 'ABS plastic',
                'set_number': '42151',
                'features': 'Steering, W16 engine replica',
                'gender': 'Unisex',
            },
        },
    ],

    # ─────────────────────────────────────────────────────────────────────────
    # 9. PHU KIEN (Accessories)
    #    attributes: compatibility, connectivity, battery, color, warranty
    # ─────────────────────────────────────────────────────────────────────────
    'phu-kien': [
        {
            'name': 'Apple AirPods Pro 2nd Gen',
            'description': 'Active Noise Cancellation, Adaptive Transparency, H2 chip, MagSafe.',
            'price': 6490000,
            'stock': 80,
            'brand_slug': 'apple',
            'image_url': 'https://store.storeimages.cdn-apple.com/airpods-pro-2.jpg',
            'attributes': {
                'type': 'In-ear TWS',
                'chip': 'Apple H2',
                'anc': True,
                'battery_bud': '6 hours (ANC on)',
                'battery_case': '30 hours total',
                'connectivity': 'Bluetooth 5.3',
                'water_resistant': 'IPX4',
                'charging': 'MagSafe / Lightning / USB-C',
                'compatibility': 'iPhone, iPad, Mac',
                'color': 'White',
            },
        },
        {
            'name': 'Apple Watch Series 9 45mm',
            'description': 'Apple Watch with S9 chip, Double Tap gesture, Always-On display.',
            'price': 11990000,
            'stock': 40,
            'brand_slug': 'apple',
            'image_url': 'https://store.storeimages.cdn-apple.com/apple-watch-s9.jpg',
            'attributes': {
                'size': '45mm',
                'chip': 'Apple S9',
                'display': 'Always-On LTPO OLED',
                'battery': 'Up to 18 hours',
                'water_resistant': '50m (WR50)',
                'health': ['ECG', 'Blood O2', 'Heart rate', 'Crash detection'],
                'connectivity': 'GPS + Cellular',
                'color': 'Midnight Aluminum',
                'compatibility': 'iPhone XS or later',
            },
        },
        {
            'name': 'Samsung Galaxy Buds2 Pro',
            'description': 'Samsung earbuds with 3-mic ANC, Hi-Fi 24-bit audio, ergonomic design.',
            'price': 3490000,
            'stock': 65,
            'brand_slug': 'samsung',
            'image_url': 'https://images.samsung.com/galaxy-buds2-pro.jpg',
            'attributes': {
                'type': 'In-ear TWS',
                'anc': True,
                'audio': '24-bit Hi-Fi',
                'battery_bud': '5 hours (ANC on)',
                'battery_case': '18 hours total',
                'connectivity': 'Bluetooth 5.3',
                'water_resistant': 'IPX7',
                'charging': 'USB-C / Wireless',
                'compatibility': 'Android (best with Samsung)',
                'color': 'Bora Purple',
            },
        },
    ],

    # ─────────────────────────────────────────────────────────────────────────
    # 10. THUC PHAM (Food)
    #     attributes: weight/volume, ingredients, expiry, storage, country
    # ─────────────────────────────────────────────────────────────────────────
    'thuc-pham': [
        {
            'name': 'Trung Nguyen G7 3-in-1 Instant Coffee (50 packs)',
            'description': 'Iconic Vietnamese instant coffee G7 with coffee + milk + sugar.',
            'price': 95000,
            'stock': 500,
            'brand_slug': 'trung-nguyen',
            'image_url': 'https://trung-nguyen.com/g7-3in1.jpg',
            'attributes': {
                'weight': '850g (50 x 17g)',
                'packs': 50,
                'ingredients': 'Instant coffee, creamer, sugar',
                'caffeine': 'Approx 100mg per serving',
                'expiry': '18 months',
                'storage': 'Cool, dry place',
                'country': 'Vietnam',
                'type': '3-in-1 instant coffee',
            },
        },
        {
            'name': 'Vinamilk Organic Fresh Milk 1L',
            'description': '100% organic fresh milk from certified organic farms, no preservatives.',
            'price': 42000,
            'stock': 400,
            'brand_slug': 'trung-nguyen',   # Using available brand as placeholder
            'image_url': 'https://vinamilk.com.vn/organic-fresh-milk.jpg',
            'attributes': {
                'volume': '1000ml',
                'fat': '3.5%',
                'protein': '3.2%',
                'ingredients': 'Organic fresh milk 100%',
                'preservatives': False,
                'expiry': '7 days (refrigerated)',
                'storage': '2-8 degrees C',
                'country': 'Vietnam',
                'certification': 'USDA Organic',
            },
        },
        {
            'name': "Orion Choco Pie Original (12 packs)",
            'description': 'Korean classic soft chocolate marshmallow pie, 12 individually wrapped.',
            'price': 55000,
            'stock': 350,
            'brand_slug': 'trung-nguyen',   # Using available brand as placeholder
            'image_url': 'https://orion.net/choco-pie.jpg',
            'attributes': {
                'weight': '468g (12 x 39g)',
                'packs': 12,
                'ingredients': 'Wheat flour, sugar, chocolate coating, marshmallow',
                'allergens': ['Wheat', 'Milk', 'Eggs', 'Soy'],
                'expiry': '9 months',
                'storage': 'Cool, dry place below 27C',
                'country': 'South Korea',
                'type': 'Confectionery / Snack',
            },
        },
    ],
}


class Command(BaseCommand):
    help = 'Seed sample products for all 10 product type categories (5 products/category)'
    TARGET_PER_CATEGORY = 5

    def _image_for(self, name):
                import base64
                safe_name = name[:26]
                svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="800" viewBox="0 0 600 800">
    <defs>
        <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="#0f172a"/>
            <stop offset="100%" stop-color="#1d4ed8"/>
        </linearGradient>
    </defs>
    <rect width="600" height="800" fill="url(#g)"/>
    <circle cx="480" cy="120" r="110" fill="rgba(255,255,255,0.08)"/>
    <circle cx="120" cy="640" r="150" fill="rgba(255,255,255,0.06)"/>
    <text x="50%" y="43%" text-anchor="middle" font-family="Arial, sans-serif" font-size="34" font-weight="700" fill="#f8fafc">Bookstore</text>
    <text x="50%" y="52%" text-anchor="middle" font-family="Arial, sans-serif" font-size="26" font-weight="600" fill="#dbeafe">{safe_name}</text>
    <text x="50%" y="90%" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" fill="#bfdbfe">Catalog image</text>
</svg>'''
                encoded = base64.b64encode(svg.encode('utf-8')).decode('utf-8')
                return f"data:image/svg+xml;base64,{encoded}"

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing products in seeded categories before seeding',
        )

    def _safe_write(self, msg):
        try:
            self.stdout.write(msg)
        except UnicodeEncodeError:
            self.stdout.write(msg.encode('ascii', errors='replace').decode('ascii'))

    def _expand_products(self, products, target, cat_slug):
        if not products:
            return []

        expanded = []
        idx = 0
        base_count = len(products)

        while len(expanded) < target:
            base = products[idx % base_count]
            item = copy.deepcopy(base)
            variant_no = (idx // base_count) + 1

            if variant_no == 1:
                item['name'] = base['name']
            else:
                item['name'] = f"{base['name']} - Variant {variant_no}"
            # Tạo biến thể giá/tồn kho nhẹ để data đa dạng hơn
            item['price'] = int(base['price'] + (variant_no - 1) * 10000)
            item['stock'] = int(base['stock'] + (variant_no - 1) * 2)

            attrs = item.get('attributes', {})
            if isinstance(attrs, dict):
                attrs['variant'] = variant_no
            item['attributes'] = attrs
            
            # Map each product to its respective premium Unsplash URL that matches it
            name_lower = item['name'].lower()
            
            if 'iphone' in name_lower:
                item['image_url'] = 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=600&q=80'
            elif 'samsung' in name_lower or 'galaxy' in name_lower:
                if 'buds' in name_lower:
                    item['image_url'] = 'https://images.unsplash.com/photo-1606220588913-b3aacb4d2f46?w=600&q=80'
                else:
                    item['image_url'] = 'https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=600&q=80'
            elif 'xiaomi' in name_lower:
                if 'purifier' in name_lower or 'purify' in name_lower:
                    item['image_url'] = 'https://images.unsplash.com/photo-1585338107529-13afc5f02586?w=600&q=80'
                else:
                    item['image_url'] = 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=600&q=80'
            elif 'macbook' in name_lower:
                item['image_url'] = 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=600&q=80'
            elif 'xps' in name_lower:
                item['image_url'] = 'https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=600&q=80'
            elif 'rog' in name_lower or 'zephyrus' in name_lower:
                item['image_url'] = 'https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=600&q=80'
            elif 'nike' in name_lower:
                if 'infinity' in name_lower or 'run' in name_lower:
                    item['image_url'] = 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&q=80'
                else:
                    item['image_url'] = 'https://images.unsplash.com/photo-1600185365483-26d7a4cc7519?w=600&q=80'
            elif 'adidas' in name_lower:
                if 'predator' in name_lower:
                    item['image_url'] = 'https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=600&q=80'
                else:
                    item['image_url'] = 'https://images.unsplash.com/photo-1491553895911-0055eca6402d?w=600&q=80'
            elif 'uniqlo' in name_lower or 'polo' in name_lower:
                item['image_url'] = 'https://images.unsplash.com/photo-1581655353564-df123a1eb820?w=600&q=80'
            elif 'l\'oreal' in name_lower or 'revitalift' in name_lower:
                item['image_url'] = 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=600&q=80'
            elif 'anessa' in name_lower:
                item['image_url'] = 'https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?w=600&q=80'
            elif 'mac' in name_lower and 'lipstick' in name_lower:
                item['image_url'] = 'https://images.unsplash.com/photo-1586495777744-4413f21062fa?w=600&q=80'
            elif 'philips' in name_lower and 'cooker' in name_lower:
                item['image_url'] = 'https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?w=600&q=80'
            elif 'panasonic' in name_lower and 'microwave' in name_lower:
                item['image_url'] = 'https://images.unsplash.com/photo-1574269909862-7e1d70bb8078?w=600&q=80'
            elif 'dac nhan tam' in name_lower or 'nha gia kim' in name_lower or 'atomic habits' in name_lower:
                item['image_url'] = 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=600&q=80'
            elif 'yonex' in name_lower or 'racket' in name_lower:
                item['image_url'] = 'https://images.unsplash.com/photo-1626224583764-f87db24ac4ea?w=600&q=80'
            elif 'lego' in name_lower:
                item['image_url'] = 'https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=600&q=80'
            elif 'barbie' in name_lower or 'dreamhouse' in name_lower:
                item['image_url'] = 'https://images.unsplash.com/photo-1559082246-3f5502af2c0d?w=600&q=80'
            elif 'airpods' in name_lower:
                item['image_url'] = 'https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=600&q=80'
            elif 'watch' in name_lower:
                item['image_url'] = 'https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=600&q=80'
            elif 'coffee' in name_lower or 'g7' in name_lower or 'orion' in name_lower or 'choco' in name_lower:
                item['image_url'] = 'https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=600&q=80'
            elif 'vinamilk' in name_lower or 'milk' in name_lower:
                item['image_url'] = 'https://images.unsplash.com/photo-1563636619-e9143da7973b?w=600&q=80'
            else:
                # Category fallbacks
                if 'dien-thoai' in cat_slug:
                    item['image_url'] = 'https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=600&q=80'
                elif 'laptop' in cat_slug:
                    item['image_url'] = 'https://images.unsplash.com/photo-1531297484001-80022131f5a1?w=600&q=80'
                elif 'thoi-trang' in cat_slug:
                    item['image_url'] = 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&q=80'
                elif 'my-pham' in cat_slug:
                    item['image_url'] = 'https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=600&q=80'
                elif 'do-gia-dung' in cat_slug:
                    item['image_url'] = 'https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?w=600&q=80'
                elif 'sach' in cat_slug:
                    item['image_url'] = 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=600&q=80'
                elif 'the-thao' in cat_slug:
                    item['image_url'] = 'https://images.unsplash.com/photo-1517649763962-0c623066013b?w=600&q=80'
                elif 'do-choi' in cat_slug:
                    item['image_url'] = 'https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=600&q=80'
                elif 'phu-kien' in cat_slug:
                    item['image_url'] = 'https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=600&q=80'
                elif 'thuc-pham' in cat_slug:
                    item['image_url'] = 'https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=600&q=80'
                else:
                    item['image_url'] = self._image_for(item['name'])

            expanded.append(item)
            idx += 1

        return expanded

    def handle(self, *args, **options):
        self._safe_write('=== Seeding products for 10 product types ===\n')
        do_reset = options.get('reset', False)

        total_created = 0
        total_exists = 0

        for cat_slug, products in PRODUCTS_BY_CATEGORY.items():
            # Lookup category
            try:
                category = CategoryModel.objects.get(slug=cat_slug)
            except CategoryModel.DoesNotExist:
                self._safe_write(
                    self.style.WARNING(
                        f"[SKIP] Category '{cat_slug}' not found. "
                        f"Run 'python manage.py seed_categories' first."
                    )
                )
                continue

            deleted_count, _ = ProductModel.objects.filter(category=category).delete()
            self._safe_write(f"  [RESET] Deleted {deleted_count} existing products in category '{cat_slug}'")

            expanded_products = self._expand_products(products, self.TARGET_PER_CATEGORY, cat_slug)

            self._safe_write(f'\n[{cat_slug.upper()}] ({len(expanded_products)} products)')

            for i, p in enumerate(expanded_products, 1):
                # Lookup brand
                brand = None
                if p.get('brand_slug'):
                    try:
                        brand = BrandModel.objects.get(slug=p['brand_slug'])
                    except BrandModel.DoesNotExist:
                        brand = None

                obj, created = ProductModel.objects.update_or_create(
                    name=p['name'],
                    defaults={
                        'description': p['description'],
                        'price': p['price'],
                        'stock': p['stock'],
                        'category': category,
                        'brand': brand,
                        'image_url': p.get('image_url', ''),
                        'attributes': p['attributes'],
                        'is_active': True,
                    },
                )

                label = 'Created' if created else 'Exists'
                if created:
                    total_created += 1
                else:
                    total_exists += 1

                self._safe_write(
                    f'  [{i}] [{label}] {p["name"]}'
                    f' | {p["price"]:,} VND | stock={p["stock"]}'
                )

        self._safe_write(self.style.SUCCESS(
            f'\n=== Done! Created: {total_created}, Already existed: {total_exists} ==='
        ))
        per_cat = self.TARGET_PER_CATEGORY
        self._safe_write(
            f'\nSummary: {total_created + total_exists} total products across 10 categories\n'
            f'  dien-thoai  (Phone)      : {per_cat} products\n'
            f'  laptop      (Laptop)     : {per_cat} products\n'
            f'  thoi-trang  (Fashion)    : {per_cat} products\n'
            f'  my-pham     (Cosmetic)   : {per_cat} products\n'
            f'  do-gia-dung (Appliance)  : {per_cat} products\n'
            f'  sach        (Book)       : {per_cat} products\n'
            f'  the-thao    (Sports)     : {per_cat} products\n'
            f'  do-choi     (Toy)        : {per_cat} products\n'
            f'  phu-kien    (Accessories): {per_cat} products\n'
            f'  thuc-pham   (Food)       : {per_cat} products\n'
        )
