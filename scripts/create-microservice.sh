#!/bin/bash

# Script to create a new microservice from the template
# Usage: ./create-microservice.sh <service-name>

set -e

if [ -z "$1" ]; then
    echo "Error: Service name is required"
    echo "Usage: ./create-microservice.sh <service-name>"
    exit 1
fi

SERVICE_NAME=$1
TEMPLATE_DIR="../templates/microservice-template"
TARGET_DIR="../${SERVICE_NAME}"

echo "Creating new microservice: ${SERVICE_NAME}"

# Check if service already exists
if [ -d "$TARGET_DIR" ]; then
    echo "Error: Service directory already exists: ${TARGET_DIR}"
    exit 1
fi

# Copy template to new directory
cp -r "$TEMPLATE_DIR" "$TARGET_DIR"

# Replace placeholder in files
find "$TARGET_DIR" -type f -exec sed -i "s/SERVICE_NAME/${SERVICE_NAME}/g" {} \;
find "$TARGET_DIR" -type f -exec sed -i "s/Zionix Microservice/Zionix ${SERVICE_NAME^} Service/g" {} \;

# Create Kubernetes gateway configuration
cat > "../gateway/kong/${SERVICE_NAME}.yaml" << EOF
apiVersion: configuration.konghq.com/v1
kind: KongPlugin
metadata:
  name: ${SERVICE_NAME}-cors
config:
  origins:
  - '*'
  methods:
  - GET
  - POST
  - PUT
  - DELETE
  - OPTIONS
  - PATCH
  headers:
  - Accept
  - Accept-Version
  - Content-Length
  - Content-MD5
  - Content-Type
  - Date
  - X-Auth-Token
  - Authorization
  exposed_headers:
  - X-Auth-Token
  credentials: true
  max_age: 3600
---
apiVersion: configuration.konghq.com/v1
kind: KongIngress
metadata:
  name: ${SERVICE_NAME}-ingress
route:
  protocols:
  - http
  - https
  strip_path: true
---
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: ${SERVICE_NAME}-ingress
  annotations:
    kubernetes.io/ingress.class: kong
    konghq.com/plugins: ${SERVICE_NAME}-cors
    konghq.com/override: ${SERVICE_NAME}-ingress
spec:
  rules:
  - http:
      paths:
      - path: /api/${SERVICE_NAME}
        backend:
          serviceName: ${SERVICE_NAME}
          servicePort: 8000
EOF

# Update CI/CD pipeline to include the new service
echo "Adding ${SERVICE_NAME} to CI/CD pipeline..."

# Create database migration directory
mkdir -p "$TARGET_DIR/alembic/versions"
touch "$TARGET_DIR/alembic/versions/.gitkeep"

# Create requirements.txt with common dependencies
cat > "$TARGET_DIR/requirements.txt" << EOF
fastapi>=0.95.0,<0.96.0
pydantic>=2.0.0,<3.0.0
pydantic-settings>=2.0.0,<3.0.0
uvicorn>=0.22.0,<0.23.0
sqlalchemy>=2.0.0,<3.0.0
alembic>=1.11.0,<1.12.0
psycopg2-binary>=2.9.6,<2.10.0
python-jose>=3.3.0,<3.4.0
passlib>=1.7.4,<1.8.0
python-multipart>=0.0.6,<0.1.0
email-validator>=2.0.0,<3.0.0
requests>=2.28.0,<2.29.0
tenacity>=8.2.2,<8.3.0
aiokafka>=0.8.0,<0.9.0
redis>=4.5.5,<4.6.0
prometheus-fastapi-instrumentator>=6.0.0,<6.1.0
opentelemetry-api>=1.18.0,<1.19.0
opentelemetry-sdk>=1.18.0,<1.19.0
opentelemetry-instrumentation-fastapi>=0.39b0,<0.40.0
loguru>=0.7.0,<0.8.0
EOF

# Create alembic.ini file
cat > "$TARGET_DIR/alembic.ini" << EOF
[alembic]
script_location = alembic
prepend_sys_path = .

sqlalchemy.url = postgresql://postgres:postgres@localhost/${SERVICE_NAME}_db

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
EOF

# Create directory structure
mkdir -p "$TARGET_DIR/app/api/routes"
mkdir -p "$TARGET_DIR/app/core"
mkdir -p "$TARGET_DIR/app/crud"
mkdir -p "$TARGET_DIR/app/db"
mkdir -p "$TARGET_DIR/app/models"
mkdir -p "$TARGET_DIR/app/schemas"
mkdir -p "$TARGET_DIR/app/events"
mkdir -p "$TARGET_DIR/tests"

# Create __init__.py files
touch "$TARGET_DIR/app/__init__.py"
touch "$TARGET_DIR/app/api/__init__.py"
touch "$TARGET_DIR/app/api/routes/__init__.py"
touch "$TARGET_DIR/app/core/__init__.py"
touch "$TARGET_DIR/app/crud/__init__.py"
touch "$TARGET_DIR/app/db/__init__.py"
touch "$TARGET_DIR/app/models/__init__.py"
touch "$TARGET_DIR/app/schemas/__init__.py"
touch "$TARGET_DIR/app/events/__init__.py"
touch "$TARGET_DIR/tests/__init__.py"

# Create basic API router
cat > "$TARGET_DIR/app/api/routes/__init__.py" << EOF
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "Welcome to ${SERVICE_NAME} service"}
EOF

# Create database session file
cat > "$TARGET_DIR/app/db/session.py" << EOF
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
EOF

# Create database base file
cat > "$TARGET_DIR/app/db/base.py" << EOF
from app.db.session import Base

# Import all models here so Alembic can discover them
# from app.models.item import Item
# from app.models.user import User
EOF

# Create Kubernetes HPA configuration for automatic scaling
cat > "$TARGET_DIR/k8s/base/hpa.yaml" << EOF
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ${SERVICE_NAME}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ${SERVICE_NAME}
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
EOF

# Create observability configuration
cat > "$TARGET_DIR/app/core/observability.py" << EOF
from prometheus_fastapi_instrumentator import Instrumentator
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from loguru import logger
import json

def setup_observability(app):
    # Set up Prometheus metrics
    Instrumentator().instrument(app).expose(app)
    
    # Set up OpenTelemetry tracing
    FastAPIInstrumentor.instrument_app(app)
    
    # Configure structured JSON logging
    logger.configure(
        handlers=[
            {
                "sink": lambda msg: print(json.dumps(msg)),
                "serialize": True,
            },
        ]
    )
    
    return app
EOF

# Update main.py to include observability setup
cat > "$TARGET_DIR/app/main.py" << EOF
from fastapi import FastAPI
from app.api.routes import router
from app.core.config import settings
from app.core.observability import setup_observability
from app.db.session import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# Set up observability (metrics, tracing, logging)
app = setup_observability(app)

# Include API router
app.include_router(router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/readiness")
async def readiness_check():
    return {"status": "ready"}
EOF

# Create service mesh configuration
mkdir -p "$TARGET_DIR/k8s/base/istio"
cat > "$TARGET_DIR/k8s/base/istio/virtual-service.yaml" << EOF
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: ${SERVICE_NAME}
spec:
  hosts:
  - ${SERVICE_NAME}
  http:
  - route:
    - destination:
        host: ${SERVICE_NAME}
    retries:
      attempts: 3
      perTryTimeout: 2s
      retryOn: gateway-error,connect-failure,refused-stream
    timeout: 10s
EOF

cat > "$TARGET_DIR/k8s/base/istio/destination-rule.yaml" << EOF
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: ${SERVICE_NAME}
spec:
  host: ${SERVICE_NAME}
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 100
        maxRequestsPerConnection: 10
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 30s
EOF

echo "Microservice ${SERVICE_NAME} created successfully!"
echo "Next steps:"
echo "1. Implement your service-specific logic"
echo "2. Update the CI/CD pipeline in .github/workflows/ci-cd.yaml"
echo "3. Deploy your service with ../scripts/deploy.sh"
echo "4. Review the architecture documentation in ../docs/ARCHITECTURE.md"
echo "5. Configure service-specific scaling in k8s/base/hpa.yaml"