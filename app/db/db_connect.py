"""app/db/db_connect.py"""
import MySQLdb
from flask import current_app


class VDBConnect:
    """@VDBConnect"""

    def __init__(self, db='vapi_db'):
        try:
            self.conn = MySQLdb.connect(
                host=current_app.config['DATABASE_CONFIG']['db_host'],
                user=current_app.config['DATABASE_CONFIG']['db_user'],
                passwd=current_app.config['DATABASE_CONFIG']['db_password'],
                db=db,
                charset='utf8mb4',
                use_unicode=True)
            self.cursor = self.conn.cursor(
                cursorclass=MySQLdb.cursors.SSDictCursor)
            self.connected = True
        except MySQLdb.Error as err:  #pylint: disable=E
            self.error = err
            self.connected = False

    def writecommit(self, statements, vals=()):
        """@writecommit"""
        self.cursor.execute(statements, vals)
        self.conn.commit()

    def write(self, statements, vals=()):
        """@write"""
        self.cursor.execute(statements, vals)

    def commit(self):
        """@commit"""
        self.conn.commit()

    def lastrowid(self):
        """@lastrowid"""
        return self.cursor.lastrowid

    def readone(self, statements, vals=()):
        """@fetchone"""
        self.cursor.execute(statements, vals)
        return self.cursor.fetchone()

    def readall(self, statements, vals=()):
        """@fetchall"""
        self.cursor.execute(statements, vals)
        return self.cursor.fetchall()

    def close(self):
        """@close"""
        self.cursor.close()
        self.conn.close()

    def get_slash_setting(self):
        """@get_slash_setting"""
        statements = ("SELECT * FROM vnappmob_slash_setting;")
        self.cursor.execute(statements)
        vnappmob_slash_setting = self.cursor.fetchall()
        settings = {}
        for k in vnappmob_slash_setting:
            settings[k['setting_key']] = k['setting_value']
        return settings
