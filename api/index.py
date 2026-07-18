import sys
import os

# Append project root to sys.path so Vercel can find the app module
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import the FastAPI instance
from app.main import app
