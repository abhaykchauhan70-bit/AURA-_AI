# Database

SQLAlchemy models define users, conversations, messages, tasks, uploaded documents, and user memories. Foreign keys cascade deletion for user-owned records. PostgreSQL is the Docker default; SQLite is accepted for local development. The starter creates tables at application startup. Before production or collaborative development, replace this with Alembic migrations and add task dependency, tool execution, approval, and evaluation tables as their workflows are implemented.
