FROM python:3.7-slim
RUN apt-get update && apt-get install -y gcc python3-dev
RUN apt-get install -y default-libmysqlclient-dev
WORKDIR /vapi
COPY . /vapi
RUN pip install -r requirements.txt
CMD exec gunicorn -b :5103 --access-logfile - --error-logfile - app:app
