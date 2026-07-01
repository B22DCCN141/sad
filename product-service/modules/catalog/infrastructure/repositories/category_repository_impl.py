"""
Category Repository Implementation - Infrastructure Layer.
"""
from typing import List, Optional

from modules.catalog.domain.entities.category import Category
from modules.catalog.domain.repositories.category_repository import CategoryRepository
from modules.catalog.infrastructure.models.product_model import CategoryModel


class DjangoCategoryRepository(CategoryRepository):
    """Concrete implementation của CategoryRepository dùng Django ORM."""

    @staticmethod
    def _to_domain(orm: CategoryModel) -> Category:
        return Category(
            id=orm.id,
            name=orm.name,
            slug=orm.slug,
            description=orm.description or "",
            parent_id=orm.parent_id,
            is_active=orm.is_active,
        )

    def get_by_id(self, category_id: int) -> Optional[Category]:
        try:
            return self._to_domain(CategoryModel.objects.get(pk=category_id))
        except CategoryModel.DoesNotExist:
            return None

    def get_all(self, active_only: bool = True) -> List[Category]:
        qs = CategoryModel.objects.all()
        if active_only:
            qs = qs.filter(is_active=True)
        return [self._to_domain(orm) for orm in qs]

    def get_children(self, parent_id: int) -> List[Category]:
        return [self._to_domain(orm) for orm in CategoryModel.objects.filter(parent_id=parent_id)]

    def save(self, category: Category) -> Category:
        if category.id is None:
            orm = CategoryModel.objects.create(
                name=category.name,
                slug=category.slug,
                description=category.description,
                parent_id=category.parent_id,
                is_active=category.is_active,
            )
        else:
            CategoryModel.objects.filter(pk=category.id).update(
                name=category.name,
                slug=category.slug,
                description=category.description,
                parent_id=category.parent_id,
                is_active=category.is_active,
            )
            orm = CategoryModel.objects.get(pk=category.id)
        return self._to_domain(orm)
