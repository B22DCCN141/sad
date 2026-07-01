"""
Brand Entity - Thương hiệu sản phẩm.
Pure domain entity, không phụ thuộc framework.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Brand:
    """
    Entity thương hiệu sản phẩm.
    Ví dụ: Apple, Samsung, Nike, Adidas, ...
    """
    id: Optional[int]
    name: str
    slug: str
    description: str = ""
    is_active: bool = True

    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise ValueError("Tên thương hiệu không được để trống.")

    def __repr__(self):
        return f"<Brand id={self.id} name='{self.name}'>"
