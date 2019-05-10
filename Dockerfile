FROM python:3.7

WORKDIR /kblab
ADD . /kblab/

RUN pip install -r requirements.txt
RUN cd /kblab/client && ./setup.py install

