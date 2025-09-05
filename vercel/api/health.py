"""
Vercel health check function
"""
import json
import time
import os


def handler(request):
    """Health check handler"""
    try:
        # Basic health check response
        health_data = {
            "status": "healthy",
            "timestamp": int(time.time()),
            "functions": {
                "analyze-photo": "available",
                "process-barcode": "available"
            },
            "environment": {
                "openai_configured": bool(os.environ.get("OPENAI_API_KEY")),
                "openfoodfacts_configured": bool(os.environ.get("OPENFOODFACTS_API_URL"))
            },
            "version": "1.0.0"
        }
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(health_data)
        }
        
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "status": "unhealthy",
                "error": str(e),
                "timestamp": int(time.time())
            })
        }


# For local testing
if __name__ == "__main__":
    test_request = type('Request', (), {'method': 'GET'})()
    result = handler(test_request)
    print(json.dumps(result, indent=2))
