Deployment: Enabling HTTPS and Secure Headers
=============================================

This guide explains how to serve the Django app over HTTPS, enforce redirects, and configure security headers in production.

Prerequisites
- A public domain name pointing to your server
- Root or sudo access
- Django app deployed (e.g., with Gunicorn/Uvicorn) and a reverse proxy (Nginx or Apache)

Environment variables (production)
- DJANGO_DEBUG=False
- DJANGO_ALLOWED_HOSTS=example.com,www.example.com
- DJANGO_SECURE_SSL_REDIRECT=true           # optional; defaults to true when DEBUG=false
- DJANGO_SECURE_HSTS_SECONDS=31536000       # 1 year
- DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS=true
- DJANGO_SECURE_HSTS_PRELOAD=true           # only if you intend to preload
- DJANGO_SECURE_PROXY_SSL_HEADER="HTTP_X_FORWARDED_PROTO,https"  # when behind reverse proxy
- DJANGO_CSRF_TRUSTED_ORIGINS=https://example.com,https://www.example.com

Nginx (reverse proxy + TLS termination)
1. Install certbot and nginx plugin (Ubuntu):
   - sudo apt-get update
   - sudo apt-get install -y nginx certbot python3-certbot-nginx

2. Basic Nginx site config (replace example.com and upstream as needed):

   server {
       listen 80;
       server_name example.com www.example.com;
       # Redirect all HTTP to HTTPS
       return 301 https://$host$request_uri;
   }

   server {
       listen 443 ssl http2;
       server_name example.com www.example.com;

       # SSL certificates (provisioned by certbot)
       ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

       # Security headers (Django also sets these; duplication is mostly harmless)
       add_header X-Content-Type-Options nosniff always;
       add_header X-Frame-Options DENY always;
       add_header Referrer-Policy same-origin always;
       # Example CSP if you want at the proxy as well (optional):
       # add_header Content-Security-Policy "default-src 'self'" always;

       # Pass through the original protocol for Django to detect HTTPS
       proxy_set_header X-Forwarded-Proto $scheme;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       proxy_set_header Host $host;

       location /static/ {
           alias /var/www/example.com/static/;  # adjust to your static root
       }

       location / {
           proxy_pass http://127.0.0.1:8000;   # Gunicorn/Uvicorn upstream
           proxy_http_version 1.1;
           proxy_set_header Connection "";     # keep-alive
       }
   }

3. Provision Let’s Encrypt certificates (auto config):
   - sudo certbot --nginx -d example.com -d www.example.com
   - sudo systemctl reload nginx

Apache (reverse proxy + TLS termination)
1. Install Apache and certbot plugin:
   - sudo apt-get install -y apache2 certbot python3-certbot-apache

2. Enable required modules:
   - sudo a2enmod ssl proxy proxy_http headers

3. VirtualHost config:

   <VirtualHost *:80>
       ServerName example.com
       ServerAlias www.example.com
       RewriteEngine On
       RewriteRule ^ https://%{SERVER_NAME}%{REQUEST_URI} [R=301,L]
   </VirtualHost>

   <VirtualHost *:443>
       ServerName example.com
       ServerAlias www.example.com

       SSLEngine on
       SSLCertificateFile /etc/letsencrypt/live/example.com/fullchain.pem
       SSLCertificateKeyFile /etc/letsencrypt/live/example.com/privkey.pem

       # Security headers
       Header always set X-Content-Type-Options "nosniff"
       Header always set X-Frame-Options "DENY"
       Header always set Referrer-Policy "same-origin"

       # Forwarded proto for Django
       RequestHeader set X-Forwarded-Proto "https"

       ProxyPreserveHost On
       ProxyPass / http://127.0.0.1:8000/
       ProxyPassReverse / http://127.0.0.1:8000/
   </VirtualHost>

4. Provision Let’s Encrypt certificates:
   - sudo certbot --apache -d example.com -d www.example.com
   - sudo systemctl reload apache2

Gunicorn/Uvicorn notes
- Bind your ASGI/WSGI server to 127.0.0.1:8000 and let the reverse proxy terminate TLS.
- Ensure environment variables are set for Django (see above).

Django settings recap (already configured)
- SECURE_SSL_REDIRECT=True in production; HSTS enabled with includeSubDomains and preload by default.
- SECURE_PROXY_SSL_HEADER should be set in env when using a proxy.
- Cookies are Secure/HttpOnly; CSP is set via middleware.

Verification checklist
- HTTP requests redirect to HTTPS.
- HSTS header is present in responses in production.
- Cookies have the Secure and HttpOnly attributes.
- `request.is_secure()` is True behind the proxy.
- SSL certificates are valid and auto-renew via certbot.
