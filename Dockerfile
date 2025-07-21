FROM python:3.9-alpine3.13
LABEL maintainer='rect1fy'
ENV PYTHONUNBUFFERED=1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8000

ARG DEV=false
RUN python -m venv /py && \
    # Upgrade pip
    /py/bin/pip install --upgrade pip && \
    # Install runtime dependencies
    apk add --update --no-cache postgresql-client jpeg-dev && \
    # Install build dependencies
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base \
        postgresql-dev \
        musl-dev \
        zlib \
        zlib-dev && \
    # Install Python packages
    /py/bin/pip install -r /tmp/requirements.txt && \
    # Install dev dependencies if DEV is true
    if [ "$DEV" = "true" ]; then \
        /py/bin/pip install -r /tmp/requirements.dev.txt; \
    fi && \
    # Clean up temporary files and build dependencies
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    # Create a system user for running the Django app
    adduser --disabled-password --no-create-home django-user && \
    mkdir -p vol/web/media && \
    mkdir -p vol/web/static && \
    chown -R django-user:django-user /vol && \
    chmod -R 755 /vol

ENV PATH="/py/bin:$PATH"
USER django-user