FROM python:3.7-slim
RUN apt-get update && apt-get install -y make gcc python3-dev python3-sphinx
RUN apt-get install -y default-libmysqlclient-dev
WORKDIR /vapi
COPY . /vapi
RUN pip install -r requirements.txt
WORKDIR /vapi/docs
RUN cd /vapi/docs && make clean && make html; exit 0
WORKDIR /vapi
CMD exec gunicorn -b :5103 --access-logfile - --error-logfile - app:app
