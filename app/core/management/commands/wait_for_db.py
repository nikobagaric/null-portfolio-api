"""
Django command for waiting for available db
"""
import time

from psycopg2 import OperationalError as Psycopg2OpError

from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django command for wait for DB"""

    def handle(self, *args, **options):
        """Entrypoint for cmd"""
        self.stdout.write('Waiting for databse...')
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except (Psycopg2OpError, OperationalError):
                self.stdout.write('Database unavailable, waiting 1s')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Database available!'))
        