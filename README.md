# Upkeeper

Below are general setup instructions that you may remove or keep and adapt for your project.

* * *

## Project Docs

For how to install uv and Python, see [installation.md](installation.md).

For development workflows, see [development.md](development.md).

For instructions on publishing to PyPI, see [publishing.md](publishing.md).

## Database Migrations

This project uses Alembic for database schema management. Migrations are automatically applied on application startup.

### Creating Migrations

When you modify database models, create a new migration:

```bash
uv run alembic revision --autogenerate -m "Description of changes"
```

### Applying Migrations

Apply pending migrations manually:

```bash
uv run alembic upgrade head
```

### Other Useful Commands

- Check current migration status: `uv run alembic current`
- View migration history: `uv run alembic history`
- Downgrade to previous migration: `uv run alembic downgrade -1`

* * *
