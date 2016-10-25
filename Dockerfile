FROM python:3.4-slim
ADD . /src
WORKDIR /src
RUN pip install -r requirements.txt
CMD python ./bot/app.py
