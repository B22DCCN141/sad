"""
Unit Tests cho Product Domain Entity.
Kiểm tra business logic thuần - không cần database.
"""
from decimal import Decimal
import pytest
from modules.catalog.domain.entities.product import Product


def make_product(**kwargs) -> Product:
    defaults = {
        'id': 1,
        'name': 'Test Product',
        'description': 'Mô tả test',
        'price': Decimal('100000'),
        'stock': 10,
        'category_id': 1,
        'brand_id': None,
        'attributes': {},
    }
    defaults.update(kwargs)
    return Product(**defaults)


class TestProductEntity:

    def test_create_product_success(self):
        p = make_product(name='iPhone 15', price=Decimal('25000000'), stock=5)
        assert p.name == 'iPhone 15'
        assert p.price == Decimal('25000000')
        assert p.stock == 5
        assert p.is_active is True

    def test_product_invalid_empty_name(self):
        with pytest.raises(ValueError, match='Tên sản phẩm'):
            make_product(name='')

    def test_product_negative_price(self):
        with pytest.raises(ValueError, match='Giá sản phẩm'):
            make_product(price=Decimal('-1'))

    def test_product_negative_stock(self):
        with pytest.raises(ValueError, match='Tồn kho'):
            make_product(stock=-1)

    def test_is_in_stock_true(self):
        p = make_product(stock=5)
        assert p.is_in_stock() is True

    def test_is_in_stock_false(self):
        p = make_product(stock=0)
        assert p.is_in_stock() is False

    def test_decrease_stock_success(self):
        p = make_product(stock=10)
        p.decrease_stock(3)
        assert p.stock == 7

    def test_decrease_stock_insufficient(self):
        p = make_product(stock=2)
        with pytest.raises(ValueError, match='Không đủ hàng'):
            p.decrease_stock(5)

    def test_increase_stock(self):
        p = make_product(stock=10)
        p.increase_stock(5)
        assert p.stock == 15

    def test_deactivate(self):
        p = make_product()
        p.deactivate()
        assert p.is_active is False

    def test_get_attribute(self):
        p = make_product(attributes={'ram': '8GB', 'storage': '256GB'})
        assert p.get_attribute('ram') == '8GB'
        assert p.get_attribute('nonexistent') is None

    def test_attributes_flexible_for_different_categories(self):
        # Phone attributes
        phone = make_product(
            name='iPhone 15',
            category_id=1,  # Điện thoại
            attributes={'ram': '8GB', 'os': 'iOS 17', 'screen_size': '6.1 inch'}
        )
        assert phone.get_attribute('os') == 'iOS 17'

        # Laptop attributes
        laptop = make_product(
            name='MacBook Pro',
            category_id=2,  # Laptop
            attributes={'ram': '16GB', 'cpu': 'Apple M4', 'storage': '512GB SSD'}
        )
        assert laptop.get_attribute('cpu') == 'Apple M4'

        # Fashion attributes
        fashion = make_product(
            name='Nike Air Force 1',
            category_id=3,  # Thời trang
            attributes={'size': '42', 'color': 'Trắng', 'material': 'Da'}
        )
        assert fashion.get_attribute('size') == '42'

        # Book attributes
        book = make_product(
            name='Đắc Nhân Tâm',
            category_id=5,  # Sách
            attributes={'author': 'Dale Carnegie', 'pages': 320}
        )
        assert book.get_attribute('pages') == 320
