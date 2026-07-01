"""
Attributes Value Object - Đại diện cho tập thuộc tính linh hoạt của sản phẩm.
Đây là cốt lõi của DDD Cách 2: Category là dữ liệu, attributes là JSONB.

Ví dụ sử dụng:
- Phone:   Attributes({"ram": "8GB", "storage": "256GB", "screen_size": "6.1 inch", "os": "iOS"})
- Laptop:  Attributes({"ram": "16GB", "cpu": "Intel Core i7-12700H", "gpu": "RTX 3060", "storage": "512GB SSD"})
- Fashion: Attributes({"size": "L", "color": "Xanh navy", "material": "Cotton 100%", "gender": "Nam"})
- Cosmetic:Attributes({"volume": "50ml", "skin_type": "Da dầu", "ingredient": "Vitamin C"})
"""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class Attributes:
    """
    Value Object đại diện cho tập thuộc tính JSONB của sản phẩm.
    Immutable - dùng dict để lưu trữ.
    """
    data: Dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        return dict(self.data)

    def merge(self, other: 'Attributes') -> 'Attributes':
        """Merge hai tập attributes thành một."""
        merged = {**self.data, **other.data}
        return Attributes(data=merged)

    def __repr__(self):
        return f"<Attributes {self.data}>"
