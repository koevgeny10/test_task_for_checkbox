from fastapi import APIRouter

from checks.api.views.auth import auth_router
from checks.api.views.check import check_router
from checks.api.views.health import health_router
from checks.api.views.user import users_router

root_router = APIRouter()

for router in (
    health_router,
    users_router,
    auth_router,
    check_router,
):
    root_router.include_router(router)
