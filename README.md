# Bookstore Microservice

Đây là dự án bán sách dạng microservice, chạy bằng Docker Compose với nhiều service Django và một Neo4j làm nền cho phần graph/RAG.

## Cần chuẩn bị

- Windows 10/11
- Docker Desktop
- Git
- Trình duyệt web để mở giao diện frontend

## Lưu ý quan trọng về ổ F

Nếu bạn không muốn Docker chiếm dung lượng ở ổ C, hãy chuyển toàn bộ dữ liệu Docker sang ổ F.

Sau khi cài Docker Desktop, mở **Settings** rồi tìm mục **Resources** hoặc **Advanced** và đổi **Disk image location** sang một thư mục trên ổ F, ví dụ:

`F:\DockerData`

Nên làm bước này trước khi pull image hoặc chạy `docker compose up` lần đầu.

## Cấu trúc chạy

- `neo4j`: cơ sở dữ liệu graph
- `api_gateway`: cổng vào chính của hệ thống
- `customer-service`, `book-service`, `cart-service`, `staff-service`, `manager-service`, `catalog-service`, `order-service`, `ship-service`, `pay-service`, `comment-rate-service`, `recommender-ai-service`, `electronic-service`, `clothe-service`, `product-service`, `healthcare-service`: các microservice Django
- `store-front`: giao diện HTML tĩnh

## Chạy dự án từ đầu

1. Cài Docker Desktop và trỏ Disk image location sang ổ F như hướng dẫn ở trên.
2. Mở PowerShell tại thư mục gốc dự án:

```powershell
cd F:\bookstore-microservice
```

3. Kiểm tra Docker đã chạy chưa:

```powershell
docker --version
docker compose version
```

4. Chạy toàn bộ hệ thống:

```powershell
docker compose up --build
```

5. Đợi các container khởi động xong. `product-service` sẽ tự migrate và seed dữ liệu ban đầu.

## Truy cập các service

- API Gateway: http://localhost:8000
- Customer Service: http://localhost:8001
- Book Service: http://localhost:8002
- Cart Service: http://localhost:8003
- Staff Service: http://localhost:8004
- Manager Service: http://localhost:8005
- Catalog Service: http://localhost:8006
- Order Service: http://localhost:8007
- Ship Service: http://localhost:8008
- Pay Service: http://localhost:8009
- Comment Rate Service: http://localhost:8010
- Recommender AI Service: http://localhost:8011
- Electronic Service: http://localhost:8012
- Clothe Service: http://localhost:8013
- Product Service: http://localhost:8014
- **Healthcare Service: http://localhost:8015**
  - Admin: http://localhost:8015/admin
  - Chat/Appointments: http://localhost/healthcare.html

## Neo4j

- Browser: http://localhost:7474
- Bolt: `bolt://localhost:7687`
- Tài khoản mặc định:
  - Username: `neo4j`
  - Password: `neo4jpassword`

## Frontend

Thư mục `store-front/` chứa giao diện HTML tĩnh. Bạn có thể:

- mở trực tiếp `store-front/index.html` bằng trình duyệt, hoặc
- dùng extension Live Server trong VS Code để chạy tiện hơn

## Dừng hệ thống

```powershell
docker compose down
```

Nếu muốn xóa luôn volume dữ liệu Neo4j:

```powershell
docker compose down -v
```

## Xem log

```powershell
docker compose logs -f api_gateway
docker compose logs -f neo4j
docker compose logs -f product-service
```

## Ghi chú

- Nếu container không lên được, hãy kiểm tra lại Docker Desktop đã dùng ổ F cho disk image chưa.
- Nếu cần chạy lại từ trạng thái sạch, dùng `docker compose down -v` rồi chạy lại `docker compose up --build`.