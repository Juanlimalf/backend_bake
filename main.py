import uvicorn


if __name__ == "__main__":
    uvicorn.run("app.routes.routes:app", host="0.0.0.0", port=8004, log_level="info")
