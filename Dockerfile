FROM python:3.7-slim
RUN apt-get update \
   && apt-get install -y gcc python3-dev tzdata \
   && apt-get install -y default-libmysqlclient-dev \
   && apt-get install -y make \
   && apt-get clean
COPY . /app

WORKDIR /app
RUN pip install -r requirements.txt

WORKDIR /app/docs
RUN make clean && make html

WORKDIR /app
CMD exec gunicorn -b :5103 --access-logfile - --error-logfile - app:app
