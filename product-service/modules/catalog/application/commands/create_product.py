"""
Command: Tạo sản phẩm mới.
Application layer - xử lý use case tạo sản phẩm.
"""
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Dict, Optional


@dataclass
class CreateProductCommand:
    """
    Command object cho việc tạo sản phẩm mới.
    Chứa dữ liệu input thuần, không có logic business.
    """
    name: str
    description: str
    price: Decimal
    stock: int
    category_id: int
    brand_id: Optional[int] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    image_url: str = ""
