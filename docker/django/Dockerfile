FROM python:slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip \
	&& pip install -r requirements.txt \
	&& pip install gunicorn \
	&& pip cache purge

COPY django_project ./django_project

RUN mkdir -p /logs/gunicorn/ \
    && touch /logs/gunicorn/gunicorn-{access,error}.log

COPY docker/django/entrypoint.sh .
ENTRYPOINT ["sh", "/app/entrypoint.sh"]
