# PHÂN TÍCH YÊU CẦU HỆ THỐNG ECOMMERCE

## 1. TỔNG QUAN HỆ THỐNG

### 1.1 Kiến trúc Microservice
Hệ thống được thiết kế theo mô hình **microservice architecture** với các thành phần:

- **API Gateway** (Port 8000): Cổng vào chính, điều hướng request tới các service
- **14 Django Microservices**: Mỗi service quản lý một domain riêng biệt
- **Neo4j Database**: Cơ sở dữ liệu graph (chưa được triển khai)
- **Store-Front**: Frontend HTML/JavaScript tĩnh

### 1.2 Các Service chính
| Service | Port | Chức năng |
|---------|------|----------|
| customer-service | 8001 | Quản lý khách hàng, đăng ký/đăng nhập |
| book-service | 8002 | Quản lý sách, tồn kho sách |
| cart-service | 8003 | Quản lý giỏ hàng |
| staff-service | 8004 | Quản lý nhân viên |
| manager-service | 8005 | Quản lý hệ thống, báo cáo |
| catalog-service | 8006 | Quản lý danh mục sản phẩm |
| order-service | 8007 | Quản lý đơn hàng |
| ship-service | 8008 | Quản lý giao hàng, vận chuyển |
| pay-service | 8009 | Xử lý thanh toán |
| comment-rate-service | 8010 | Quản lý bình luận & đánh giá |
| recommender-ai-service | 8011 | Gợi ý sản phẩm dựa trên AI |
| electronic-service | 8012 | Quản lý sản phẩm điện tử |
| clothe-service | 8013 | Quản lý sản phẩm quần áo |
| product-service | 8014 | Quản lý sản phẩm chung (tổng hợp) |

---

## 2. YÊU CẦU CHỨC NĂNG - USE CASE

### 2.1 Nhóm Use Case: Khách hàng (Customer)

#### UC-01: Đăng ký tài khoản
**Actor**: Khách hàng mới
**Mô tả**: Người dùng nhập email, mật khẩu, họ tên để tạo tài khoản mới
**Luồng chính**:
1. Nhập email, password, tên
2. Hệ thống xác thực email không trùng lặp
3. Lưu thông tin vào customer-service
4. Cấp customer_id

#### UC-02: Đăng nhập
**Actor**: Khách hàng
**Mô tả**: Xác thực tài khoản và quản lý phiên đăng nhập
**Luồng chính**:
1. Nhập email & password
2. Xác thực với customer-service
3. Lưu customer_id, userName, userRole vào localStorage
4. Cấp quyền truy cập

#### UC-03: Xem danh mục sản phẩm
**Actor**: Bất kỳ người dùng
**Mô tả**: Duyệt sản phẩm theo danh mục
**Thực thể tham gia**: Catalog-service, Product-service
**Luồng chính**:
1. Yêu cầu danh mục từ catalog-service
2. Lấy sản phẩm từ product-service (tổng hợp từ book/electronic/clothe)
3. Hiển thị với giá, hình ảnh, đánh giá

#### UC-04: Tìm kiếm sản phẩm
**Actor**: Bất kỳ người dùng
**Mô tả**: Tìm kiếm sản phẩm theo từ khóa
**Luồng chính**:
1. Nhập từ khóa tìm kiếm
2. Truy vấn product-service (tìm trong sách, điện tử, quần áo)
3. Hiển thị kết quả

---

### 2.2 Nhóm Use Case: Giỏ hàng & Thanh toán (Cart & Order)

#### UC-05: Thêm sản phẩm vào giỏ hàng
**Actor**: Khách hàng đã đăng nhập
**Mô tả**: Thêm sản phẩm vào giỏ hàng
**Thực thể tham gia**: 
- Cart-service (quản lý giỏ)
- Book/Electronic/Clothe-service (kiểm tra tồn kho)
**Luồng chính**:
1. Chọn sản phẩm & số lượng
2. Kiểm tra tồn kho từ service tương ứng
3. Tạo/cập nhật Cart với customer_id
4. Thêm CartItem (product_type, product_id, quantity)

#### UC-06: Xem giỏ hàng
**Actor**: Khách hàng
**Luồng chính**:
1. Tải Cart theo customer_id
2. Hiển thị danh sách CartItem với tên, giá, số lượng
3. Tính tổng tiền

#### UC-07: Cập nhật giỏ hàng
**Actor**: Khách hàng
**Mô tả**: Thay đổi số lượng, xóa sản phẩm
**Luồng chính**:
1. Cập nhật quantity hoặc xóa CartItem
2. Tính lại tổng tiền

#### UC-08: Thanh toán (Checkout)
**Actor**: Khách hàng
**Mô tả**: Hoàn thành giao dịch mua hàng
**Thực thể tham gia**: Order, Pay-service, Ship-service, Recommender
**Luồng chính**:
1. Chọn phương thức thanh toán (pay_method)
2. Chọn phương thức giao hàng (ship_method)
3. Xác nhận đơn hàng
4. Tạo Order với status = "Pending"
5. Tạo OrderItem từ CartItem
6. Ghi nhận thanh toán trong pay-service
7. Xóa giỏ hàng
8. Recommender-service ghi nhận hành động mua hàng

#### UC-09: Theo dõi đơn hàng
**Actor**: Khách hàng
**Mô tả**: Xem trạng thái đơn hàng đã mua
**Luồng chính**:
1. Tải danh sách Order của customer
2. Hiển thị trạng thái: Pending → Processing → Shipped → Delivered
3. Xem chi tiết OrderItem (sản phẩm, số lượng, giá)

---

### 2.3 Nhóm Use Case: Đánh giá & Bình luận (Rating & Comment)

#### UC-10: Xem đánh giá sản phẩm
**Actor**: Bất kỳ người dùng
**Mô tả**: Xem bình luận & sao từ người mua khác
**Luồng chính**:
1. Chọn sản phẩm (product_type, product_id)
2. Tải danh sách Rating từ comment-rate-service
3. Hiển thị stars, comment, customer_id, ngày

#### UC-11: Thêm đánh giá sản phẩm
**Actor**: Khách hàng đã mua sản phẩm
**Mô tả**: Để lại sao & bình luận
**Luồng chính**:
1. Chọn sản phẩm & nhập sao (1-5)
2. Nhập bình luận tùy chọn
3. Lưu vào comment-rate-service
4. Ghi nhận customer_id & thời gian tạo

---

### 2.4 Nhóm Use Case: Gợi ý sản phẩm (Recommender AI)

#### UC-12: Nhận gợi ý sản phẩm
**Actor**: Khách hàng đã đăng nhập
**Mô tả**: Nhận danh sách sản phẩm được gợi ý dựa trên AI
**Luồng chính**:
1. Lấy lịch sử mua hàng của khách
2. Recommender-service phân tích chi tiêu xu hướng
3. Trả về danh sách sản phẩm tương tự
4. Hiển thị trên homepage

---

### 2.5 Nhóm Use Case: Nhân viên & Quản trị (Staff & Admin)

#### UC-13: Đăng nhập nhân viên
**Actor**: Nhân viên, Quản trị viên
**Mô tả**: Đăng nhập vào dashboard quản trị
**Luồng chính**:
1. Nhập email & password
2. Xác thực với staff-service
3. Kiểm tra role (staff hoặc admin)
4. Cấp quyền truy cập quản trị

#### UC-14: Quản lý sản phẩm
**Actor**: Quản trị viên (admin)
**Mô tả**: Thêm/sửa/xóa sản phẩm
**Luồng chính**:
1. Truy cập dashboard quản trị
2. Thêm sản phẩm mới (book/electronic/clothe)
3. Cập nhật giá, tồn kho, mô tả
4. Xóa sản phẩm (nếu cần)
5. Dữ liệu lưu trong service tương ứng

#### UC-15: Quản lý đơn hàng
**Actor**: Quản trị viên
**Mô tả**: Xem & cập nhật trạng thái đơn hàng
**Luồng chính**:
1. Xem danh sách Order
2. Cập nhật status (Pending → Processing → Shipped → Delivered)
3. Thông báo cho khách hàng

#### UC-16: Quản lý giao hàng
**Actor**: Nhân viên giao hàng
**Mô tả**: Cập nhật tình trạng giao hàng
**Luồng chính**:
1. Lấy danh sách Order với status = "Shipped"
2. Cập nhật thông tin giao hàng (địa chỉ, trạng thái)
3. Đánh dấu hoàn thành

#### UC-17: Xem báo cáo
**Actor**: Quản trị viên (manager)
**Mô tả**: Xem thống kê doanh số, chi phí, ...
**Luồng chính**:
1. Truy cập manager-service
2. Xem báo cáo doanh số theo ngày/tháng
3. Xem thống kê sản phẩm bán chạy

---

## 3. DANH SÁCH CÁC BẢNG (ENTITIES)

### 3.1 Customer Service

#### Bảng: Customer
| Trường | Kiểu dữ liệu | Ràng buộc | Mô tả |
|--------|-------------|----------|-------|
| id | INT | PK, AUTO_INCREMENT | Mã khách hàng |
| name | VARCHAR(255) | NOT NULL | Tên khách hàng |
| email | VARCHAR(255) | UNIQUE, NOT NULL | Email (dùng để đăng nhập) |
| password | VARCHAR(255) | NOT NULL | Mật khẩu (hash) |
| phone | VARCHAR(15) | NULLABLE | Số điện thoại |
| address | TEXT | NULLABLE | Địa chỉ nhà |
| created_at | DATETIME | NOT NULL | Ngày tạo tài khoản |

**Ràng buộc**:
- Email phải unique
- Password phải được hash
- Email hợp lệ

**Relationship**:
- 1 Customer → N Order (một khách có nhiều đơn hàng)
- 1 Customer → 1 Cart
- 1 Customer → N Rating

---

### 3.2 Book Service

#### Bảng: Book
| Trường | Kiểu dữ liệu | Ràng buộc | Mô tả |
|--------|-------------|----------|-------|
| id | INT | PK, AUTO_INCREMENT | Mã sách |
| title | VARCHAR(255) | NOT NULL | Tên sách |
| author | VARCHAR(255) | NOT NULL | Tác giả |
| price | DECIMAL(10,2) | NOT NULL | Giá bán |
| stock | INT | DEFAULT 0 | Tồn kho |
| category_id | INT | NULLABLE | Mã danh mục (từ catalog-service) |
| image_url | VARCHAR(500) | NULLABLE | URL hình ảnh |

**Ràng buộc**:
- price > 0
- stock >= 0

---

### 3.3 Electronic Service

#### Bảng: Electronic
| Trường | Kiểu dữ liệu | Ràng buộc | Mô tả |
|--------|-------------|----------|-------|
| id | INT | PK, AUTO_INCREMENT | Mã sản phẩm |
| name | VARCHAR(255) | NOT NULL | Tên sản phẩm |
| brand | VARCHAR(100) | NOT NULL | Thương hiệu |
| model_number | VARCHAR(100) | NULLABLE | Mã model |
| category | VARCHAR(20) | NOT NULL | Danh mục: phone, laptop, tablet, tv, audio, camera, accessory, other |
| description | TEXT | NULLABLE | Mô tả chi tiết |
| price | DECIMAL(12,2) | NOT NULL | Giá (VNĐ) |
| image_url | VARCHAR(500) | NULLABLE | URL hình ảnh |
| stock | INT | DEFAULT 0 | Tồn kho |
| warranty_months | INT | DEFAULT 12 | Bảo hành (tháng) |
| is_active | BOOLEAN | DEFAULT True | Còn bán hay không |
| created_at | DATETIME | NOT NULL | Ngày tạo |

---

### 3.4 Clothe Service

#### Bảng: Clothing
| Trường | Kiểu dữ liệu | Ràng buộc | Mô tả |
|--------|-------------|----------|-------|
| id | INT | PK, AUTO_INCREMENT | Mã sản phẩm |
| name | VARCHAR(255) | NOT NULL | Tên quần áo |
| category | VARCHAR(20) | NOT NULL | shirt, tshirt, pants, shorts, dress, jacket, sportswear, underwear, accessory, other |
| size | VARCHAR(10) | NOT NULL | XS, S, M, L, XL, XXL, XXXL, freesize |
| gender | VARCHAR(10) | NOT NULL | male, female, unisex, kid |
| color | VARCHAR(50) | NULLABLE | Màu sắc |
| material | VARCHAR(100) | NULLABLE | Chất liệu (cotton, polyester, ...) |
| price | DECIMAL(12,2) | NOT NULL | Giá (VNĐ) |
| image_url | VARCHAR(500) | NULLABLE | URL hình ảnh |
| stock | INT | DEFAULT 0 | Tồn kho |
| is_active | BOOLEAN | DEFAULT True | Còn bán hay không |
| created_at | DATETIME | NOT NULL | Ngày tạo |

---

### 3.5 Cart Service

#### Bảng: Cart
| Trường | Kiểu dữ liệu | Ràng buộc | Mô tả |
|--------|-------------|----------|-------|
| id | INT | PK, AUTO_INCREMENT | Mã giỏ hàng |
| customer_id | INT | UNIQUE, NOT NULL, FK | Mã khách hàng (1 khách 1 giỏ) |

**Relationship**:
- 1 Cart → N CartItem
- Cart.customer_id → Customer.id

---

#### Bảng: CartItem
| Trường | Kiểu dữ liệu | Ràng buộc | Mô tả |
|--------|-------------|----------|-------|
| id | INT | PK, AUTO_INCREMENT | Mã item trong giỏ |
| cart_id | INT | NOT NULL, FK | Mã giỏ hàng |
| product_type | VARCHAR(20) | NOT NULL | book, electronic, clothe |
| product_id | INT | NOT NULL | Mã sản phẩm trong bảng tương ứng |
| book_id | INT | NULLABLE | (Backward compatibility - legacy) |
| quantity | INT | DEFAULT 1 | Số lượng |

**Ràng buộc**:
- quantity >= 1

**Relationship**:
- CartItem.cart_id → Cart.id
- CartItem.product_id → Book/Electronic/Clothing.id (tùy product_type)

---

### 3.6 Order Service

#### Bảng: Order
| Trường | Kiểu dữ liệu | Ràng buộc | Mô tả |
|--------|-------------|----------|-------|
| id | INT | PK, AUTO_INCREMENT | Mã đơn hàng |
| customer_id | INT | NOT NULL, FK | Mã khách hàng |
| total | DECIMAL(15,2) | DEFAULT 0 | Tổng tiền đơn hàng |
| ship_method | VARCHAR(100) | NULLABLE | Phương thức giao hàng |
| pay_method | VARCHAR(100) | NULLABLE | Phương thức thanh toán |
| status | VARCHAR(50) | DEFAULT 'Pending' | Pending, Processing, Shipped, Delivered |
| created_at | DATETIME | NOT NULL | Ngày tạo đơn |
| updated_at | DATETIME | NOT NULL | Ngày cập nhật cuối |

**Ràng buộc**:
- total >= 0
- status IN ('Pending', 'Processing', 'Shipped', 'Delivered')

**Relationship**:
- 1 Order → N OrderItem
- Order.customer_id → Customer.id

---

#### Bảng: OrderItem
| Trường | Kiểu dữ liệu | Ràng buộc | Mô tả |
|--------|-------------|----------|-------|
| id | INT | PK, AUTO_INCREMENT | Mã item trong đơn |
| order_id | INT | NOT NULL, FK | Mã đơn hàng |
| product_type | VARCHAR(20) | NOT NULL | book, electronic, clothe |
| product_id | INT | NOT NULL | Mã sản phẩm |
| book_id | INT | NULLABLE | (Legacy) |
| quantity | INT | NOT NULL | Số lượng mua |
| price | DECIMAL(15,2) | NOT NULL | Giá tại thời điểm mua (snapshot) |

**Ràng buộc**:
- quantity >= 1
- price >= 0

**Relationship**:
- OrderItem.order_id → Order.id

---

### 3.7 Comment Rate Service

#### Bảng: Rating
| Trường | Kiểu dữ liệu | Ràng buộc | Mô tả |
|--------|-------------|----------|-------|
| id | INT | PK, AUTO_INCREMENT | Mã bình luận |
| product_type | VARCHAR(20) | NOT NULL | book, electronic, clothe |
| product_id | INT | NOT NULL | Mã sản phẩm |
| book_id | INT | NULLABLE | (Legacy) |
| customer_id | INT | NOT NULL, FK | Mã khách hàng đánh giá |
| stars | INT | NOT NULL | Điểm đánh giá (1-5) |
| comment | TEXT | NULLABLE | Nội dung bình luận |
| created_at | DATETIME | NOT NULL | Ngày tạo bình luận |

**Ràng buộc**:
- stars IN (1, 2, 3, 4, 5)

**Relationship**:
- Rating.customer_id → Customer.id
- Rating.product_id → Book/Electronic/Clothing.id (tùy product_type)

---

### 3.8 Staff Service

#### Bảng: Staff
| Trường | Kiểu dữ liệu | Ràng buộc | Mô tả |
|--------|-------------|----------|-------|
| id | INT | PK, AUTO_INCREMENT | Mã nhân viên |
| name | VARCHAR(255) | NOT NULL | Tên nhân viên |
| email | VARCHAR(255) | UNIQUE, NOT NULL | Email (đăng nhập) |
| password | VARCHAR(255) | NOT NULL | Mật khẩu (hash) |
| role | VARCHAR(50) | NOT NULL | staff, admin, manager |
| phone | VARCHAR(15) | NULLABLE | Số điện thoại |
| created_at | DATETIME | NOT NULL | Ngày tuyển dụng |

**Ràng buộc**:
- role IN ('staff', 'admin', 'manager')
- Email unique

---

### 3.9 Catalog Service
**Lưu ý**: File models.py rỗng, logic danh mục có thể được quản lý bởi product-service hoặc là enum/config

#### Bảng: Category (Dự kiến)
| Trường | Kiểu dữ liệu | Ràng buộc | Mô tả |
|--------|-------------|----------|-------|
| id | INT | PK | Mã danh mục |
| name | VARCHAR(100) | NOT NULL | Tên danh mục |
| parent_category_id | INT | NULLABLE | Danh mục cha (phân cấp) |

---

### 3.10 Ship Service
**Lưu ý**: File models.py rỗng

#### Bảng: Shipment (Dự kiến)
| Trường | Kiểu dữ liệu | Ràng buộc | Mô tả |
|--------|-------------|----------|-------|
| id | INT | PK | Mã vận chuyển |
| order_id | INT | NOT NULL, FK | Mã đơn hàng |
| status | VARCHAR(50) | NOT NULL | Pending, In Transit, Delivered |
| ship_address | TEXT | NOT NULL | Địa chỉ giao |
| ship_date | DATETIME | NULLABLE | Ngày giao |
| delivery_date | DATETIME | NULLABLE | Ngày nhận |

---

### 3.11 Pay Service
**Lưu ý**: File models.py rỗng

#### Bảng: Payment (Dự kiến)
| Trường | Kiểu dữ liệu | Ràng buộc | Mô tả |
|--------|-------------|----------|-------|
| id | INT | PK | Mã thanh toán |
| order_id | INT | NOT NULL, FK | Mã đơn hàng |
| amount | DECIMAL(15,2) | NOT NULL | Số tiền thanh toán |
| method | VARCHAR(50) | NOT NULL | credit_card, cash, ewallet |
| status | VARCHAR(50) | NOT NULL | Pending, Success, Failed |
| transaction_id | VARCHAR(100) | NULLABLE | Mã giao dịch |
| paid_at | DATETIME | NULLABLE | Ngày thanh toán |

---

### 3.12 Manager Service
**Lưu ý**: File models.py rỗng

#### Bảng: Report (Dự kiến)
| Trường | Kiểu dữ liệu | Ràng buộc | Mô tả |
|--------|-------------|----------|-------|
| id | INT | PK | Mã báo cáo |
| report_type | VARCHAR(50) | NOT NULL | sales, revenue, inventory |
| period | VARCHAR(20) | NOT NULL | daily, monthly, yearly |
| total_orders | INT | NULLABLE | Số đơn |
| total_revenue | DECIMAL(15,2) | NULLABLE | Doanh thu |
| report_date | DATE | NOT NULL | Ngày báo cáo |

---

### 3.13 Recommender AI Service
**Lưu ý**: File models.py rỗng

#### Bảng: UserPreference (Dự kiến)
| Trường | Kiểu dữ liệu | Ràng buộc | Mô tả |
|--------|-------------|----------|-------|
| id | INT | PK | Mã sở thích |
| customer_id | INT | NOT NULL, FK | Mã khách hàng |
| product_type | VARCHAR(20) | NOT NULL | Loại sản phẩm yêu thích |
| category | VARCHAR(100) | NULLABLE | Danh mục yêu thích |
| last_viewed_at | DATETIME | NULLABLE | Lần cuối xem |

#### Bảng: Recommendation (Dự kiến)
| Trường | Kiểu dữ liệu | Ràng buộc | Mô tả |
|--------|-------------|----------|-------|
| id | INT | PK | Mã gợi ý |
| customer_id | INT | NOT NULL, FK | Mã khách |
| product_type | VARCHAR(20) | NOT NULL | Loại sản phẩm |
| product_id | INT | NOT NULL | Mã sản phẩm gợi ý |
| score | FLOAT | NOT NULL | Điểm gợi ý (0-1) |
| created_at | DATETIME | NOT NULL | Ngày gợi ý |

---

## 4. THÔNG TIN CHO BIỂU ĐỒ LỚP (ENTITY RELATIONSHIP DIAGRAM)

### 4.1 Các lớp chính và thuộc tính

#### Lớp: Customer
**Attributes**:
- id: int
- name: string
- email: string (unique)
- password: string
- phone: string
- address: string
- created_at: datetime

**Methods**:
- register()
- login()
- getUserOrders()
- getCart()

---

#### Lớp: Product (Abstract/Base)
**Attributes**:
- id: int
- name: string
- price: decimal
- stock: int
- image_url: string
- created_at: datetime

**Methods**:
- getPrice()
- checkStock(quantity)
- decreaseStock(quantity)

**Subclasses**:
- Book (inherit: title, author, category_id)
- Electronic (inherit: brand, model, category, warranty_months)
- Clothing (inherit: size, gender, color, material)

---

#### Lớp: Cart
**Attributes**:
- id: int
- customer_id: int (unique)
- items: List<CartItem>

**Methods**:
- addItem(product_type, product_id, quantity)
- removeItem(cart_item_id)
- updateQuantity(cart_item_id, quantity)
- calculateTotal()
- getItems()

**Relationships**:
- has-many: CartItem
- belongs-to: Customer (1:1)

---

#### Lớp: CartItem
**Attributes**:
- id: int
- cart_id: int (FK)
- product_type: string (book, electronic, clothe)
- product_id: int
- quantity: int

**Methods**:
- getProduct()
- getSubtotal()
- updateQuantity()

**Relationships**:
- belongs-to: Cart
- belongs-to: Product (polymorphic)

---

#### Lớp: Order
**Attributes**:
- id: int
- customer_id: int (FK)
- items: List<OrderItem>
- total: decimal
- ship_method: string
- pay_method: string
- status: string (Pending, Processing, Shipped, Delivered)
- created_at: datetime
- updated_at: datetime

**Methods**:
- createOrder()
- calculateTotal()
- updateStatus(new_status)
- getOrderItems()
- canCancelOrder()

**Relationships**:
- has-many: OrderItem
- belongs-to: Customer
- has-one: Payment (optional)
- has-one: Shipment (optional)

---

#### Lớp: OrderItem
**Attributes**:
- id: int
- order_id: int (FK)
- product_type: string
- product_id: int
- quantity: int
- price: decimal (snapshot)

**Methods**:
- getProduct()
- getSubtotal()

**Relationships**:
- belongs-to: Order
- belongs-to: Product (polymorphic)

---

#### Lớp: Rating
**Attributes**:
- id: int
- customer_id: int (FK)
- product_type: string
- product_id: int
- stars: int (1-5)
- comment: string
- created_at: datetime

**Methods**:
- submitRating()
- editRating()
- deleteRating()

**Relationships**:
- belongs-to: Customer
- belongs-to: Product (polymorphic)

---

#### Lớp: Staff
**Attributes**:
- id: int
- name: string
- email: string (unique)
- password: string
- role: string (staff, admin, manager)
- phone: string
- created_at: datetime

**Methods**:
- login()
- hasPermission(action)
- getRole()

---

#### Lớp: Payment (Dự kiến)
**Attributes**:
- id: int
- order_id: int (FK)
- amount: decimal
- method: string (credit_card, cash, ewallet)
- status: string (Pending, Success, Failed)
- transaction_id: string
- paid_at: datetime

**Methods**:
- processPayment()
- refund()
- getPaymentStatus()

**Relationships**:
- belongs-to: Order (1:1)

---

#### Lớp: Shipment (Dự kiến)
**Attributes**:
- id: int
- order_id: int (FK)
- status: string
- ship_address: string
- ship_date: datetime
- delivery_date: datetime

**Methods**:
- updateShipmentStatus()
- trackShipment()

**Relationships**:
- belongs-to: Order (1:1)

---

### 4.2 Sơ đồ quan hệ (ERD)

```
Customer (1) ---- (N) Order
   |
   |---- (1) Cart (1) ---- (N) CartItem
   |                          |
   |                          +--> [Product] (polymorphic)
   |
   +----- (N) Rating
             |
             +--> [Product] (polymorphic)

Order (1) ---- (1) Payment (optional)
  |
  |----- (1) Shipment (optional)
  |
  +----- (N) OrderItem ---> [Product] (polymorphic)

[Product] <-- Book
         <-- Electronic
         <-- Clothing

Staff (nhiều) quản lý Product, Order, Customer
```

---

### 4.3 Mối quan hệ chính (Main Relationships)

| Từ | Đến | Mối quan hệ | Cardinality |
|-----|-----|-----------|-----------|
| Customer | Cart | has_one | 1:1 |
| Customer | Order | has_many | 1:N |
| Customer | Rating | has_many | 1:N |
| Cart | CartItem | has_many | 1:N |
| CartItem | Product | belongs_to (polymorphic) | N:1 |
| Order | OrderItem | has_many | 1:N |
| OrderItem | Product | belongs_to (polymorphic) | N:1 |
| Order | Payment | has_one (optional) | 1:1 |
| Order | Shipment | has_one (optional) | 1:1 |
| Rating | Product | belongs_to (polymorphic) | N:1 |
| Staff | [All entities] | manages | N:N |

---

### 4.4 Inheritance/Polymorphism

**Product** là lớp cha (Abstract):
- **Book** kế thừa (thêm: title, author, category_id)
- **Electronic** kế thừa (thêm: brand, model, category, warranty)
- **Clothing** kế thừa (thêm: size, gender, color, material)

**Polymorphism** áp dụng cho:
- `CartItem.product_type` + `CartItem.product_id` → xác định Product subclass
- `OrderItem.product_type` + `OrderItem.product_id` → xác định Product subclass
- `Rating.product_type` + `Rating.product_id` → xác định Product subclass

---

## 5. LUỒNG CHÍNH CỦA HỆ THỐNG

### 5.1 Luồng mua hàng (Happy Path)

```
1. Customer.register() → customer-service
2. Customer.login() → customer-service (localStorage: userId)
3. Browse products → book/electronic/clothe service
4. View product details + ratings → comment-rate-service
5. Add to cart → cart-service (CartItem)
6. View cart → cart-service
7. Submit order → order-service (Order + OrderItem)
8. Add payment info → pay-service
9. Process payment → pay-service
10. Order status = "Processing"
11. Assign shipping → ship-service (Shipment)
12. Update tracking → ship-service
13. Customer receives → ship-service (status = "Delivered")
14. Customer rates product → comment-rate-service (Rating)
15. Recommender learns from purchase → recommender-ai-service
```

---

### 5.2 Luồng quản trị

```
1. Staff.login() → staff-service (check role)
2. View dashboard → manager-service
3. Manage products → book/electronic/clothe service
4. Manage orders → order-service
5. Manage shipping → ship-service
6. View reports → manager-service
```

---

## 6. CONSTRAINTS & BUSINESS RULES

### 6.1 Ràng buộc dữ liệu
- **Email**: Unique, format hợp lệ
- **Password**: Hash trước lưu (không lưu plain text)
- **Stock**: >= 0, tks trừ khi mua hàng
- **Price**: > 0
- **Stars**: 1-5
- **Status**: Only valid values (Pending, Processing, ...)

### 6.2 Business Rules
1. Khách hàng chỉ có **1 giỏ hàng** (Cart)
2. Khi thanh toán, giỏ hàng phải **không rỗng**
3. Order chỉ có thể hủy khi status = **"Pending"**
4. Khi tạo Order, phải **kiểm tra tồn kho** của từng sản phẩm
5. Chỉ khách hàng **đã mua** mới có thể đánh giá sản phẩm
6. Rating chỉ lấy từ khách hàng **verified** (đã hoàn thành giao dịch)
7. Gợi ý sản phẩm dựa trên **lịch sử mua hàng** & **xem sản phẩm**

---

## 7. API ENDPOINTS (Tóm tắt)

### Customer Service (8001)
- `POST /api/customers/register` - Đăng ký
- `POST /api/customers/login` - Đăng nhập
- `GET /api/customers/<id>` - Lấy thông tin

### Cart Service (8003)
- `GET /api/carts/<customer_id>` - Xem giỏ hàng
- `POST /api/carts/<customer_id>/items` - Thêm item
- `PUT /api/carts/items/<item_id>` - Cập nhật quantity
- `DELETE /api/carts/items/<item_id>` - Xóa item

### Order Service (8007)
- `POST /api/orders` - Tạo order
- `GET /api/orders/<customer_id>` - Lấy danh sách order
- `GET /api/orders/<order_id>` - Chi tiết order
- `PUT /api/orders/<order_id>/status` - Cập nhật status

### Comment Rate Service (8010)
- `GET /api/ratings/<product_type>/<product_id>` - Xem ratings
- `POST /api/ratings` - Thêm rating

### Book Service (8002), Electronic Service (8012), Clothe Service (8013)
- `GET /api/<service_type>s` - Danh sách
- `GET /api/<service_type>s/<id>` - Chi tiết

---

## KẾT LUẬN

Hệ thống ecommerce được thiết kế theo kiến trúc **microservice** với **14 service riêng biệt**, mỗi service quản lý một domain cụ thể. Dữ liệu được phân tán, có **polymorphism** trên Product (Book/Electronic/Clothing).

**Các thực thể chính**: Customer, Product (và subclasses), Cart, Order, Rating, Staff

**Mối quan hệ quan trọng**: Customer → Cart/Order, Order → OrderItem → Product, Rating → Product

Hệ thống hỗ trợ **đơn hàng đầy đủ**: browse → cart → checkout → payment → shipping → delivery → rating
