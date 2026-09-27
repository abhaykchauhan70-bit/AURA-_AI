# Deployment

Local Docker deployment: copy `.env.example` to `.env`, set a strong `JWT_SECRET` and database password, then run `docker compose up --build`. Frontend: port 3000. API: port 8000. PostgreSQL data and uploaded files use named persistent volumes. Do not expose this development compose setup publicly without TLS, secret management, backups, migrations, and production server configuration.
