"""
Vercel serverless function handler for FastAPI app
"""
import sys
import os

# Add the parent directory to Python path for Vercel
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import the FastAPI app
from app.main import app
from mangum import Mangum

# Create the handler for Vercel
# Vercel uses AWS Lambda-compatible events
handler = Mangum(app, lifespan="off")

def lambda_handler(event, context):
    """Vercel-compatible handler (uses Lambda event format)"""
    return handler(event, context)
