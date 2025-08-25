from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import webhook, prediction, transaction, token, user

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins -> will be adjusted
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook.router, prefix="/webhook", tags=["webhook"])
app.include_router(user.router, prefix="/user", tags=["user"])
app.include_router(prediction.router, prefix="/prediction", tags=["prediction"])
app.include_router(transaction.router, prefix="/transaction", tags=["transaction"])
app.include_router(token.router, prefix="/token", tags=["token"])