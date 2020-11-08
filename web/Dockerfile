FROM python

RUN groupadd flaskgroup && useradd -m -g flaskgroup -s /bin/bash flask
RUN mkdir -p /home/flask/app/web
WORKDIR /home/flask/app/web

COPY requirements.txt /home/flask/app/web/

RUN pip3 install --no-cache-dir -r requirements.txt

COPY ./project /home/flask/app/web

# RUN chown -R flask:flaskgroup /home/flask
# USER flask
