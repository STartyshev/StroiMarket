from fastapi import FastAPI
from api.endpoints.main_screen import main_screen_router
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from api.errors.register_handlers import register_exception_handlers
from api.endpoints.base_auth import base_auth
from api.endpoints.cookie_auth import cookie_auth
from api.endpoints.jwt_auth import jwt_auth
from api.endpoints.catalog import catalog_router
from api.endpoints.product import product_page_router
from api.endpoints.user_profile import user_profile_router

origins = [
    "http://127.0.0.1:5500"
]

market_app = FastAPI()
market_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

market_app.include_router(product_page_router)
market_app.include_router(main_screen_router)
market_app.include_router(base_auth)
market_app.include_router(cookie_auth)
market_app.include_router(jwt_auth)
market_app.include_router(catalog_router)
market_app.include_router(user_profile_router)
register_exception_handlers(market_app)

if __name__ == '__main__':
    uvicorn.run(app=market_app)
