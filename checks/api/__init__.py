from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from checks.api.constants import OPENAPI_TAGS
from checks.api.dev.middlewares import add_process_time_header
from checks.api.views import root_router
from checks.settings import DEBUG

app = FastAPI(
    debug=DEBUG,
    title="Checks",
    description="Checks CRUD",
    openapi_tags=OPENAPI_TAGS,
    redoc_url="/docs2",
    default_response_class=ORJSONResponse,
    swagger_ui_parameters={"displayRequestDuration": True},
)

app.include_router(root_router)

if DEBUG:
    app.middleware("http")(add_process_time_header)
