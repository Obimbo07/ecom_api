import os

from django.conf import settings
from django.apps import apps
from django.core.asgi import get_asgi_application

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from mangum import Mangum

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aeroplane.settings")
apps.populate(settings.INSTALLED_APPS)


from aeroplane.endpoints import router as aero_router
from users.endpoints import router as user_router

app = FastAPI(title="Aeroplane", debug=settings.DEBUG)
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
