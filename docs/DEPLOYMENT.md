# Zionix Microservice Deployment Guide

This guide provides detailed instructions for deploying and managing microservices in the Zionix platform, designed to support deployments at massive scale.

## Prerequisites

- Kubernetes cluster access with appropriate permissions
- `kubectl` configured for your target environment
- Docker for local development and testing

## Deployment Environments

The Zionix platform supports three deployment environments:

| Environment | Purpose                   | Scaling Configuration                   |
| ----------- | ------------------------- | --------------------------------------- |
| `dev`       | Development and testing   | Minimal resources, fast startup         |
| `staging`   | Pre-production validation | Production-like with reduced replicas   |
| `prod`      | Production environment    | Full HA configuration with auto-scaling |

## Deployment Methods

### Automated CI/CD Pipeline

The recommended way to deploy services is through the automated CI/CD pipeline:

1. Push changes to your service's repository
2. The pipeline automatically:
   - Builds and tests the service
   - Creates a container image
   - Deploys to the appropriate environment based on the branch

### Manual Deployment

For manual deployments, use the deployment script:

```bash
# Deploy a specific service to dev environment
./scripts/deploy.sh dev

# Deploy with increased parallelism for faster deployment
./scripts/deploy.sh dev 10

# Deploy to production
./scripts/deploy.sh prod
```

## Creating New Microservices

Use the microservice creation script to generate a new service with all the necessary configuration:

```bash
./scripts/create-microservice.sh my-service-name
```

This creates a new service with:

- Standardized directory structure
- API Gateway configuration
- Database migration setup
- Kubernetes manifests
- Service mesh integration

## Scaling Configuration

### Horizontal Pod Autoscaling

Each service includes HPA configuration in `k8s/base/hpa.yaml`. Customize the scaling parameters:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: my-service
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-service
  minReplicas: 3
  maxReplicas: 20
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
```

### Resource Allocation

Set appropriate resource requests and limits in `k8s/base/deployment.yaml`:

```yaml
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

## Monitoring Deployments

### Deployment Status

Check deployment status:

```bash
# Get all deployments in an environment
kubectl -n zionix-dev get deployments

# Check specific deployment details
kubectl -n zionix-dev describe deployment my-service

# View deployment history
kubectl -n zionix-dev rollout history deployment my-service
```

### Logs and Metrics

Access service logs:

```bash
# Get logs for a service
kubectl -n zionix-dev logs -l app=my-service --tail=100

# Follow logs in real-time
kubectl -n zionix-dev logs -l app=my-service -f
```

Access the monitoring dashboards:

- Prometheus: `http://prometheus.zionix.internal`
- Grafana: `http://grafana.zionix.internal`
- Jaeger: `http://jaeger.zionix.internal`

## Rollback Procedures

If a deployment causes issues, roll back to the previous version:

```bash
# Roll back to the previous version
kubectl -n zionix-dev rollout undo deployment my-service

# Roll back to a specific revision
kubectl -n zionix-dev rollout undo deployment my-service --to-revision=2
```

## Advanced Deployment Strategies

### Canary Deployments

For critical services, use canary deployments to gradually roll out changes:

1. Deploy a small percentage of traffic to the new version
2. Monitor for errors and performance issues
3. Gradually increase traffic to the new version
4. Complete the rollout when confident

This is configured through the service mesh:

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: my-service
spec:
  hosts:
    - my-service
  http:
    - route:
        - destination:
            host: my-service
            subset: v1
          weight: 90
        - destination:
            host: my-service
            subset: v2
          weight: 10
```

### Blue/Green Deployments

For zero-downtime deployments:

1. Deploy the new version alongside the existing version
2. Verify the new version is working correctly
3. Switch traffic from the old version to the new version
4. Remove the old version after confirming success

## Deployment at Scale

### Batch Deployments

When deploying multiple services, use batch deployments to manage the process:

```bash
# Deploy infrastructure services first
./scripts/deploy.sh dev infrastructure

# Deploy core services
./scripts/deploy.sh dev core

# Deploy remaining services with high parallelism
./scripts/deploy.sh dev services 15
```

### Deployment Prioritization

Services are deployed in the following order:

1. Infrastructure services (databases, message brokers, etc.)
2. Core services (authentication, user management, etc.)
3. Business services (domain-specific functionality)
4. Edge services (API gateways, CDN configurations, etc.)

## Troubleshooting

### Common Deployment Issues

| Issue               | Possible Causes                              | Resolution                                             |
| ------------------- | -------------------------------------------- | ------------------------------------------------------ |
| Pod crash looping   | Resource limits too low, application errors  | Check logs, increase resources, fix application issues |
| Service unavailable | Network policies, service mesh configuration | Verify network policies, check service mesh routes     |
| Slow deployment     | Resource contention, large images            | Optimize image size, adjust resource requests          |

### Deployment Debugging

For detailed debugging:

```bash
# Get detailed events for a namespace
kubectl -n zionix-dev get events --sort-by=.metadata.creationTimestamp

# Describe a pod to see its status and events
kubectl -n zionix-dev describe pod my-service-pod-name

# Check service mesh configuration
istioctl analyze -n zionix-dev
```

## Deployment Best Practices

1. **Immutable Infrastructure**: Never modify running containers; always deploy new versions
2. **Infrastructure as Code**: Keep all deployment configurations in version control
3. **Automated Testing**: Run comprehensive tests before deployment
4. **Gradual Rollouts**: Use progressive delivery for critical services
5. **Monitoring and Alerting**: Set up alerts for deployment failures and service degradation
6. **Documentation**: Keep deployment procedures and runbooks up to date
7. **Deployment Windows**: Establish regular deployment windows for non-emergency changes
8. **Rollback Plan**: Always have a clear rollback plan before deploying

## Further Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Istio Documentation](https://istio.io/latest/docs/)
- [Kong API Gateway Documentation](https://docs.konghq.com/)
- Internal architecture documentation in the `docs` directory
