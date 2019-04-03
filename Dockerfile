FROM python:3.6-alpine

RUN apk add --no-cache postgresql-libs postgresql-dev nmap linux-headers gcc musl-dev

ADD requirements.txt /code/
WORKDIR /code
RUN pip3 install -r requirements.txt --no-cache-dir

COPY *.py *.sh /code/
COPY web_app /code/web_app
COPY migrations /code/migrations

EXPOSE 5000
ENV FLASK_APP /code/first_app.py
ENV APP_MAIL_USERNAME "dimalynin@gmail.com"
ENV APP_MAIL_PASSWORD ""

CMD ["/code/run_server.sh"]
# CMD ["ls", "/code"]
