import uvicorn
import os
from redis import Redis

from fastapi import FastAPI
from starlette.responses import RedirectResponse
from starlette.middleware import Middleware


from .api.users.controllers import router as user_router
from .api.auth.controllers import router as auth_router
from .api.wallet.controllers import router as wallet_router
from .utils.logger import LoggerMiddleware

redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", 6379))
redis_user = os.getenv("REDIS_USER", None)
redis_password = os.getenv("REDIS_PASSWORD", None)

redis_client = Redis(host=redis_host, port=redis_port, password=redis_password)

app = FastAPI(
    title="Система аутентификации и авторизации",
    middleware=[
        Middleware(LoggerMiddleware)
    ]
)


@app.get('/', include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse(url="/docs")


app.include_router(user_router)
app.include_router(auth_router)
app.include_router(wallet_router)

app.add_middleware(LoggerMiddleware)

if __name__ == '__main__':
    uvicorn.run("main:proj_app", host="0.0.0.0", port=8000, reload=True)
