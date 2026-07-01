"""
Money Value Object - Đại diện cho giá tiền trong domain.
Immutable, không phụ thuộc framework.
"""
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP


@dataclass(frozen=True)
class Money:
    """
    Value Object đại diện cho giá tiền (VNĐ).
    Immutable - không thay đổi sau khi tạo.
    """
    amount: Decimal
    currency: str = "VND"

    def __post_init__(self):
        if self.amount < Decimal('0'):
            raise ValueError("Số tiền không được âm.")

    def add(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("Không thể cộng hai đơn vị tiền tệ khác nhau.")
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def multiply(self, factor: int) -> 'Money':
        return Money(amount=(self.amount * factor).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                     currency=self.currency)

    def format(self) -> str:
        """Hiển thị theo định dạng VNĐ."""
        return f"{self.amount:,.0f} {self.currency}"

    def __repr__(self):
        return f"<Money {self.format()}>"
