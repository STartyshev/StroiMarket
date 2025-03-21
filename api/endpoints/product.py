import asyncio
import json
from fastapi import APIRouter, WebSocket, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from api.schemas.authentication import UserIdRole, UserFull
from database.actions import get_user_by_id_from_db, get_product_feedback_by_id, get_user_with_bonus_card_from_db
from database.db import async_session_maker
from database.models import Product, ProductFeedback, ProductSubtype
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload
from api.schemas.feedback import FeedbackTextWebsocket, FeedbackCreateToSend, FeedbackUpdateToSend, \
    NotAuthorizedUser, AdminCommentWebsocket, DeleteFeedbackWebsocket, FeedbackDeleteToSend, Feedback
from api.security.authentication import check_jwt_access_token
from pydantic import ValidationError
from jinja2 import Environment, FileSystemLoader

product_page_router = APIRouter(prefix="/catalog/product")
# Инициализация директории шаблонов (для создания TemplateResponse)
templates = Jinja2Templates(directory="templates")
# Инициализация переменной окружения (для загрузки HTML-шаблона в websocket)
env = Environment(loader=FileSystemLoader(searchpath="templates"))
connected_users: dict[WebSocket, str] = dict()


async def connect_guest(websocket: WebSocket):
    connected_users[websocket] = "guest"
    # Оповещаем гостя о том, что доступ к созданию отзыва запрещен
    await websocket.send_json(
        NotAuthorizedUser(
            status_code=401,
            error_message="Для отправки отзывов необходимо авторизоваться").model_dump())

    # Поддерживаем websocket-соединение
    while True:
        await asyncio.sleep(3)

async def connect_user(websocket: WebSocket, user_id: int, product_id: int, async_session):
    connected_users[websocket] = "user"
    user_from_db = await get_user_by_id_from_db(async_session, UserIdRole(id=user_id, role="user"))
    user_from_db = UserFull.model_validate(user_from_db)

    try:
        while True:
            new_websocket_data = await get_new_websocket_data(websocket)

            # Проверяем какие данные пришли. Если с информацией о новом отзыве,
            # то возвращаем динамически заполненный HTML-отзыв
            if isinstance(new_websocket_data, FeedbackTextWebsocket):
                new_feedback_data = new_websocket_data

                new_feedback = ProductFeedback(
                    author_id=user_id,
                    product_id=product_id,
                    liked_text=new_feedback_data.liked_text,
                    disliked_text=new_feedback_data.disliked_text
                )
                async_session.add(new_feedback)
                await async_session.commit()
                await async_session.refresh(new_feedback)

                new_feedback = Feedback.model_validate(new_feedback)

                feedback_json_data = {
                    "id": new_feedback.id,
                    "user_name": f"{user_from_db.first_name} {user_from_db.last_name[0]}.",
                    "feedback_date": new_feedback.date_of_update.strftime("%d.%m.%Y %H:%M"),
                    "liked_text": new_feedback.liked_text,
                    "disliked_text": new_feedback.disliked_text
                }

                # Загружаем HTML-шаблоны
                user_template_feedback = env.get_template("user_new_feedback.html")
                admin_template_feedback = env.get_template("admin_new_feedback.html")
                # Заполняем их данными
                user_feedback_html = user_template_feedback.render(feedback_json_data)
                admin_feedback_html = admin_template_feedback.render(feedback_json_data)

                # Делаем рассылку всем пользователям подключившимся по websocket
                for user_websocket, user_role in connected_users.items():
                    await user_websocket.send_json(FeedbackCreateToSend(
                        status_code=200,
                        operation_type="create",
                        feedback_html=
                        admin_feedback_html
                        if user_role == "admin"
                        else user_feedback_html
                    ).model_dump())

    except Exception as e:
        print(f"Ошибка в вебсокете: {e}")
    finally:
        await websocket.close()
        connected_users.pop(websocket, None)


async def connect_admin(websocket: WebSocket, async_session):
    connected_users[websocket] = "admin"

    try:
        while True:
            new_websocket_data = await get_new_websocket_data(websocket)

            # Обрабатываем запрос на добавление комментария администратора
            if isinstance(new_websocket_data, AdminCommentWebsocket):
                new_admin_comment = new_websocket_data

                # Находим в БД отзыв на котором администратор оставил комментарий
                feedback_to_update = await get_product_feedback_by_id(async_session, new_admin_comment.feedback_id)

                feedback_to_update.admin_comment = new_admin_comment.admin_comment
                await async_session.commit()
                await async_session.refresh(feedback_to_update)

                for user_websocket in connected_users.keys():
                    await user_websocket.send_json(
                        FeedbackUpdateToSend(
                            status_code=200,
                            operation_type="update",
                            feedback_id=feedback_to_update.id,
                            admin_comment=feedback_to_update.admin_comment
                        ).model_dump())
            # Обрабатываем запрос на удаление отзыва
            elif isinstance(new_websocket_data, DeleteFeedbackWebsocket):
                feedback_to_delete = new_websocket_data
                feedback_to_delete_id = feedback_to_delete.feedback_id

                feedback_to_delete_from_db = await get_product_feedback_by_id(async_session, feedback_to_delete_id)

                await async_session.delete(feedback_to_delete_from_db)
                await async_session.commit()

                for user_websocket in connected_users.keys():
                    await user_websocket.send_json(
                        FeedbackDeleteToSend(
                            status_code=200,
                            operation_type="delete",
                            feedback_id=feedback_to_delete_id
                        ).model_dump())

    except Exception as e:
        print(f"Ошибка в вебсокете: {e}")
    finally:
        await websocket.close()
        connected_users.pop(websocket)


@product_page_router.websocket("/{product_id}")
async def websocket_feedback(websocket: WebSocket, product_id: int, user_id: int, user_role: str):
    await websocket.accept()

    async with async_session_maker() as async_session:
        if user_role == "guest":
            await connect_guest(websocket)
        elif user_role == "user":
            await connect_user(websocket, user_id, product_id, async_session)
        elif user_role == "admin":
            await connect_admin(websocket, async_session)


async def get_new_websocket_data(websocket: WebSocket) -> FeedbackTextWebsocket | AdminCommentWebsocket | DeleteFeedbackWebsocket:
    try:
        data_json_string = await websocket.receive_text()
        data_json = json.loads(data_json_string)
        if data_json["role"] == "user":
            return FeedbackTextWebsocket(**data_json)
        elif data_json["role"] == "admin":
            if data_json["operation_type"] == "update":
                return AdminCommentWebsocket(**data_json)
            elif data_json["operation_type"] == "delete":
                return DeleteFeedbackWebsocket(**data_json)
            else:
                raise ValidationError
        else:
            raise ValidationError
    except (ValidationError, KeyError) as e:
        print(e.errors)
        await websocket.send_json({"status_code": 400, "error_message": "Invalid value"})
        raise


@product_page_router.get('/{product_id}', response_class=HTMLResponse)
async def get_product_page(request: Request, product_id: int, user: UserIdRole = Depends(check_jwt_access_token)):
    async with async_session_maker() as async_session:
        # Получаем информацию о продукте из БД
        product_from_db = await async_session.execute(
            select(Product)
            .where(Product.id == product_id)
            .options(
                joinedload(Product.product_subtype).joinedload(ProductSubtype.type),
                selectinload(Product.feedbacks).joinedload(ProductFeedback.author)
            )
        )
        product = product_from_db.scalar()

        # Если пользователь не гость, то рассчитываем скидочную цену
        if user.role == "user":
            user_from_db = await get_user_with_bonus_card_from_db(async_session, user)
            product_bonus_price = product.price - (
                    product.price / 100 * user_from_db.bonus_card.customer_level.discount_amount_in_percent)
        else:
            product_bonus_price = product.price - (product.price / 100 * 3)

        # Приводим дату создания отзыва к формату "день.месяц.год час:минута"
        for feedback in product.feedbacks:
            feedback.date_of_update = feedback.date_of_update.strftime("%d.%m.%Y %H:%M")

        # Заполняем страницу продукта данными
        product_html = templates.TemplateResponse(
            name="product.html",
            context={
                "request": request,
                "product_type": product.product_subtype.type.name,
                "product_subtype": product.product_subtype.name,
                "product_name": product.name,
                "product_description": product.description,
                "product_bonus_price": product_bonus_price,
                "product_price": product.price,
                "product_availability": product.quantity_in_stock,
                "product_image_link": product.image_link,
                "feedbacks": product.feedbacks,
                "role": user.role
            }
        )
        return product_html
