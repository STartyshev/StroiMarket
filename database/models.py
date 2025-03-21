import datetime

from database.db import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, text, ForeignKey, SmallInteger, Numeric, LargeBinary, Float, literal_column
from typing import Annotated


class CustomTypes:
    int_pk = Annotated[int, mapped_column(primary_key=True)]
    small_int_pk = Annotated[int, mapped_column(SmallInteger, primary_key=True)]

    str50_pk = Annotated[str, mapped_column(String(50), primary_key=True)]

    created_at = Annotated[datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]
    updated_at = Annotated[datetime.datetime, mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=lambda: datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    )]


class User(Base):
    __tablename__ = "users"

    id: Mapped[CustomTypes.int_pk]
    first_name: Mapped[str] = mapped_column(String(30), server_default="Новый")
    last_name: Mapped[str] = mapped_column(String(50), server_default="Пользователь")
    phone_number: Mapped[str | None] = mapped_column(String(12), unique=True)
    email: Mapped[str | None] = mapped_column(String(50), unique=True)
    login: Mapped[str | None] = mapped_column(String(30), unique=True)
    hashed_password: Mapped[bytes | None] = mapped_column(LargeBinary)
    role: Mapped[str] = mapped_column(String(15), server_default="user")
    total_amount_of_purchases: Mapped[float] = mapped_column(Float, server_default=literal_column('0.0'))
    date_of_registration: Mapped[CustomTypes.created_at]
    date_of_update: Mapped[CustomTypes.updated_at]

    addresses: Mapped[list["UserAddress"]] = relationship(back_populates="user", cascade="all, delete", passive_deletes=True)
    orders: Mapped[list["Order"]] = relationship(back_populates="user", cascade="all, delete", passive_deletes=True)
    bonus_card: Mapped["BonusCard"] = relationship(back_populates="user", cascade="all, delete", passive_deletes=True)
    feedbacks: Mapped[list["ProductFeedback"]] = relationship(back_populates="author")
    items_in_cart: Mapped[list["Product"]] = relationship(back_populates="customers", secondary="cart_items", cascade="all, delete", passive_deletes=True)


class UserAddress(Base):
    __tablename__ = "users_addresses"

    id: Mapped[CustomTypes.int_pk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    city: Mapped[str] = mapped_column(String(30))
    street: Mapped[str] = mapped_column(String(30))
    house_number: Mapped[str] = mapped_column(String(10))
    entrance: Mapped[str] = mapped_column(String(5))
    delivery_point: Mapped[str] = mapped_column(String(15))

    user: Mapped["User"] = relationship(back_populates="addresses")
    orders: Mapped[list["Order"]] = relationship(back_populates="address")


class DeliveryType(Base):
    __tablename__ = "delivery_types"

    name: Mapped[CustomTypes.str50_pk]

    orders: Mapped[list["Order"]] = relationship(back_populates="delivery_type")


class OrderStatus(Base):
    __tablename__ = "order_statuses"

    name: Mapped[CustomTypes.str50_pk]

    orders: Mapped[list["Order"]] = relationship(back_populates="order_status")


class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    name: Mapped[CustomTypes.str50_pk]

    orders: Mapped[list["Order"]] = relationship(back_populates="payment_method")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[CustomTypes.int_pk]
    delivery_type_name: Mapped[str] = mapped_column(ForeignKey("delivery_types.name"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    address_id: Mapped[int] = mapped_column(ForeignKey("users_addresses.id"))
    status_name: Mapped[str] = mapped_column(ForeignKey("order_statuses.name"))
    payment_method_name: Mapped[str] = mapped_column(ForeignKey("payment_methods.name"))
    date_of_registration: Mapped[CustomTypes.created_at]
    date_of_update: Mapped[CustomTypes.updated_at]

    delivery_type: Mapped["DeliveryType"] = relationship(back_populates="orders")
    user: Mapped["User"] = relationship(back_populates="orders")
    address: Mapped["UserAddress"] = relationship(back_populates="orders")
    order_status: Mapped["OrderStatus"] = relationship(back_populates="orders")
    payment_method: Mapped["PaymentMethod"] = relationship(back_populates="orders")
    products: Mapped[list["Product"]] = relationship(back_populates="orders", secondary="order_items")


class CustomerLevel(Base):
    __tablename__ = "customer_levels"

    name: Mapped[CustomTypes.str50_pk]
    discount_amount_in_percent: Mapped[int] = mapped_column(SmallInteger)
    lower_threshold: Mapped[int]
    level_number: Mapped[int | None] = mapped_column(SmallInteger)

    bonus_cards: Mapped[list["BonusCard"]] = relationship(back_populates="customer_level")


class BonusCard(Base):
    __tablename__ = "bonus_cards"

    id: Mapped[CustomTypes.int_pk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    customer_level_name: Mapped[str] = mapped_column(ForeignKey("customer_levels.name"), server_default="Новичок")
    date_of_registration: Mapped[CustomTypes.created_at]
    date_of_update: Mapped[CustomTypes.updated_at]

    user: Mapped["User"] = relationship(back_populates="bonus_card")
    customer_level: Mapped["CustomerLevel"] = relationship(back_populates="bonus_cards")


class ProductType(Base):
    __tablename__ = "product_types"

    name: Mapped[str] = mapped_column(String(100), primary_key=True)
    image_link: Mapped[str]

    product_subtypes: Mapped[list["ProductSubtype"]] = relationship(back_populates="type")


class ProductSubtype(Base):
    __tablename__ = "product_subtypes"

    name: Mapped[str] = mapped_column(String(100), primary_key=True)
    image_link: Mapped[str]
    type_name: Mapped[str] = mapped_column(ForeignKey("product_types.name"))

    type: Mapped["ProductType"] = relationship(back_populates="product_subtypes")
    products: Mapped[list["Product"]] = relationship(back_populates="product_subtype")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[CustomTypes.int_pk]
    name: Mapped[str] = mapped_column(unique=True)
    price: Mapped[float] = mapped_column(Numeric(7, 2))
    description: Mapped[str]
    image_link: Mapped[str]
    quantity_in_stock: Mapped[int | None]
    product_subtype_name: Mapped[str] = mapped_column(ForeignKey("product_subtypes.name"))
    additional_information: Mapped[str]
    rating: Mapped[float] = mapped_column(Numeric(1, 1))
    number_of_sales: Mapped[int | None]

    product_subtype: Mapped["ProductSubtype"] = relationship(back_populates="products")
    orders: Mapped[list["Order"]] = relationship(back_populates="products", secondary="order_items")
    feedbacks: Mapped[list["ProductFeedback"]] = relationship(back_populates="product")
    customers: Mapped[list["User"]] = relationship(back_populates="items_in_cart", secondary="cart_items")


class OrderItem(Base):
    __tablename__ = "order_items"

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), primary_key=True)
    quantity: Mapped[int] = mapped_column(SmallInteger)


class ProductFeedback(Base):
    __tablename__ = "product_feedbacks"

    id: Mapped[CustomTypes.int_pk]
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"))
    liked_text: Mapped[str]
    disliked_text: Mapped[str]
    admin_comment: Mapped[str | None]
    number_of_likes: Mapped[int] = mapped_column(SmallInteger, server_default=literal_column('0'))
    number_of_dislikes: Mapped[int] = mapped_column(SmallInteger, server_default=literal_column('0'))
    date_of_registration: Mapped[CustomTypes.created_at]
    date_of_update: Mapped[CustomTypes.updated_at]

    author: Mapped["User"] = relationship(back_populates="feedbacks")
    product: Mapped["Product"] = relationship(back_populates="feedbacks")


class CartItem(Base):
    __tablename__ = "cart_items"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), primary_key=True)
    quantity: Mapped[int] = mapped_column(SmallInteger)


class ImageTable:
    name: Mapped[CustomTypes.str50_pk]
    image_link: Mapped[str]


class MainInfoImage(Base, ImageTable):
    __tablename__ = "main_info_images"


class PromotionImage(Base, ImageTable):
    __tablename__ = "promotion_images"


class ServiceImage(Base, ImageTable):
    __tablename__ = "service_images"
