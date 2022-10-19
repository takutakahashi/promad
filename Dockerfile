FROM python:3.10

WORKDIR /app

ADD requirements.txt .
RUN pip install -r requirements.txt
ADD main.py .
ADD entrypoint.sh .
ADD lib/ ./lib/
CMD ["./entrypoint.sh"]