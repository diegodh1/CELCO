FROM  ubuntu:18.04

RUN apt-get update && apt-get -y upgrade && apt-get -y install python3-dev && apt-get -y install python3-pip\
    && pip3 install --upgrade pip && apt-get -y install g++ \
    && apt-get -y install curl && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/ubuntu/18.04/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update && ACCEPT_EULA=Y apt-get -y install msodbcsql17 && apt-get -y install unixodbc-dev

WORKDIR /app

COPY . /app

RUN pip3  install -r requirements.txt

CMD [ "python3", "src/app.py" ]