"""
URL Patterns cho Catalog module - Presentation Layer.

API Endpoints:
  Products:
    GET/POST   /products/                           → Danh sách & tạo mới
    GET/PUT    /products/<pk>/                      → Chi tiết & cập nhật
    DELETE     /products/<pk>/                      → Ẩn sản phẩm (soft delete)
    GET        /products/<pk>/stock/                → Kiểm tra tồn kho

  Categories:
    GET/POST   /categories/                         → Danh sách & tạo mới
    GET/PUT    /categories/<pk>/                    → Chi tiết & cập nhật
    GET        /categories/<pk>/products/           → SP theo danh mục
"""
from django.urls import path

from modules.catalog.presentation.api.views.product_view import (
    ProductListCreateView,
    ProductDetailView,
    ProductStockView,
    ProductByCategoryView,
)
from modules.catalog.presentation.api.views.category_view import (
    CategoryListCreateView,
    CategoryDetailView,
)

urlpatterns = [
    # ── Products ──────────────────────────────────────────────────────────
    path('products/', ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('products/<int:pk>/stock/', ProductStockView.as_view(), name='product-stock'),

    # ── Categories ────────────────────────────────────────────────────────
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('categories/<int:category_id>/products/', ProductByCategoryView.as_view(), name='category-products'),
]
