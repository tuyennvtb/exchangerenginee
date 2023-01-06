FROM python:3.7-slim-buster
RUN apt update && apt install -y build-essential libmariadbclient-dev unzip && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /

RUN pip install -r /requirements.txt
WORKDIR /usr/src/app
COPY . /usr/src/app/
RUN cp sources/huobi_Python-2.2.0.zip /tmp && cd /tmp && unzip huobi_Python-2.2.0.zip && cd huobi_Python-2.2.0 && python3 setup.py install && cd /tmp && rm -rfv huobi_Python-2.2.0*
# COPY sources/patches/binance/streams.py /usr/local/lib/python3.7/site-packages/binance/streams.py
ENTRYPOINT ["/bin/bash"]