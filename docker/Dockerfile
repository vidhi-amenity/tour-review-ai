# syntax=docker/dockerfile:experimental

FROM ubuntu:20.04

EXPOSE 8000

ENV APP=/home/app
RUN mkdir $APP
RUN mkdir $APP/staticfiles
RUN mkdir $APP/mediafiles
RUN mkdir $APP/files
WORKDIR $APP

# Copy project
COPY . $APP_HOME

# setting this up to avoid the TZ input issue
ENV TZ="America/New_York"
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update && apt-get install -y apt-transport-https 
# upper ni line me add kareli chhe 

RUN apt-get update && apt-get install -y python3 python3-pip default-libmysqlclient-dev libglib2.0-0 libnss3 libxcb-randr0-dev libxcb-xtest0-dev libxcb-xinerama0-dev libxcb-shape0-dev libxcb-xkb-dev pkg-config libcairo2-dev

RUN pip3 install -r requirements.txt
RUN pip3 install gunicorn

RUN apt -f install -y
RUN apt-get install -y wget
# RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
# RUN apt-get install ./google-chrome-stable_current_amd64.deb -y
RUN pip install xlwt
# Run database migrations
# RUN python3 manage.py migrate

CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "tour_reviews_ai.wsgi:application"]