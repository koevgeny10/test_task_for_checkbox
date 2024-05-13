from fastapi import APIRouter

health_router = APIRouter(prefix="/health", tags=["health"])


@health_router.get("/", response_description="Сервер работает")
async def get_health() -> None:
    """Для проверки работоспособности сервера."""
