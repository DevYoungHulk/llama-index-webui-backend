# llama-index-webui-backend

apt install libldap2-dev libsasl2-dev python3-openssl
pip install -r requirements.txt

# Generate a secret
python generate_secret.py

# Run
docker compose up -d  # start database
python main.py # start backend

celery -A app.celery_tasks.celery_app worker # start celery tasks worker
celery -A app.celery_tasks.celery_app flower # start flower for monitor celery tasks