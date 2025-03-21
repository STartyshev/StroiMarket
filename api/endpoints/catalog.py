from fastapi import APIRouter, Request
from fastapi.params import Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.sql.expression import and_
from starlette.responses import JSONResponse

from api.schemas.authentication import UserIdRole
from api.security.authentication import check_jwt_access_token
from database.db import async_session_maker
from database.models import Product, ProductSubtype, ProductType, User, BonusCard
from api.schemas.main_page import ProductTypeDTO
import math


def ceil(value):
    return math.ceil(value)


catalog_router = APIRouter(prefix='/catalog')
templates = Jinja2Templates(directory="templates")
templates.env.filters["ceil"] = ceil


@catalog_router.get("/catalog_data", response_class=JSONResponse)
async def get_catalog_data():
    async with async_session_maker() as async_session:
        catalog_data_from_db = await async_session.execute(
            select(ProductType)
            .options(selectinload(ProductType.product_subtypes))
        )
        catalog_data_from_db = catalog_data_from_db.scalars().all()

        catalog_data_dto = [
            ProductTypeDTO.model_validate(product_type)
            for product_type in catalog_data_from_db
        ]

        return {"catalog_data": catalog_data_dto}


@catalog_router.get('/{product_type}/{product_subtype}', response_class=HTMLResponse)
async def get_items(
        request: Request,
        product_type: str,
        product_subtype: str,
        user: UserIdRole = Depends(check_jwt_access_token)):
    async with async_session_maker() as async_session:
        products_from_db = await async_session.execute(
            select(Product)
            .join(ProductSubtype)
            .join(ProductType)
            .where(
                and_(
                    ProductSubtype.name == product_subtype,
                    ProductType.name == product_type))
        )
        products_from_db = products_from_db.scalars().all()

        # Заменить на HTML страницу
        # if not products_from_db:
        #     return JSONResponse(status_code=404, content={"detail": "Запрашиваемый ресурс не найден."})

        if user.role == "user":
            user_from_db = await async_session.execute(
                select(User)
                .where(User.id == user.id)
                .options(joinedload(User.bonus_card).joinedload(BonusCard.customer_level))
            )
            user_from_db = user_from_db.scalar()
            for product in products_from_db:
                product.price = product.price - (
                        product.price / 100 * user_from_db.bonus_card.customer_level.discount_amount_in_percent)

        return templates.TemplateResponse(
            name="catalog.html",
            context={
                "request": request,
                "product_type": product_type,
                "product_subtype": product_subtype,
                "products_from_db": products_from_db
            })
