# Product Service - Thiết kế theo DDD Cách 2

## Tổng quan

Product Service là **một microservice duy nhất** quản lý toàn bộ danh mục sản phẩm theo **DDD Cách 2**:

> **"1 Product Service duy nhất. Category là dữ liệu. Không tách theo loại sản phẩm."**

## Cách 2 vs Cách 1

| Tiêu chí | Cách 1 (Tách riêng) | Cách 2 (Product Service) ✅ |
|---|---|---|
| DDD | ❌ Sai | ✅ Đúng |
| Maintain | Khó | Dễ |
| Scale | Kém | Tốt |
| Tái sử dụng | Thấp | Cao |

**Cách 1 (KHÔNG dùng):** PhoneService + LaptopService + FashionService + ...

**Cách 2 (ĐANG dùng):**
```
ProductService
├─ Dien thoai (Phone)       ← category là DATA
├─ Laptop                   ← category là DATA
├─ Thoi trang (Fashion)     ← category là DATA
├─ My pham (Cosmetic)       ← category là DATA
├─ Do gia dung (Appliance)  ← category là DATA
├─ Sach (Book)              ← category là DATA
├─ The thao (Sports)        ← category là DATA
├─ Do choi (Toy)            ← category là DATA
├─ Phu kien (Accessories)   ← category là DATA
└─ Thuc pham (Food)         ← category là DATA
```

## Cấu trúc thư mục (DDD 4 Layer)

```
product-service/
├── manage.py
├── requirements.txt           django, djangorestframework, django-cors-headers
├── Dockerfile
├── AGENTS.md
│
├── config/                          # Configuration layer
│   ├── settings/
│   │   ├── base.py                  # Base settings
│   │   ├── dev.py                   # Development - SQLite
│   │   └── prod.py                  # Production - PostgreSQL
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
└── modules/
    └── catalog/                     # Bounded Context duy nhất
        │
        ├── domain/                  # ① DOMAIN LAYER (pure Python)
        │   ├── entities/
        │   │   ├── product.py       # Aggregate Root - Product
        │   │   ├── category.py      # Category (là DỮ LIỆU, không phải service)
        │   │   └── brand.py
        │   ├── value_objects/
        │   │   ├── money.py         # Immutable Money VO
        │   │   └── attributes.py    # Flexible JSONB Attributes VO
        │   └── repositories/        # Abstract interfaces (Ports)
        │       ├── product_repository.py
        │       └── category_repository.py
        │
        ├── application/             # ② APPLICATION LAYER (use cases)
        │   ├── commands/
        │   │   ├── create_product.py
        │   │   └── update_product.py
        │   ├── queries/
        │   │   └── product_queries.py
        │   └── services/
        │       └── product_service.py
        │
        ├── infrastructure/          # ③ INFRASTRUCTURE LAYER (ORM)
        │   ├── models/
        │   │   └── product_model.py  # BrandModel, CategoryModel, ProductModel
        │   └── repositories/
        │       ├── product_repository_impl.py
        │       └── category_repository_impl.py
        │
        ├── presentation/            # ④ PRESENTATION LAYER (REST API)
        │   └── api/
        │       ├── views/
        │       │   ├── product_view.py
        │       │   └── category_view.py
        │       ├── serializers/
        │       │   └── product_serializer.py
        │       └── urls.py
        │
        ├── management/commands/     # Seed data
        │   ├── seed_categories.py   # 10 product type categories
        │   └── seed_products.py     # 3 products × 10 categories = 30 products
        │
        ├── tests/
        └── admin.py
```

## 10 Loại sản phẩm (Product Types)

| # | Slug | Tên | Ví dụ sản phẩm |
|---|------|-----|----------------|
| 1 | `dien-thoai` | Điện thoại | iPhone 15, Samsung S24, Xiaomi 14 |
| 2 | `laptop` | Laptop | MacBook Pro M4, Dell XPS 15, ASUS ROG |
| 3 | `thoi-trang` | Thời trang | Nike AF1, Adidas Ultraboost, Uniqlo Polo |
| 4 | `my-pham` | Mỹ phẩm | L'Oreal Serum, Anessa SPF50+, MAC Lipstick |
| 5 | `do-gia-dung` | Đồ gia dụng | Philips Rice Cooker, Xiaomi Air Purifier |
| 6 | `sach` | Sách | Đắc Nhân Tâm, Nhà Giả Kim, Atomic Habits |
| 7 | `the-thao` | Thể thao | Yonex Racket, Nike Run, Adidas Football |
| 8 | `do-choi` | Đồ chơi | LEGO City, Barbie Dreamhouse, LEGO Technic |
| 9 | `phu-kien` | Phụ kiện | AirPods Pro, Apple Watch S9, Galaxy Buds2 |
| 10 | `thuc-pham` | Thực phẩm | G7 Coffee, Vinamilk Organic, Choco Pie |

## Database Schema

```sql
-- Category là DỮ LIỆU - 10 product types trong 1 bảng
CREATE TABLE categories (
    id          SERIAL PRIMARY KEY,
    name        TEXT NOT NULL,
    slug        TEXT UNIQUE NOT NULL,  -- 'dien-thoai', 'laptop', 'thoi-trang', ...
    description TEXT,
    parent_id   INT REFERENCES categories(id),
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMP
);

CREATE TABLE brands (
    id   SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    slug TEXT UNIQUE NOT NULL
);

-- 1 bảng products cho TẤT CẢ 10 loại sản phẩm
CREATE TABLE products (
    id          SERIAL PRIMARY KEY,
    name        TEXT NOT NULL,
    description TEXT,
    price       NUMERIC(14,2),
    stock       INT DEFAULT 0,
    category_id INT REFERENCES categories(id),  -- dien-thoai? laptop? sach?
    brand_id    INT REFERENCES brands(id),
    attributes  JSONB DEFAULT '{}',              -- linh hoạt theo từng loại!
    image_url   TEXT,
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMP,
    updated_at  TIMESTAMP
);
```

### Attributes JSONB theo từng loại

```json
// Phone:   {"ram":"8GB", "storage":"256GB", "os":"iOS 17", "chip":"A17 Pro"}
// Laptop:  {"ram":"16GB", "cpu":"Apple M4", "gpu":"10-core", "screen":"14.2 inch"}
// Fashion: {"size":"42", "color":"White", "material":"Leather", "gender":"Unisex"}
// Cosmetic:{"volume":"30ml", "spf":"SPF50+", "skin_type":"All", "country":"Japan"}
// Book:    {"author":"Dale Carnegie", "pages":320, "isbn":"...", "genre":"Self-help"}
// Sports:  {"sport":"Badminton", "weight":"4U", "flex":"Stiff", "level":"Pro"}
// Toy:     {"pieces":668, "age_range":"6+", "theme":"LEGO City", "minifigures":5}
// Access.: {"anc":true, "battery":"6h", "connectivity":"BT5.3", "waterproof":"IPX4"}
// Food:    {"weight":"850g", "packs":50, "expiry":"18 months", "country":"Vietnam"}
```

## API Endpoints

| Method | URL | Mô tả |
|--------|-----|--------|
| `GET`  | `/products/` | Tất cả sản phẩm (filter: category_id, brand_id, price) |
| `POST` | `/products/` | Tạo sản phẩm mới |
| `GET`  | `/products/<pk>/` | Chi tiết sản phẩm |
| `PUT`  | `/products/<pk>/` | Cập nhật sản phẩm |
| `DELETE` | `/products/<pk>/` | Ẩn sản phẩm (soft delete) |
| `GET`  | `/products/<pk>/stock/` | Kiểm tra tồn kho |
| `GET`  | `/categories/` | 10 loại danh mục |
| `POST` | `/categories/` | Tạo danh mục mới |
| `GET`  | `/categories/<pk>/products/` | Sản phẩm theo loại |

## Chạy Development

```bash
# 1. Cài đặt
pip install -r requirements.txt

# 2. Migrate database
python manage.py migrate --settings=config.settings.dev

# 3. Seed 10 loại danh mục
python manage.py seed_categories --settings=config.settings.dev

# 4. Seed ~30 sản phẩm mẫu (3 sản phẩm × 10 loại)
python manage.py seed_products --settings=config.settings.dev

# 5. (Tuỳ chọn) Tạo superuser cho Django Admin
python manage.py createsuperuser --settings=config.settings.dev

# 6. Chạy server
python manage.py runserver 0.0.0.0:8005 --settings=config.settings.dev
```

## Ví dụ Query

```bash
# Lấy toàn bộ điện thoại
GET /categories/   → xem id của 'dien-thoai'
GET /products/?category_id=<id>

# Lấy laptop giá từ 40 triệu
GET /products/?category_id=<laptop_id>&min_price=40000000

# Kiểm tra tồn kho (cart-service / order-service dùng)
GET /products/1/stock/
```
