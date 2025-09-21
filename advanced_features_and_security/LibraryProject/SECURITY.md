Django Security Hardening Summary
================================

This document summarizes the security measures configured in this project.

Settings hardening (LibraryProject/settings.py)
- DEBUG is controlled by environment variable `DJANGO_DEBUG`. In production set it to `False`.
- ALLOWED_HOSTS read from `DJANGO_ALLOWED_HOSTS` (comma-separated) in production.
- HTTPS enforcement: `SECURE_SSL_REDIRECT` defaults to `True` when `DEBUG=False`. Override via `DJANGO_SECURE_SSL_REDIRECT` if needed.
- HSTS: defaults to 1 year (`SECURE_HSTS_SECONDS=31536000`) when `DEBUG=False`, including subdomains and preload. Control via env: `DJANGO_SECURE_HSTS_SECONDS`, `DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS`, `DJANGO_SECURE_HSTS_PRELOAD`.
- `SECURE_CONTENT_TYPE_NOSNIFF = True` and `X_FRAME_OPTIONS = 'DENY'` are enabled.
- Secure cookies: default to `True` when `DEBUG=False`. Overridable via `DJANGO_SESSION_COOKIE_SECURE`, `DJANGO_CSRF_COOKIE_SECURE`.
- HttpOnly cookies: `SESSION_COOKIE_HTTPONLY = True`, `CSRF_COOKIE_HTTPONLY = True`.
- `SECURE_REFERRER_POLICY = 'same-origin'`.
- CSRF trusted origins can be set via `DJANGO_CSRF_TRUSTED_ORIGINS`.
- Reverse proxy TLS termination: set `DJANGO_SECURE_PROXY_SSL_HEADER="HTTP_X_FORWARDED_PROTO,https"` when behind a trusted proxy that sets `X-Forwarded-Proto: https`.

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

Security review
- Transport security: All HTTP traffic is redirected to HTTPS in production; HSTS ensures browsers use HTTPS for subsequent requests. Include-subdomains and preload are enabled by default; only enable preload if you intend to submit your domain to the preload list.
- Cookie security: Session and CSRF cookies are marked Secure and HttpOnly; reduces risk of interception and XSS exfiltration.
- Clickjacking: `X-Frame-Options: DENY` and CSP `frame-ancestors 'none'` mitigate UI redress attacks.
- MIME sniffing/XSS: `X-Content-Type-Options: nosniff` is set; CSP reduces script injection vectors. Note that `SECURE_BROWSER_XSS_FILTER` is deprecated and intentionally not used.
- Reverse proxy awareness: When using TLS termination at a proxy, configure `DJANGO_SECURE_PROXY_SSL_HEADER` to ensure Django regards requests as secure for building `https://` URLs and setting secure cookies.

Potential improvements
- Enable and tune a stricter CSP (e.g., nonces for scripts, eliminate `'unsafe-inline'` for styles if feasible).
- Add Subresource Integrity (SRI) for any third-party assets if introduced later.
- Use `SESSION_COOKIE_SAMESITE='Lax'` or `'Strict'` based on app needs; default is framework-dependent.
- Consider security scanning (e.g., OWASP ZAP) in CI for regressions.

Manual testing checklist
1. Ensure DEBUG is False and HTTPS is enabled in production. Set env vars accordingly.
2. Visit `/books/` and use the search box; verify that no errors occur with special characters.
3. Create/edit a book; tamper with fields and verify form validation prevents invalid data.
4. Confirm the presence of the `Content-Security-Policy` header in responses.
5. Verify cookies are marked `Secure` and `HttpOnly` when using HTTPS.
6. Confirm forms have CSRF tokens and that CSRF attacks are rejected.
7. Confirm HTTP to HTTPS redirect (http:// to https://) and that HSTS header is present in production.
8. If using a reverse proxy, confirm `SECURE_PROXY_SSL_HEADER` is set and Django recognizes requests as secure (`request.is_secure()` is True).
