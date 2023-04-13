from app.routes_api.routes import router_bakeshop

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

# Configurando o FAST-API
metadata = [{
    "name": "API - Roleta Bakeshop",
    "description": "Backend game roleta bakeshop "
}]

app = FastAPI(title="Roleta Bakeshop",
              description="API - Roleta Bakeshop",
              version="1.0.0",
              openapi_tags=metadata)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])


@app.get("/", tags=["Docs"], include_in_schema=False)
async def docs():

    return RedirectResponse(url="/docs")


app.include_router(router_bakeshop)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8004, log_level="info")
