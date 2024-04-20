FROM python:3.12.3-alpine3.18

WORKDIR /src

RUN apk update \
    && apk --no-cache --update add build-base 
    
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xvzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib/ && \
    ./configure --prefix=/usr && \
    make && \
    make install

WORKDIR /app
COPY . .
RUN pip install -r requeriments.txt

ENTRYPOINT ["python", "first.py"]