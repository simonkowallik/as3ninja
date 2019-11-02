FROM python:alpine

LABEL org.label-schema.name="AS3 Ninja"
LABEL org.label-schema.description="An AS3 Jinja2 templating engine."
LABEL org.label-schema.vendor="Simon Kowallik"
LABEL org.label-schema.url="https://as3ninja.readthedocs.io/"
LABEL org.label-schema.vcs-url="https://github.com/simonkowalli/as3ninja"
LABEL org.label-schema.schema-version="1.0"
LABEL org.label-schema.docker.cmd="docker run -d -p 8000:8000 as3ninja"
LABEL org.label-schema.version="0.1.0"

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

WORKDIR /as3ninja

RUN apk update --no-cache; \
    apk add --no-cache \
            bash \
            git \
            make \
            openssl \
            vim \
            ;
RUN apk add --no-cache \
            --virtual .build-deps \
            alpine-sdk \
            ;
RUN pip3 install --no-cache-dir \
            flake8 \
            pipenv \
            pylint \
            ;
RUN addgroup as3ninja; \
        adduser -h /as3ninja -s /sbin/nologin -G as3ninja -S -D -H as3ninja;

ADD . /as3ninja

RUN bash -c " \
            pip3 install --no-cache-dir -r <(pipenv lock --requirements); \
            "

RUN apk del .build-deps

RUN chown -R as3ninja.as3ninja /as3ninja

USER as3ninja

EXPOSE 8000

CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "as3ninja.api:app"]
