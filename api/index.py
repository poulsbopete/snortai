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
try:
    from app.main import app
    from mangum import Mangum
    
    # Create the Mangum handler for FastAPI
    mangum_handler = Mangum(app, lifespan="off")
    
    # Vercel Python functions expect a handler function
    def handler(event, context):
        """Vercel-compatible handler (uses Lambda event format)"""
        try:
            return mangum_handler(event, context)
        except Exception as e:
            # Return error response
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': str(e)})
            }
except Exception as e:
    # If import fails, create a simple error handler
    import json
    def handler(event, context):
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': f'Import error: {str(e)}'})
        }
