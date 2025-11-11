# Techno‑Commercial Proposal Platform (MySQL)

## Quick Start (Local)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# ensure MySQL is running and the DB/user exist (see below)
streamlit run app.py
```

### MySQL Setup
Create a database and user (example):
```sql
CREATE DATABASE proposal_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'proposal_user'@'%' IDENTIFIED BY 'proposal_pass';
GRANT ALL PRIVILEGES ON proposal_db.* TO 'proposal_user'@'%';
FLUSH PRIVILEGES;
```

### Role Access
- **BESS** → BESS Template only
- **EPC** → EPC Template only
- **ADMIN** → both

### Backups
- Local ZIPs in `backups/` named `{reference}_{timestamp}.zip` containing artifacts and metadata.

### Docker Compose (MySQL + App)
Create `docker-compose.yml` and run `docker compose up -d`.

### CI/CD & MLOps Notes
- Build container with Dockerfile; deploy behind reverse proxy.
- Use env vars for `DATABASE_URL`.
- Add DB migrations later with Alembic when the schema evolves.
