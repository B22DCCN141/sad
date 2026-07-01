"""
Product Entity - Core Aggregate Root trong Catalog domain.
Pure domain entity, không phụ thuộc framework.

Thiết kế theo DDD Cách 2:
- 1 Product Service duy nhất
- Category là dữ liệu (field category_id + attributes JSONB)
- Không tách theo loại sản phẩm

Attributes JSON linh hoạt hỗ trợ mọi loại sản phẩm:
- Phone: {"ram": "8GB", "storage": "256GB", "screen": "6.1 inch"}
- Laptop: {"ram": "16GB", "cpu": "Intel i7", "gpu": "RTX 3060"}
- Fashion: {"size": "L", "color": "Xanh navy", "material": "Cotton"}
- Cosmetic: {"volume": "50ml", "skin_type": "Da dầu"}
- ...
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from decimal import Decimal


@dataclass
class Product:
    """
    Core Entity (Aggregate Root) trong Catalog bounded context.
    Category là DỮ LIỆU thông qua category_id, không phải Service riêng.
    Attributes là JSONB linh hoạt theo từng loại sản phẩm.
    """
    id: Optional[int]
    name: str
    description: str
    price: Decimal
    stock: int
    category_id: int
    brand_id: Optional[int]
    # attributes JSONB - linh hoạt theo loại sản phẩm (Phone/Laptop/Fashion/...)
    attributes: Dict[str, Any] = field(default_factory=dict)
    image_url: str = ""
    is_active: bool = True

    def __post_init__(self):
        self._validate()

    def _validate(self):
        if not self.name or not self.name.strip():
            raise ValueError("Tên sản phẩm không được để trống.")
        if self.price < Decimal('0'):
            raise ValueError("Giá sản phẩm không được âm.")
        if self.stock < 0:
            raise ValueError("Tồn kho không được âm.")

    def is_in_stock(self) -> bool:
        """Kiểm tra còn hàng không."""
        return self.stock > 0

    def decrease_stock(self, quantity: int) -> None:
        """Giảm tồn kho khi đặt hàng."""
        if quantity <= 0:
            raise ValueError("Số lượng phải lớn hơn 0.")
        if self.stock < quantity:
            raise ValueError(f"Không đủ hàng. Tồn kho: {self.stock}, yêu cầu: {quantity}.")
        self.stock -= quantity

    def increase_stock(self, quantity: int) -> None:
        """Tăng tồn kho khi nhập hàng."""
        if quantity <= 0:
            raise ValueError("Số lượng phải lớn hơn 0.")
        self.stock += quantity

    def deactivate(self) -> None:
        """Ẩn sản phẩm (soft delete)."""
        self.is_active = False

    def get_attribute(self, key: str) -> Any:
        """Lấy thuộc tính theo key."""
        return self.attributes.get(key)

    def __repr__(self):
        return f"<Product id={self.id} name='{self.name}' price={self.price}>"
