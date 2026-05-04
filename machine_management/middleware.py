import logging

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.startswith('/static/'):
            method = request.method
            path = request.path
            
            body_str = ""
            if method in ['POST', 'PUT', 'PATCH'] and request.body:
                try:
                    body_sample = request.body.decode('utf-8')
                    if len(body_sample) > 500:
                        body_sample = body_sample[:500] + "... (truncated)"
                    body_str = f" | Payload: {body_sample}"
                except Exception:
                    body_str = " | Payload: <Binary Data>"
                    
            print(f">>> WEB ACTION: [{method}] {path}{body_str}", flush=True)
            
        response = self.get_response(request)
        return response
