# LibraryProject

This is the initial setup for the Django project named LibraryProject. It was created using Django's startproject command and will serve as the foundation for developing Django applications.

## Structure
- `manage.py`: Command-line utility to interact with the project.
- `LibraryProject/settings.py`: Main configuration for the Django project.
- `LibraryProject/urls.py`: URL declarations for the project.
- `LibraryProject/wsgi.py` and `asgi.py`: Entry points for WSGI/ASGI-compatible web servers.

## Getting Started
To run the development server:

```bash
C:/Users/emmun/projects/Alx_DjangoLearnLab/.venv/Scripts/python.exe manage.py runserver
```

Then open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser to view the default Django welcome page.

## Custom User Model

This copy has been extended to use a custom user model at `accounts.CustomUser` (based on `AbstractUser`) with two extra fields:

- `date_of_birth: DateField`
- `profile_photo: ImageField` (requires Pillow)

Settings updates:

- `INSTALLED_APPS` includes `accounts`
- `AUTH_USER_MODEL = 'accounts.CustomUser'`
- Media configured with `MEDIA_URL` and `MEDIA_ROOT`

Admin uses a customized `UserAdmin` to manage the extra fields.

### Migrations and DB

Because swapping the user model must happen at project start, this copy uses a fresh `db.sqlite3`. If you run into migration history issues, delete the DB file and migrate again.

### Requirements

Install Pillow for image fields.
