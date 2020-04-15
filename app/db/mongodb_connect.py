import pymongo
from flask import current_app


class MongoDBConnect:
    """MongoDBConnect"""

    def __init__(self):
        super().__init__()
        self.connection = pymongo.MongoClient(
            'mongodb://%s:%s@%s:%s' % (
                current_app.config['MONGODB_CONFIG']['db_user'],
                current_app.config['MONGODB_CONFIG']['db_password'],
                current_app.config['MONGODB_CONFIG']['db_host'],
                current_app.config['MONGODB_CONFIG']['db_port']
            )
        )
