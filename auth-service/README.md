# ZCare Auth Service

The Auth Service is a microservice component of the ZCare Platform responsible for user authentication and authorization. It provides APIs for user management, authentication, and token verification.

## Features

- User management (CRUD operations)
- JWT-based authentication
- Token verification
- Role-based access control
- RESTful API with FastAPI

## Architecture

The Auth Service follows a clean architecture pattern with the following components:

- **API Layer**: FastAPI routes and endpoints
- **Service Layer**: Business logic and use cases
- **Data Layer**: Database models and repositories

## Setup and Installation

### Prerequisites

- Python 3.9+
- PostgreSQL

### Local Development

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Set up environment variables (or create a .env file)
5. Run the application:
   ```
   uvicorn app.main:app --reload --port 8001
   ```

### Docker

Build and run using Docker:

```
docker build -t zcare/auth-service .
docker run -p 8001:8001 zcare/auth-service
```

### Kubernetes

Deploy to Kubernetes:

```
kubectl apply -f k8s/base/auth-service.yaml
```

## API Documentation

When the service is running, access the Swagger UI documentation at:

```
http://localhost:8001/docs
```

## Configuration

Configuration is managed through environment variables and the `app/core/config.py` file.

Key configuration options:

- Database connection
- JWT settings (secret key, token expiration)
- CORS settings

## Gateway Integration

The Auth Service is exposed through the Kong API Gateway with the following configuration:

- Route: `/api/v1/auth`
- Authentication: None (for login endpoints) / JWT (for protected endpoints)
- Rate limiting: 60 requests per minute
- CORS enabled
- Prometheus metrics