from aiogram import Router


from .user_handlers import user_router
from .admin_handlers import admin_router
from .headman_handlers import headman_router

main_router = Router()
main_router.include_routers(user_router, headman_router, admin_router)