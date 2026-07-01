"""
Queries cho Product - Application layer.
Các use case đọc dữ liệu (CQRS read side).
"""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class GetProductQuery:
    """Query lấy một sản phẩm theo ID."""
    product_id: int


@dataclass
class ListProductsQuery:
    """
    Query lấy danh sách sản phẩm với filter.
    Category là dữ liệu => filter theo category_id.
    """
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    is_active: Optional[bool] = True
    min_price: Optional[float] = None
    max_price: Optional[float] = None


@dataclass
class FilterProductsQuery:
    """
    Query lọc sản phẩm nâng cao theo attributes JSONB.
    Ví dụ: {"ram": "16GB"} cho Laptop, {"size": "L"} cho Fashion
    """
    category_id: Optional[int] = None
    attribute_filters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CheckStockQuery:
    """Query kiểm tra tồn kho - dùng bởi cart-service và order-service."""
    product_id: int
