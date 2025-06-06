# Database Migrations

This directory contains database migrations for the Admin Service using Alembic.

## Migration Structure

- `env.py`: Configuration for the Alembic environment
- `script.py.mako`: Template for generating new migration scripts
- `versions/`: Directory containing individual migration scripts

## Available Migrations

- `001_create_domains_table.py`: Initial migration that creates the domains table
- `002_create_applications_table.py`: Migration that creates the applications table with foreign key to domains

## Running Migrations

To apply migrations to your database:

```bash
# Navigate to the admin-service root directory
cd /path/to/zionix-be-v1/admin-service

# Run migrations
alembic upgrade head
```

## Creating New Migrations

To create a new migration:

```bash
# Generate a migration script
alembic revision --autogenerate -m "description of changes"

# Review the generated script in versions/ directory
# Apply the migration
alembic upgrade head
```

## Rolling Back Migrations

To roll back to a previous migration:

```bash
# Roll back one migration
alembic downgrade -1

# Roll back to a specific migration
alembic downgrade <migration_id>

# Roll back all migrations
alembic downgrade base
```