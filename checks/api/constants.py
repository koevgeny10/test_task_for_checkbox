from enum import StrEnum, auto, unique


@unique
class EndpointTag(StrEnum):
    AUTH = auto()
    USER = auto()
    CHECK = auto()


OPENAPI_TAGS = [
    {
        "name": EndpointTag.AUTH.value,
        "description": "Для авторизації.",
    },
    {
        "name": EndpointTag.USER.value,
        "description": "Для роботи з користувачами.",
    },
    {
        "name": EndpointTag.CHECK.value,
        "description": "Для роботи з чеками.",
    },
]
