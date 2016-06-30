FROM continuumio/anaconda

MAINTAINER QCR

ADD . /src

RUN cd /src; pip install -r requirements.txt

EXPOSE 5000

RUN chmod -x /src/launch.sh
CMD sh /src/launch.sh
