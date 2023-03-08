FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./src /code

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]