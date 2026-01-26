import uvicorn
import os
import sys

# Add current dir to path
sys.path.append(os.getcwd())

if __name__ == "__main__":
    uvicorn.run("api.index:app", host="127.0.0.1", port=8005)
