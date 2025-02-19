import os

from django.conf import settings
from django.apps import apps
from django.core.asgi import get_asgi_application

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from starlette.middleware.cors import CORSMiddleware
from mangum import Mangum

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aeroplane.settings")
apps.populate(settings.INSTALLED_APPS)


from aeroplane.endpoints import router as aero_router
from users.endpoints import router as user_router



app = FastAPI(title="Aeroplane", debug=settings.DEBUG)

def custom_openapi():
    """Customize OpenAPI schema to include JWT authentication."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="E-Commerce API",
        version="1.0.0",
        description="FastAPI-based authentication with JWT",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(aero_router, prefix="/api")
app.include_router(user_router, prefix="/users")
app.mount("/dj", get_asgi_application())

handler = Mangum(app)
