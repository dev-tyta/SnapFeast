import re
from django.core.exceptions import DisallowedHost

class AllowSubdomainMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        allowed_domain = 'snapfeast.onrender.com'
        host = request.get_host().split(':')[0]  # Remove port
        if re.match(rf'^[\w.-]+\.{allowed_domain}$', host) or host == allowed_domain:
            return self.get_response(request)
        else:
            raise DisallowedHost(f"Invalid HTTP_HOST header: {host}")
