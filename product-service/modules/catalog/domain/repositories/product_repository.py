"""
Product Repository Interface (Port) - Domain layer.
Định nghĩa contract mà Infrastructure layer phải implement.
Domain không biết về ORM hay database cụ thể.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from modules.catalog.domain.entities.product import Product


class ProductRepository(ABC):
    """
    Abstract Repository cho Product.
    Infrastructure (ORM) phải implement interface này.
    """

    @abstractmethod
    def get_by_id(self, product_id: int) -> Optional[Product]:
        """Lấy sản phẩm theo ID."""
        ...

    @abstractmethod
    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[Product]:
        """
        Lấy danh sách sản phẩm với filter tùy chọn.
        filters: {"category_id": 1, "is_active": True, "brand_id": 2}
        """
        ...

    @abstractmethod
    def save(self, product: Product) -> Product:
        """Lưu hoặc cập nhật sản phẩm."""
        ...

    @abstractmethod
    def delete(self, product_id: int) -> bool:
        """Xóa sản phẩm (hard delete)."""
        ...
