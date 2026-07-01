"""
Category Repository Interface (Port) - Domain layer.
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from modules.catalog.domain.entities.category import Category


class CategoryRepository(ABC):
    """
    Abstract Repository cho Category.
    """

    @abstractmethod
    def get_by_id(self, category_id: int) -> Optional[Category]:
        """Lấy danh mục theo ID."""
        ...

    @abstractmethod
    def get_all(self, active_only: bool = True) -> List[Category]:
        """Lấy tất cả danh mục."""
        ...

    @abstractmethod
    def get_children(self, parent_id: int) -> List[Category]:
        """Lấy danh mục con."""
        ...

    @abstractmethod
    def save(self, category: Category) -> Category:
        """Lưu hoặc cập nhật danh mục."""
        ...
