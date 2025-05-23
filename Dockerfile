FROM python:3.11-slim

WORKDIR /app

COPY . /app/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000
ENV DJANGO_SETTINGS_MODULE qyzmettap_back.settings.release

ENTRYPOINT ["/entrypoint.sh"]
