FROM python:3.11-slim

WORKDIR /backend

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1
ENV TZ America/Caracas

# install system dependencies
RUN apt-get update \
  && apt-get -y install gcc postgresql \
  && apt-get clean

# support for certains processors
ARG ARCH
ENV ARCH $ARCH

# RUN wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/$ARCH.deb
RUN dpkg -i $ARCH.deb; apt-get install -y -f

# install python dependencies
RUN pip install --upgrade pip
COPY ./backend/requirements.txt /backend/requirements.txt
RUN pip install -r requirements.txt

COPY . /backend