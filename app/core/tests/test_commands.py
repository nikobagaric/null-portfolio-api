# noqa
"""
Test custom Django manage commands
"""
from unittest.mock import patch

from psycopg2 import OperationalError as Psycopg2Error

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase


@patch('core.management.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):
    """Test commands."""

    def test_wait_for_db_ready(self, patched_check):
        """Test waiting for database - ready state"""
        patched_check.return_value = True # magic mock object :p

        call_command('wait_for_db')

        patched_check.assert_called_once_with(databases=['default']) 
        # checks if right thing is called on test

    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """Test waiting for databse - not ready - OperationalError"""
        patched_check.side_effect = [Psycopg2Error] * 2 + \
            [OperationalError] * 3 + [True]

        """
        confusing test mocking;
        first two times we called mocked error;
        we wanna raise the psycopg2error twice;
        next 3 times we raise the operationalerror; mocks real situation;
        on the sixth time it returns true, doesn't raise an exception
        """

        call_command('wait_for_db')

        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=['default'])
