from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Standardized exception handler returning consistent JSON responses:
    {
        "success": false,
        "error": {
            "code": "...",
            "message": "...",
            "details": {...}
        }
    }
    """
    response = exception_handler(exc, context)

    if response is not None:
        custom_data = {
            "success": False,
            "status_code": response.status_code,
            "error": {
                "message": "Validation or request processing error.",
                "details": response.data,
            },
        }

        # Handle specific detail string or dict
        if isinstance(response.data, dict) and "detail" in response.data:
            custom_data["error"]["message"] = str(response.data["detail"])
        elif isinstance(response.data, list) and len(response.data) > 0:
            custom_data["error"]["message"] = str(response.data[0])

        response.data = custom_data
    else:
        logger.error(f"Unhandled server error: {exc}", exc_info=True)
        response = Response(
            {
                "success": False,
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "error": {
                    "message": "An internal server error occurred.",
                    "details": str(exc),
                },
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response
