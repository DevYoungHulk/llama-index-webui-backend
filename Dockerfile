FROM ubuntu:20.04

# Get latest root certificates
RUN apt-get update 
# RUN apt-get install -y --no-cache ca-certificates tzdata && update-ca-certificates
RUN apt-get install software-properties-common -y

RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update && apt-get install -y python3.10 python3.10-venv python3.10-dev python3-pip
RUN apt-get install -y libldap2-dev libsasl2-dev python3-openssl
RUN apt-get install -y cmake build-essential pkg-config libgoogle-perftools-dev
RUN python3 --version
RUN python3 -m pip install --upgrade pip

RUN useradd -ms /bin/bash flask
USER flask
WORKDIR /home/flask

COPY ./ ./

ENV PYTHONUNBUFFERED=1 PYTHONHASHSEED=random PYTHONDONTWRITEBYTECODE=1

# Install the required packages
RUN python3 -m pip install -r requirements.txt --no-cache-dir

# PYTHONUNBUFFERED: Force stdin, stdout and stderr to be totally unbuffered. (equivalent to `python -u`)
# PYTHONHASHSEED: Enable hash randomization (equivalent to `python -R`)
# PYTHONDONTWRITEBYTECODE: Do not write byte files to disk, since we maintain it as readonly. (equivalent to `python -B`)

# Default port
EXPOSE 5000

# Add a user with an explicit UID/GID and create necessary directories
# RUN set -eux; \
#     addgroup -g 1000 flask; \
#     adduser -u 1000 -G flask flask -D; \
#     mkdir -p "$FLASK_DATA_DIR"; \
#     chown flask:flask "$FLASK_DATA_DIR"
# USER flask

# VOLUME $FLASK_DATA_DIR

CMD ["python3", "/home/flask/main.py"]