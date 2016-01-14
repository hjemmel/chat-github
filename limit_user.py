from django.contrib.auth import logout


class LimitUserMiddleware:
    def process_request(self, request):
        if request.user.is_authenticated():
            if (request.user.username != 'test'
                and request.user.username != 'test1'):
                logout(request)
