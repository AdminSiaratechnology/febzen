from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.dashboard_url = reverse('dashboard')
        self.select_company_url = reverse('select_company')

    def __call__(self, request):
        path = request.path

        # If user is logged in
        if request.user.is_authenticated:

            # CASE 1: User is logged in but has NOT selected company yet
            needs_company = request.session.get('active_company_id') is None

            if needs_company:
                # Allowed URLs even when company not selected
                allowed_paths = [
                    self.select_company_url,
                    self.logout_url,
                ]

                # If trying to visit anything else → redirect to select_company
                if path not in allowed_paths:
                    return redirect(self.select_company_url)

            # CASE 2: Logged in user going to login page → redirect to dashboard
            if path == self.login_url:
                return redirect(self.dashboard_url)

            return self.get_response(request)

        # If user is NOT logged in
        allowed = [self.login_url, self.logout_url, '/admin/']

        static_url = settings.STATIC_URL
        media_url = getattr(settings, 'MEDIA_URL', None)

        if static_url:
            allowed.append(static_url)
        if media_url:
            allowed.append(media_url)

        for prefix in allowed:
            if prefix and path.startswith(prefix):
                return self.get_response(request)

        return redirect(self.login_url)
