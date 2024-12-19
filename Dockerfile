FROM python:3.11

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN chmod 777 ./entrypoint.sh
ENTRYPOINT ./entrypoint.sh
