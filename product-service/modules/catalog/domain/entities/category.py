"""
Category Entity - Pure domain entity, không phụ thuộc framework.
Category là DỮ LIỆU (theo DDD Cách 2), không phải Service riêng.
Hỗ trợ category tree (parent-child).
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Category:
    """
    Entity danh mục sản phẩm.
    Category là dữ liệu trong Catalog bounded context.
    Ví dụ: Điện tử > Điện thoại > iPhone
    """
    id: Optional[int]
    name: str
    slug: str
    description: str = ""
    parent_id: Optional[int] = None
    is_active: bool = True

    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise ValueError("Tên danh mục không được để trống.")
        if not self.slug or not self.slug.strip():
            raise ValueError("Slug danh mục không được để trống.")

    def is_root(self) -> bool:
        """Kiểm tra xem đây có phải là danh mục gốc không."""
        return self.parent_id is None

    def __repr__(self):
        return f"<Category id={self.id} name='{self.name}'>"
