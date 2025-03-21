from fastapi import APIRouter, Depends, Request

from api.schemas.authentication import UserIdRole
from database.actions import get_images_from_db, get_user_with_bonus_card_from_db
from database.db import async_session_maker
from database.models import MainInfoImage
from api.schemas.main_page import ImageDTO, ProductTypeDTO, ProductCardDTO
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from database.models import ProductType, PromotionImage, Product, ServiceImage
from api.errors.headers.exceptions import HeaderMissing
from api.security.authentication import check_jwt_access_token

main_screen_router = APIRouter()


@main_screen_router.get('/headers')
async def get_headers(request: Request):
    user_agent = request.headers.get("User-Agent")
    accept_language = request.headers.get("Accept-Language")

    if user_agent is None:
        raise HeaderMissing(header_name="User-Agent")
    if accept_language is None:
        raise HeaderMissing(header_name="Accept-Language")

    return {
        "User-Agent": user_agent,
        "Accept-Language": accept_language
    }


@main_screen_router.get('/')
async def get_main_page_info(user: UserIdRole = Depends(check_jwt_access_token)):
    async with async_session_maker() as async_session:
        main_info_images_dto = await get_images_from_db(MainInfoImage, ImageDTO, async_session)

        product_types_subtypes_from_db = await async_session.execute(
            select(ProductType)
            .options(selectinload(ProductType.product_subtypes))
        )
        product_types_subtypes_from_db = product_types_subtypes_from_db.scalars().all()
        product_types_subtypes_dto = [
            ProductTypeDTO.model_validate(product_type)
            for product_type in product_types_subtypes_from_db
        ]

        promotion_images_dto = await get_images_from_db(PromotionImage, ImageDTO, async_session)

        top_sellers_from_db = await async_session.execute(
            select(Product)
            .order_by(desc(Product.number_of_sales))
            .limit(10)
        )
        top_sellers_from_db = top_sellers_from_db.scalars().all()
        top_sellers_dto = [
            ProductCardDTO.model_validate(product)
            for product in top_sellers_from_db
        ]

        if user.role == "user":
            user_from_db = await get_user_with_bonus_card_from_db(async_session, user)

            for product in top_sellers_dto:
                product.price = product.price - (
                        product.price / 100 * user_from_db.bonus_card.customer_level.discount_amount_in_percent)

        service_images_dto = await get_images_from_db(ServiceImage, ImageDTO, async_session)

        response_data = {
            "user_id": user.id,
            "user_role": user.role,
            "main_info_images": main_info_images_dto,
            "product_types_subtypes": product_types_subtypes_dto,
            "promotion_images": promotion_images_dto,
            "top_sellers": top_sellers_dto,
            "service_images": service_images_dto
        }

    return response_data
