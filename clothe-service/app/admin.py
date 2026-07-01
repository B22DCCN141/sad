from django.contrib import admin
from .models import Clothing


@admin.register(Clothing)
class ClothingAdmin(admin.ModelAdmin):
    list_display  = ['id', 'name', 'brand', 'category', 'size', 'color', 'gender', 'price', 'stock', 'is_active']
    list_filter   = ['category', 'size', 'gender', 'is_active', 'brand']
    search_fields = ['name', 'brand', 'color', 'material']
    list_editable = ['price', 'stock', 'is_active']
    ordering      = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Thông tin sản phẩm', {
            'fields': ('name', 'brand', 'category', 'description')
        }),
        ('Thuộc tính', {
            'fields': ('size', 'color', 'gender', 'material')
        }),
        ('Kinh doanh', {
            'fields': ('price', 'stock', 'is_active')
        }),
        ('Thời gian', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
