import redis.asyncio as redis
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from middlewares import CustomHeaderMiddleware
from fastapi_limiter import FastAPILimiter
from src.conf.config import settings
from src.routes import contacts, auth, users
# from middlewares import (BlackListMiddleware, CustomCORSMiddleware,
#                          CustomHeaderMiddleware, UserAgentBanMiddleware,
#                          WhiteListMiddleware)

import uvicorn

app = FastAPI()

app.include_router(auth.router, prefix='/api')
app.include_router(users.router, prefix='/api')
app.include_router(contacts.router, prefix='/api')
app.add_middleware(CustomHeaderMiddleware)

app.mount("/static", StaticFiles(directory='src/static'), name="static")

@app.on_event("startup")
async def startup():
    r = await redis.Redis(host=settings.REDIS_DOMAIN, port=settings.REDIS_PORT, db=0, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(r)

@app.get("/")
def read_root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)