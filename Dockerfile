
FROM tiangolo/uvicorn-gunicorn:python3.11-slim
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY . .
CMD ["python3", "-m", "gunicorn", "src.fastapi_app.app:app", "-c", "src/gunicorn.conf.py"]