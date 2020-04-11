import pymongo
from flask import current_app


class MongoDBConnect:
    """MongoDBConnect"""

    def __init__(self, db_name='vbiz'):
        super().__init__()
        self.connection = False
        self.db = False
        self.error = ''
        try:
            if not db_name:
                raise Exception('Not provide db name')

            self.connection = pymongo.MongoClient(
                'mongodb://%s:%s@%s:%s' % (
                    current_app.config['MONGODB_CONFIG']['db_user'],
                    current_app.config['MONGODB_CONFIG']['db_password'],
                    current_app.config['MONGODB_CONFIG']['db_host'],
                    current_app.config['MONGODB_CONFIG']['db_port']
                )
            )
            self.db = self.connection[db_name]
        except Exception as e:
            self.error = e
            print('err: %s' % (e))
