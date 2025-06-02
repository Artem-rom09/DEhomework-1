
FROM python:3.9-slim-buster


WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .


CMD ["bash", "-c", "python python_transformer.py && python python_loader.py"]