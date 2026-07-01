"""
Command: Cập nhật sản phẩm.
"""
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Dict, Optional


@dataclass
class UpdateProductCommand:
    """
    Command object cho việc cập nhật sản phẩm.
    Chỉ chứa các field cần update (None = không thay đổi).
    """
    product_id: int
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    stock: Optional[int] = None
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    attributes: Optional[Dict[str, Any]] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None
