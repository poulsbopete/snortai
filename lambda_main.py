# Lambda entry point for SnortAI
# This file handles the import path differences between local and Lambda deployment

import sys
import os

# Add the current directory to Python path for Lambda
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the FastAPI app from the app directory
from app.main import app
from mangum import Mangum

# Create the Lambda handler
handler = Mangum(app)
