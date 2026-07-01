"""
Django Admin - Presentation Layer.
Đăng ký models để quản lý qua Admin interface.
"""
from django.contrib import admin
from modules.catalog.infrastructure.models.product_model import ProductModel, CategoryModel, BrandModel


@admin.register(BrandModel)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug', 'is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(CategoryModel)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug', 'parent', 'is_active']
    list_filter = ['is_active', 'parent']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ProductModel)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category', 'brand', 'price', 'stock', 'is_active', 'created_at']
    list_filter = ['category', 'brand', 'is_active']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['price', 'stock', 'is_active']
