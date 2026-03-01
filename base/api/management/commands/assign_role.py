from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group

class Command(BaseCommand):
    help = 'Assign a user to a role'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)
        parser.add_argument('role', type=str, choices=['Viewer', 'Stocker', 'Admin'])

    def handle(self, *args, **options):
        user = User.objects.get(username=options['username'])
        group = Group.objects.get(name=options['role'])
        user.groups.add(group)
        self.stdout.write(self.style.SUCCESS(f'Added {user} to {group}'))
