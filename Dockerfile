FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN apt-get update
RUN apt-get install netcat -y bash
RUN pip install -r requirements.txt
COPY . /code/
# run entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]