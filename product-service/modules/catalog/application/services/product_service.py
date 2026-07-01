"""
Product Application Service - Xử lý Use Cases.
Application layer: điều phối giữa Domain và Infrastructure.
Không chứa business logic (thuộc về Domain entity).
"""
from decimal import Decimal
from typing import Any, Dict, List, Optional

from modules.catalog.domain.entities.product import Product
from modules.catalog.domain.repositories.product_repository import ProductRepository
from modules.catalog.application.commands.create_product import CreateProductCommand
from modules.catalog.application.commands.update_product import UpdateProductCommand
from modules.catalog.application.queries.product_queries import (
    GetProductQuery, ListProductsQuery, CheckStockQuery
)


class ProductService:
    """
    Application Service cho Product.
    Theo DDD: orchestrate use cases, gọi domain entities và repositories.
    """

    def __init__(self, product_repository: ProductRepository):
        self._repo = product_repository

    # ─── Commands (Write) ───────────────────────────────────────────────────

    def create_product(self, command: CreateProductCommand) -> Product:
        """Use case: Tạo sản phẩm mới."""
        product = Product(
            id=None,
            name=command.name,
            description=command.description,
            price=Decimal(str(command.price)),
            stock=command.stock,
            category_id=command.category_id,
            brand_id=command.brand_id,
            attributes=command.attributes,
            image_url=command.image_url,
            is_active=True,
        )
        return self._repo.save(product)

    def update_product(self, command: UpdateProductCommand) -> Product:
        """Use case: Cập nhật sản phẩm."""
        product = self._repo.get_by_id(command.product_id)
        if product is None:
            raise ValueError(f"Sản phẩm với ID {command.product_id} không tồn tại.")

        if command.name is not None:
            product.name = command.name
        if command.description is not None:
            product.description = command.description
        if command.price is not None:
            product.price = Decimal(str(command.price))
        if command.stock is not None:
            product.stock = command.stock
        if command.category_id is not None:
            product.category_id = command.category_id
        if command.brand_id is not None:
            product.brand_id = command.brand_id
        if command.attributes is not None:
            product.attributes = command.attributes
        if command.image_url is not None:
            product.image_url = command.image_url
        if command.is_active is not None:
            product.is_active = command.is_active

        return self._repo.save(product)

    def deactivate_product(self, product_id: int) -> Product:
        """Use case: Ẩn sản phẩm (soft delete)."""
        product = self._repo.get_by_id(product_id)
        if product is None:
            raise ValueError(f"Sản phẩm với ID {product_id} không tồn tại.")
        product.deactivate()
        return self._repo.save(product)

    def decrease_stock(self, product_id: int, quantity: int) -> Product:
        """Use case: Giảm tồn kho (Order Service gọi khi đặt hàng)."""
        product = self._repo.get_by_id(product_id)
        if product is None:
            raise ValueError(f"Sản phẩm với ID {product_id} không tồn tại.")
        product.decrease_stock(quantity)
        return self._repo.save(product)

    # ─── Queries (Read) ─────────────────────────────────────────────────────

    def get_product(self, query: GetProductQuery) -> Optional[Product]:
        """Use case: Lấy chi tiết sản phẩm."""
        return self._repo.get_by_id(query.product_id)

    def list_products(self, query: ListProductsQuery) -> List[Product]:
        """Use case: Lấy danh sách sản phẩm với filter."""
        filters: Dict[str, Any] = {}
        if query.category_id is not None:
            filters['category_id'] = query.category_id
        if query.brand_id is not None:
            filters['brand_id'] = query.brand_id
        if query.is_active is not None:
            filters['is_active'] = query.is_active
        if query.min_price is not None:
            filters['min_price'] = query.min_price
        if query.max_price is not None:
            filters['max_price'] = query.max_price
        return self._repo.get_all(filters=filters)

    def check_stock(self, query: CheckStockQuery) -> Dict[str, Any]:
        """Use case: Kiểm tra tồn kho (Cart/Order Service dùng)."""
        product = self._repo.get_by_id(query.product_id)
        if product is None:
            return {'found': False, 'available': False, 'stock': 0}
        return {
            'found': True,
            'id': product.id,
            'name': product.name,
            'stock': product.stock,
            'available': product.is_in_stock(),
            'price': str(product.price),
        }
