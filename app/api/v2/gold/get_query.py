
import datetime as dt


def get_query(type=0, **kwargs):
    query = False
    if type == 0:
        query = [
            {
                '$sort': {
                    'datetime': -1
                }
            }, {
                '$limit': 1
            }
        ]
    elif type == 1:
        dnow = dt.datetime.now()
        date_from = kwargs['date_from'] if 'date_from' in kwargs else dnow - \
            dt.timedelta(30)
        date_to = kwargs['date_to'] if 'date_to' in kwargs else dnow
        query = [
            {
                '$match': {
                    'datetime': {
                        '$gte': date_from,
                        '$lt': date_to
                    }
                }
            }, {
                '$group': {
                    '_id': {
                        '$dayOfYear': '$datetime'
                    },
                    'temp_data': {
                        '$first': '$$ROOT'
                    }
                }
            }, {
                '$sort': {
                    '_id': 1
                }
            }, {
                '$replaceRoot': {
                    'newRoot': '$temp_data'
                }
            }
        ]
    return query
