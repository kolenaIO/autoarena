import uvicorn


if __name__ == "__main__":
    uvicorn.run(
        "autostack.main:app",
        host="0.0.0.0",
        port=8899,
        reload=True,
    )
