# FROM python:3.11

# WORKDIR /app

# COPY . .

# RUN pip3 install --upgrade  poetry==1.8.3

# RUN python3 -m poetry config virtualenvs.create false \
#     && python3 -m poetry install --no-interaction --no-ansi --without dev \
#     && echo yes | python3 -m poetry cache clear . --all

# RUN chmod +x script/startapp.sh

FROM python:3.11

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN chmod 777 ./entrypoint.sh
ENTRYPOINT ./entrypoint.sh