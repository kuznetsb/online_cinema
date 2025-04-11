from fastapi import FastAPI
from routes import accounts_router

app = FastAPI(title="Online cinema API",)

api_version_prefix = "/api/v1"

app.include_router(accounts_router, prefix=f"{api_version_prefix}/accounts", tags=["accounts"])
