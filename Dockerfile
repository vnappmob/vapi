FROM python:3.7-slim
RUN apt-get update && apt-get install -y gcc python3-dev
RUN apt-get install -y default-libmysqlclient-dev

COPY . /vapi

WORKDIR /vapi/docs
RUN make clean
RUN make html

WORKDIR /vapi
RUN pip install -r requirements.txt

CMD exec gunicorn -b :5103 --access-logfile - --error-logfile - app:app
