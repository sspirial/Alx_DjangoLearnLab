Bookshelf Permissions & Groups
================================

This app demonstrates fine-grained access control using Django permissions and groups.

What we added
- Custom permissions on the `Book` model: `can_view`, `can_create`, `can_edit`, `can_delete`.
- Views protected with `@permission_required`.
- A management command to create groups and assign permissions.

Groups
- Viewers: can_view
- Editors: can_view, can_create, can_edit
- Admins: can_view, can_create, can_edit, can_delete

How to set up
1) Apply migrations so custom permissions are created in the DB:
   - python manage.py makemigrations
   - python manage.py migrate
2) Initialize groups and permissions:
   - python manage.py init_roles
3) Create users and assign them to groups via the Django admin (/admin/) or shell.

Testing
- Log in as a user in each group and visit:
  - /books/ (list, requires can_view)
  - /books/create/ (requires can_create)
  - /books/<id>/edit/ (requires can_edit)
  - /books/<id>/delete/ (requires can_delete)

Notes
- The project uses a custom user model `bookshelf.CustomUser`.
- If you change permission codenames, update the decorators and the management command accordingly.
