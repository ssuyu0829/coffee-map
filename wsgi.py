import sys
import os

# Add src/main/python to path so all imports resolve
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src/main/python"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src/main/python/api"))

from app import app

if __name__ == "__main__":
    app.run()
