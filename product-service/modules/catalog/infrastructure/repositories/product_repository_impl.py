"""
Product Repository Implementation - Infrastructure Layer.
Implement domain interface ProductRepository bằng Django ORM.
Đây là nơi duy nhất biết về database/ORM.
"""
from decimal import Decimal
from typing import Any, Dict, List, Optional

from modules.catalog.domain.entities.product import Product
from modules.catalog.domain.repositories.product_repository import ProductRepository
from modules.catalog.infrastructure.models.product_model import ProductModel


class DjangoProductRepository(ProductRepository):
    """
    Concrete implementation của ProductRepository dùng Django ORM.
    Mapping: domain entity Product <-> ORM model ProductModel.
    """

    # ─── Mapper: ORM → Domain ───────────────────────────────────────────────

    @staticmethod
    def _to_domain(orm: ProductModel) -> Product:
        """Chuyển ORM model → Domain entity (thuần Python)."""
        return Product(
            id=orm.id,
            name=orm.name,
            description=orm.description,
            price=Decimal(str(orm.price)),
            stock=orm.stock,
            category_id=orm.category_id,
            brand_id=orm.brand_id,
            attributes=orm.attributes or {},
            image_url=orm.image_url or "",
            is_active=orm.is_active,
        )

    # ─── Repository Methods ──────────────────────────────────────────────────

    def get_by_id(self, product_id: int) -> Optional[Product]:
        try:
            orm = ProductModel.objects.select_related('category', 'brand').get(pk=product_id)
            return self._to_domain(orm)
        except ProductModel.DoesNotExist:
            return None

    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[Product]:
        qs = ProductModel.objects.select_related('category', 'brand').all()

        if filters:
            if 'category_id' in filters:
                qs = qs.filter(category_id=filters['category_id'])
            if 'brand_id' in filters:
                qs = qs.filter(brand_id=filters['brand_id'])
            if 'is_active' in filters:
                qs = qs.filter(is_active=filters['is_active'])
            if 'min_price' in filters:
                qs = qs.filter(price__gte=filters['min_price'])
            if 'max_price' in filters:
                qs = qs.filter(price__lte=filters['max_price'])

        return [self._to_domain(orm) for orm in qs]

    def save(self, product: Product) -> Product:
        """Insert hoặc Update tùy theo product.id."""
        if product.id is None:
            # CREATE
            orm = ProductModel.objects.create(
                name=product.name,
                description=product.description,
                price=product.price,
                stock=product.stock,
                category_id=product.category_id,
                brand_id=product.brand_id,
                attributes=product.attributes,
                image_url=product.image_url,
                is_active=product.is_active,
            )
        else:
            # UPDATE
            ProductModel.objects.filter(pk=product.id).update(
                name=product.name,
                description=product.description,
                price=product.price,
                stock=product.stock,
                category_id=product.category_id,
                brand_id=product.brand_id,
                attributes=product.attributes,
                image_url=product.image_url,
                is_active=product.is_active,
            )
            orm = ProductModel.objects.get(pk=product.id)

        return self._to_domain(orm)

    def delete(self, product_id: int) -> bool:
        deleted, _ = ProductModel.objects.filter(pk=product_id).delete()
        return deleted > 0
