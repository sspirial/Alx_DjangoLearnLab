from django.utils.deprecation import MiddlewareMixin


class ContentSecurityPolicyMiddleware(MiddlewareMixin):
    """
    Sets a basic Content Security Policy header to reduce XSS risk.
    Adjust directives as needed for your app's static/media domains or third-party integrations.
    """

    def process_response(self, request, response):
        # Default-src self; restrict scripts and styles to self
        csp = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "  # allow inline styles for simplicity; prefer removing if possible
            "img-src 'self' data:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        # Only set if not already present
        if 'Content-Security-Policy' not in response:
            response['Content-Security-Policy'] = csp
        return response
