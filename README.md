## VNAppMob API Project

This project is an open project that allows users to fetch some basic data in Vietnam. Feel free to follow the project docs at https://api.vnappmob.com

If you need more information, please hook us at hi@vnappmob.com


## Documentation

```
cd docs && make clean && make html && cd ..
```

## Local dev

Make sure to install system mysqlclient following documents https://pypi.org/project/mysqlclient/

```
pip install mysqlclient
```

Create virtual environments 
```
python -m venv .venv
```

Active virtual environments and install requirements packages
```
source .venv/bin/activate
pip install -r requirements.txt
Or force install latest dependecies...
pip install --upgrade --force-reinstall -r requirements.txt
```

Set variables for running
```
FLASK_APP=app.py FLASK_ENV=development MONGODB_HOST={} MONGODB_USER={} MONGODB_PASSWORD={} flask run
```
