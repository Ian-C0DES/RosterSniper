FROM nginx:1.19-alpine

COPY ./default.conf /etc/nginx/conf.d/

RUN mkdir -p /logs/nginx/ \
    && touch /logs/nginx/nginx-{access,error}.log
