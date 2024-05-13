from enum import StrEnum, auto, unique


@unique
class EndpointTag(StrEnum):
    AUTH = auto()
    USER = auto()
    CHECK = auto()


OPENAPI_TAGS = [
    {
        "name": EndpointTag.AUTH.value,
        "description": "Посилання для авторизації.",
    },
    {
        "name": EndpointTag.USER.value,
        "description": "Посилання для роботи з користувачами.",
    },
    {
        "name": EndpointTag.CHECK.value,
        "description": "Посилання для роботи з чеками.",
    },
]
