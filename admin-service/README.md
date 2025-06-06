# ZCare Admin Service

The Admin Service is a microservice component of the ZCare Platform responsible for managing domains and applications. It provides APIs for domain and application management and processes events through Kafka.

## Features

- Domain management (CRUD operations)
- Application management (CRUD operations)
- Event-driven architecture using Kafka
- JWT-based authentication
- RESTful API with FastAPI

## Architecture

The Admin Service follows a clean architecture pattern with the following components:

- **API Layer**: FastAPI routes and endpoints
- **Service Layer**: Business logic and use cases
- **Data Layer**: Database models and repositories
- **Event Layer**: Kafka producers and consumers

## Event Processing

The service processes events through Kafka:

- **Domain Events**: Events related to domain creation, updates, and deletion
- **Application Events**: Events related to application creation, updates, and deletion

## Setup and Installation

### Prerequisites

- Python 3.9+
- PostgreSQL
- Kafka

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
   uvicorn app.main:app --reload
   ```

### Docker

Build and run using Docker:

```
docker build -t zcare/admin-service .
docker run -p 8000:8000 zcare/admin-service
```

### Kubernetes

Deploy to Kubernetes:

```
kubectl apply -f k8s/base/admin-service.yaml
```

## API Documentation

When the service is running, access the Swagger UI documentation at:

```
http://localhost:8000/docs
```

## Event Consumers

The service includes two Kafka consumers:

1. **Domain Events Consumer**: Processes domain-related events
2. **Application Events Consumer**: Processes application-related events

Both consumers are automatically started when the service starts.

## Configuration

Configuration is managed through environment variables and the `app/core/config.py` file.

Key configuration options:

- Database connection
- Kafka settings
- JWT authentication
- CORS settings

## Gateway Integration

The Admin Service is exposed through the Kong API Gateway with the following configuration:

- Route: `/api/v1/admin`
- Authentication: JWT
- Rate limiting: 60 requests per minute
- CORS enabled
- Prometheus metrics