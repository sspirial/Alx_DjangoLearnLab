Django Security Hardening Summary
================================

This document summarizes the security measures configured in this project.

Settings hardening (LibraryProject/settings.py)
- DEBUG is controlled by environment variable `DJANGO_DEBUG`. In production set it to `False`.
- ALLOWED_HOSTS read from `DJANGO_ALLOWED_HOSTS` (comma-separated) in production.
- SECURE_SSL_REDIRECT is controlled by `DJANGO_SECURE_SSL_REDIRECT`.
- HSTS settings are available via env (`DJANGO_SECURE_HSTS_SECONDS`, `DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS`, `DJANGO_SECURE_HSTS_PRELOAD`).
- `SECURE_CONTENT_TYPE_NOSNIFF = True` and `X_FRAME_OPTIONS = 'DENY'` are enabled.
- Secure cookies: `SESSION_COOKIE_SECURE = True`, `CSRF_COOKIE_SECURE = True`.
- HttpOnly cookies: `SESSION_COOKIE_HTTPONLY = True`, `CSRF_COOKIE_HTTPONLY = True`.
- `SECURE_REFERRER_POLICY = 'same-origin'`.
- CSRF trusted origins can be set via `DJANGO_CSRF_TRUSTED_ORIGINS`.

CSRF protection
- All POST forms include `{% csrf_token %}`. See `bookshelf/templates/bookshelf/book_form.html` and `form_example.html`.
- Django's `CsrfViewMiddleware` is enabled by default.

CSP (Content Security Policy)
- Custom middleware `bookshelf.middleware.ContentSecurityPolicyMiddleware` sets a default CSP:
  `default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'`.
  Adjust directives as needed for your environment.

Safe data handling
- Views use Django ORM queries and avoid raw SQL.
- Input validation is performed using Django forms. See `bookshelf/forms.py` and usages in `bookshelf/views.py`.
- Example: `book_list` safely filters by title/author using `icontains` and `Q` objects.

Manual testing checklist
1. Ensure DEBUG is False and HTTPS is enabled in production. Set env vars accordingly.
2. Visit `/books/` and use the search box; verify that no errors occur with special characters.
3. Create/edit a book; tamper with fields and verify form validation prevents invalid data.
4. Confirm the presence of the `Content-Security-Policy` header in responses.
5. Verify cookies are marked `Secure` and `HttpOnly` when using HTTPS.
6. Confirm forms have CSRF tokens and that CSRF attacks are rejected.
