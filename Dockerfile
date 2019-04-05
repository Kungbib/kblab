FROM python:3.7

WORKDIR /kblab
ADD . /kblab/

RUN pip install -r requirements.txt
RUN ./setup.py install

