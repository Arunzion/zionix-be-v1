# Docker TLS Handshake Timeout Troubleshooting Guide

This guide helps resolve the TLS handshake timeout error when building Docker images or pulling from registries.

## Error Description

```
failed to copy: httpReadSeeker: failed open: failed to do request: Get "https://production.cloudflare.docker.com/registry-v2/docker/registry/v2/blobs/sha256/...": net/http: TLS handshake timeout
```

## Quick Fixes

### 1. Use the Retry Scripts

**For Windows:**
```cmd
scripts\docker-build-with-retry.bat
```

**For Linux/Mac:**
```bash
chmod +x scripts/docker-build-with-retry.sh
./scripts/docker-build-with-retry.sh
```

### 2. Manual Docker Commands

If the scripts don't work, try these manual steps:

```bash
# Clean Docker system
docker system prune -f --volumes

# Pull images individually with timeout
docker pull --timeout=300 postgres:13
docker pull --timeout=300 kong:2.7
docker pull --timeout=300 confluentinc/cp-zookeeper:7.0.1
docker pull --timeout=300 confluentinc/cp-kafka:7.0.1

# Build services one by one
docker-compose build --no-cache admin-service
docker-compose build --no-cache auth-service
```

## Advanced Solutions

### 1. Configure Docker Daemon

Create or edit `~/.docker/daemon.json` (Linux/Mac) or `%USERPROFILE%\.docker\daemon.json` (Windows):

```json
{
  "registry-mirrors": [
    "https://mirror.gcr.io",
    "https://registry-1.docker.io"
  ],
  "insecure-registries": [],
  "dns": ["8.8.8.8", "8.8.4.4"],
  "max-concurrent-downloads": 3,
  "max-concurrent-uploads": 3,
  "default-network-opts": {
    "bridge": {
      "com.docker.network.driver.mtu": "1450"
    }
  }
}
```

After creating this file, restart Docker Desktop.

### 2. Network Configuration

#### Windows
```cmd
# Reset network stack
netsh winsock reset
netsh int ip reset
ipconfig /flushdns
```

#### Linux/Mac
```bash
# Flush DNS cache
sudo systemctl flush-dns  # Linux
sudo dscacheutil -flushcache  # Mac

# Check MTU settings
ip link show
```

### 3. Firewall and Proxy Settings

If you're behind a corporate firewall:

1. **Configure Docker to use proxy:**
   
   Create `~/.docker/config.json`:
   ```json
   {
     "proxies": {
       "default": {
         "httpProxy": "http://proxy.company.com:8080",
         "httpsProxy": "http://proxy.company.com:8080",
         "noProxy": "localhost,127.0.0.1"
       }
     }
   }
   ```

2. **Add Docker registry domains to firewall whitelist:**
   - `production.cloudflare.docker.com`
   - `registry-1.docker.io`
   - `auth.docker.io`
   - `index.docker.io`

### 4. Alternative Base Images

If the issue persists, try using alternative base images in your Dockerfiles:

```dockerfile
# Instead of python:3.9-slim, try:
FROM python:3.9-alpine
# or
FROM ubuntu:20.04
RUN apt-get update && apt-get install -y python3 python3-pip
```

### 5. Docker Desktop Settings

In Docker Desktop:
1. Go to Settings → Resources → Advanced
2. Increase Memory to at least 4GB
3. Increase CPU to at least 2 cores
4. Go to Settings → Docker Engine
5. Add the daemon.json configuration above

## Environment-Specific Solutions

### Windows 10/11
```cmd
# Restart Docker Desktop
taskkill /f /im "Docker Desktop.exe"
"C:\Program Files\Docker\Docker\Docker Desktop.exe"

# Or use PowerShell
Restart-Service docker
```

### WSL2 (Windows Subsystem for Linux)
```bash
# In WSL2 terminal
sudo service docker restart

# Check WSL2 memory limits in .wslconfig
echo "[wsl2]
memory=4GB
processors=2" > ~/.wslconfig
```

### macOS
```bash
# Restart Docker Desktop
osascript -e 'quit app "Docker Desktop"'
open -a "Docker Desktop"
```

## Verification Steps

After applying fixes:

1. **Test Docker connectivity:**
   ```bash
   docker run hello-world
   ```

2. **Test registry access:**
   ```bash
   docker pull alpine:latest
   ```

3. **Build your services:**
   ```bash
   docker-compose build --no-cache
   ```

4. **Start the application:**
   ```bash
   docker-compose up -d
   ```

## Prevention Tips

1. **Regular maintenance:**
   ```bash
   # Weekly cleanup
   docker system prune -f
   docker volume prune -f
   ```

2. **Monitor Docker resources:**
   ```bash
   docker system df
   docker stats
   ```

3. **Keep Docker updated:**
   - Update Docker Desktop regularly
   - Update base images in Dockerfiles

## Still Having Issues?

If none of these solutions work:

1. Check Docker Desktop logs:
   - Windows: `%APPDATA%\Docker\log.txt`
   - Mac: `~/Library/Containers/com.docker.docker/Data/log/`

2. Try building on a different network (mobile hotspot)

3. Contact your network administrator if in a corporate environment

4. Consider using Docker alternatives like Podman or containerd

## Additional Resources

- [Docker Official Troubleshooting](https://docs.docker.com/desktop/troubleshoot/)
- [Docker Network Troubleshooting](https://docs.docker.com/network/troubleshooting/)
- [Docker Registry Configuration](https://docs.docker.com/registry/configuration/)