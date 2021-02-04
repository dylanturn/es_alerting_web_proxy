FROM python:alpine3.13

# Env vars that determine how you hit it
ENV BIND_IP="0.0.0.0"
ENV BIND_PORT=8080

# Install the things
ADD requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt

# Add the user that this will run as
USER 1000:1000

# Files that determine what it can do
ADD --chown=1000:1000 pushover_es_proxy.py ./pushover_es_proxy.py
ADD --chown=1000:1000 discord_es_proxy.py ./discord_es_proxy.py

# Expose stuff
EXPOSE 8080