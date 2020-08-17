# Required for running myRobogals on newer versions of macOS
import os
if os.uname()[0] == 'Darwin':
    import pymysql
    pymysql.install_as_MySQLdb()

# Allow loading of sample data to SQLite
import sys
for cmdarg in sys.argv:
    if cmdarg == 'loaddata':
        from django.db.backends.signals import connection_created
        def activate_foreign_keys(sender, connection, **kwargs):
            if connection.vendor == 'sqlite':
                cursor = connection.cursor()
                cursor.execute('PRAGMA foreign_keys = OFF;')
                print("Disabled foreign key checks while importing fixtures")
        connection_created.connect(activate_foreign_keys)
