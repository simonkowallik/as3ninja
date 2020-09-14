FROM alpine:3.12 AS base

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
            alpine-sdk \
            bash \
            git \
            libffi-dev \
            make \
            openssl \
            openssl-dev \
            python3 \
            py3-cffi \
            py3-pip \
            python3-dev \
            ;

RUN pip3 install --no-cache-dir \
            poetry \
            ;

RUN mkdir /build

WORKDIR /as3ninja

ADD ./as3ninja /as3ninja/as3ninja
ADD ./pyproject.toml /as3ninja
ADD ./poetry.lock /as3ninja

RUN echo "* create stubs: docs, tests, README.md for poetry build to succeed."; \
    mkdir docs tests; touch README.md; \
    poetry build -f wheel; \
    poetry export --without-hashes \
    -f requirements.txt -o requirements.txt; \
    export PYTHONPATH=/build/lib/python3.8/site-packages; \
    export PATH="$PATH:/build/bin"; \
    pip3 install \
       --no-cache-dir \
       --prefix /build \
       --ignore-installed \
       -r requirements.txt || exit 1; \
    pip3 install \
       --no-cache-dir \
       --prefix /build \
       --no-deps \
       $(ls dist/*.whl) || exit 1; \
    echo "* The above requirements error about poetry and pyrsistent is save to ignore."

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
    mkdir /as3ninja; \
    addgroup as3ninja; \
    adduser -h /as3ninja -s /sbin/nologin -G as3ninja -S -D -H as3ninja; \
    chown -R as3ninja.as3ninja /as3ninja; \
    chown -R as3ninja.as3ninja /home;

USER as3ninja

EXPOSE 8000

CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "as3ninja.api:app"]
