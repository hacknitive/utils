
from fastapi import (
    Depends, 
    FastAPI,
    APIRouter,
)
from fastapi.openapi.docs import (
    get_swagger_ui_html, 
    get_redoc_html,
)
from fastapi.responses import HTMLResponse

from ..dependency.add_http_basic_security import add_http_basic_security_builder


def build_documents_router(
    user_name: str,
    password: str,
    title: str,
    app: FastAPI,
) -> APIRouter:

    add_http_basic_security = add_http_basic_security_builder(
        user_name=user_name,
        password=password,
    )

    router = APIRouter(include_in_schema=False)

    @router.get(
        path="/docs",
        response_class=HTMLResponse,
        include_in_schema=False,
        dependencies=[Depends(add_http_basic_security)]
    )
    async def get_protected_docs():
        return get_swagger_ui_html(
            openapi_url="/openapi.json",
            title=title,
        )

    @app.get(
        path="/redoc",
        response_class=HTMLResponse,
        include_in_schema=False,
        dependencies=[Depends(add_http_basic_security)]
    )
    async def get_protected_redoc():
        return get_redoc_html(
            openapi_url="/openapi.json",
            title=app.title + " - ReDoc",
        )

    @router.get(
        path="/openapi.json",
        include_in_schema=False,
        dependencies=[Depends(add_http_basic_security)]
    )
    async def get_openapi_json():
        return app.openapi()

    return router
