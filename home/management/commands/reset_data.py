from django.core.management.base import BaseCommand
from django.db import connection
from home.models import EmpMast, EnrollMast, MonitorData, MachineMast

class Command(BaseCommand):
    help = 'Delete all data and reset primary keys'

    def handle(self, *args, **kwargs):
        # Delete all data
        EmpMast.objects.all().delete()
        EnrollMast.objects.all().delete()
        # MonitorData.objects.all().delete()
        # MachineMast.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('Successfully deleted all data.'))

        # Reset primary key sequences
        if connection.vendor == 'sqlite':
            self.reset_sqlite_sequence('home_empmast')
            self.reset_sqlite_sequence('home_enrollmast')
            # self.reset_sqlite_sequence('home_monitordata')
            # self.reset_sqlite_sequence('home_machinemast')
        elif connection.vendor == 'postgresql':
            self.reset_postgres_sequence('home_empmast', 'home_empmast_id_seq')
            self.reset_postgres_sequence('home_enrollmast', 'home_enrollmast_id_seq')
            # self.reset_postgres_sequence('home_monitordata', 'home_monitordata_id_seq')
            # self.reset_postgres_sequence('home_machinemast', 'home_machinemast_id_seq')

    def reset_sqlite_sequence(self, table_name):
        with connection.cursor() as cursor:
            cursor.execute(f'DELETE FROM sqlite_sequence WHERE name="{table_name}";')

    def reset_postgres_sequence(self, table_name, sequence_name):
        with connection.cursor() as cursor:
            cursor.execute(f'ALTER SEQUENCE {sequence_name} RESTART WITH 1;')
            cursor.execute(f'UPDATE {table_name} SET id = DEFAULT;')
