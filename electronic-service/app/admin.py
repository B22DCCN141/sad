from django.contrib import admin
from .models import Electronic


@admin.register(Electronic)
class ElectronicAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'name', 'brand', 'model_number', 'category',
        'price', 'stock', 'warranty_months', 'is_active', 'created_at',
    ]
    list_filter = ['category', 'is_active', 'brand']
    search_fields = ['name', 'brand', 'model_number']
    list_editable = ['price', 'stock', 'is_active']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Thông tin sản phẩm', {
            'fields': ('name', 'brand', 'model_number', 'category', 'description')
        }),
        ('Kinh doanh', {
            'fields': ('price', 'stock', 'warranty_months', 'is_active')
        }),
        ('Thời gian', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
