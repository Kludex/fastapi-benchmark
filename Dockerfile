FROM python:3.8-slim

WORKDIR /app

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt /tmp/
RUN pip install --upgrade pip==21.1.1 --no-cache-dir && \
    pip install -r /tmp/requirements.txt --no-cache-dir

COPY main.py .

EXPOSE 8000
