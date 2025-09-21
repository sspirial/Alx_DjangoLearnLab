from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from bookshelf.models import Book


class Command(BaseCommand):
    help = "Initialize default groups (Viewers, Editors, Admins) and assign Book permissions."

    def handle(self, *args, **options):
        ct = ContentType.objects.get_for_model(Book)

        perm_codes = ['can_view', 'can_create', 'can_edit', 'can_delete']
        perms = {code: Permission.objects.get(codename=code, content_type=ct) for code in perm_codes}

        viewers, _ = Group.objects.get_or_create(name='Viewers')
        editors, _ = Group.objects.get_or_create(name='Editors')
        admins, _ = Group.objects.get_or_create(name='Admins')

        # Assign permissions
        viewers.permissions.set([perms['can_view']])
        editors.permissions.set([perms['can_view'], perms['can_create'], perms['can_edit']])
        admins.permissions.set(list(perms.values()))

        self.stdout.write(self.style.SUCCESS('Groups and permissions initialized successfully.'))
