from app.app import app
from app.core.database import Base, engine


def main():
    print("Hello from backend!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    main()
