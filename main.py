from fastapi import FastAPI
from routes import router

app = FastAPI(
    title="API Compromisos y Acciones",
    description="API para gestión de compromisos y acciones",
    version="1.0.0",
)

# Incluir rutas
app.include_router(router)


# Health check
@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
