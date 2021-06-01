# syntax=docker/dockerfile:1

FROM python:3

# Step 1: Copy Oracle instant client
# ----------------------------------------
WORKDIR    /opt/oracle
RUN        apt-get update && apt-get install -y libaio1 wget unzip \
            && wget https://download.oracle.com/otn_software/linux/instantclient/instantclient-basiclite-linuxx64.zip \
            && unzip instantclient-basiclite-linuxx64.zip \
            && rm -f instantclient-basiclite-linuxx64.zip \
            && cd /opt/oracle/instantclient* \
            && rm -f *jdbc* *occi* *mysql* *README *jar uidrvci genezi adrci \
            && echo /opt/oracle/instantclient* > /etc/ld.so.conf.d/oracle-instantclient.conf \
            && ldconfig

RUN         apt-get update && apt-get install -y net-tools netcat
# Step 2: Install requirements.txt using pip
# ----------------------------------------
ENV         PYTHONUNBUFFERED=1
WORKDIR     /code
COPY        requirements.txt /code/
RUN         pip install -r requirements.txt

# Step 3: Copy Django Code
# ----------------------------------------

COPY        . /code/

EXPOSE 8000

HEALTHCHECK CMD curl --fail http://localhost:8000/ || exit 1

CMD ["/code/runserver.sh"]