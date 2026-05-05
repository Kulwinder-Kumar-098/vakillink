import uvicorn
import sys

if __name__ == "__main__":
    try:
        print("Starting VakeelLink Backend on 127.0.0.1:8001...")
        uvicorn.run("app.main:app", host="0.0.0.0", port=9000, log_level="debug")
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        sys.exit(1)
