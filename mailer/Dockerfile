FROM python:3.6-alpine

ADD . /code

RUN pip3 install -r /code/requirements.txt --no-cache-dir

CMD ["python3", "-u", "/code/consumer.py"]
