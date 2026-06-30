FROM python:3.11-slim

WORKDIR /app

COPY entrans-hr-hub/myproject/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "python entrans-hr-hub/myproject/manage.py migrate && python entrans-hr-hub/myproject/manage.py runserver 0.0.0.0:8000"]
