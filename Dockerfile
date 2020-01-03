FROM alpine:3.11 AS base

LABEL org.label-schema.name="AS3 Ninja"
LABEL org.label-schema.vendor="Simon Kowallik"
LABEL org.label-schema.description="AS3 Ninja is a templating and validation engine for your AS3 declarations."
LABEL org.label-schema.url="https://as3ninja.readthedocs.io/"
LABEL org.label-schema.vcs-url="https://github.com/simonkowallik/as3ninja"
LABEL org.label-schema.docker.cmd="docker run --rm -d -p 8000:8000 as3ninja"
LABEL org.label-schema.schema-version="1.0"

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# build stage
FROM base as build

RUN apk update --no-cache; \
    apk add --no-cache \
            bash \
            git \
            make \
            openssl \
            python3 \
            vim \
            alpine-sdk \
            python3-dev \
            ; \
    pip3 install --no-cache-dir \
            pipenv \
            ;

RUN mkdir /build

ADD . /as3ninja

WORKDIR /as3ninja

RUN bash -c "export PYTHONPATH=/build/lib/python3.8/site-packages; \
             export PATH=\"$PATH:/build/bin\"; \
             pip3 install \
                --no-cache-dir \
                --ignore-installed \
                --prefix /build \
                -r <(pipenv --bare lock --requirements); \
            "

RUN bash -c "rm -rf .[a-z]*; \
             ls | egrep -v '(as3ninja|LICENSE)' | xargs rm -rf; \
             mv /as3ninja /build/as3ninja; \
            "

# final image
FROM base

WORKDIR /

COPY --from=build /build /usr

RUN apk update --no-cache; \
    apk add --no-cache \
            bash \
            git \
            openssl \
            python3 \
            vim \
            ; \
    pip3 install --no-cache-dir \
            email-validator \
            ; \
    mv /usr/as3ninja /as3ninja; \
    addgroup as3ninja; \
    adduser -h /as3ninja -s /sbin/nologin -G as3ninja -S -D -H as3ninja; \
    chown -R as3ninja.as3ninja /as3ninja;

USER as3ninja

EXPOSE 8000

CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "as3ninja.api:app"]
