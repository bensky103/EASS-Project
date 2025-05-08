# tests/Dockerfile 
FROM python:3.11-slim

WORKDIR /code

# 1) copy requirement files *only*
COPY app/requirements.txt          ./app_requirements.txt
COPY auth_service/requirements.txt  ./auth_requirements.txt
COPY stock_service/requirements.txt ./stock_requirements.txt

# 2) install deps — this layer is cached until *any* of the 3 files change
RUN pip install \
        -r app_requirements.txt \
        -r auth_requirements.txt \
        -r stock_requirements.txt \
        pytest pytest-asyncio httpx pyjwt


ENV PYTHONPATH=/code

# 3) now copy the rest of the repo
COPY . /code

CMD ["pytest", "-q"]
