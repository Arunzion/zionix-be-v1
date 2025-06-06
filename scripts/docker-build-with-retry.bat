@echo off
setlocal enabledelayedexpansion

REM Docker build script with retry logic for TLS timeout issues (Windows)
REM Usage: scripts\docker-build-with-retry.bat [service-name]

set SERVICE_NAME=%1
if "%SERVICE_NAME%"=="" set SERVICE_NAME=all
set MAX_RETRIES=3
set RETRY_DELAY=10

echo [INFO] Starting Docker build process with retry logic...

REM Set Docker buildkit for better performance and error handling
set DOCKER_BUILDKIT=1
set COMPOSE_DOCKER_CLI_BUILD=1

REM Function to pull images with retry logic
echo [INFO] Pulling required base images...
call :pull_image_with_retry "postgres:13"
if errorlevel 1 goto :error

call :pull_image_with_retry "kong:2.7"
if errorlevel 1 goto :error

call :pull_image_with_retry "confluentinc/cp-zookeeper:7.0.1"
if errorlevel 1 goto :error

call :pull_image_with_retry "confluentinc/cp-kafka:7.0.1"
if errorlevel 1 goto :error

call :pull_image_with_retry "prom/prometheus:v2.30.3"
if errorlevel 1 goto :error

call :pull_image_with_retry "grafana/grafana:8.2.2"
if errorlevel 1 goto :error

REM Build services
if "%SERVICE_NAME%"=="all" (
    echo [INFO] Building all services...
    
    call :build_service_with_retry "admin-service"
    if errorlevel 1 goto :error
    
    call :build_service_with_retry "auth-service"
    if errorlevel 1 goto :error
    
    echo [INFO] All services built successfully!
) else (
    call :build_service_with_retry "%SERVICE_NAME%"
    if errorlevel 1 goto :error
)

echo [INFO] Docker build process completed successfully!
goto :end

:pull_image_with_retry
set IMAGE=%~1
set ATTEMPT=1

:pull_retry_loop
echo [INFO] Pulling %IMAGE% (attempt %ATTEMPT%/%MAX_RETRIES%)...

docker pull %IMAGE%
if %errorlevel%==0 (
    echo [INFO] Successfully pulled %IMAGE%
    goto :eof
)

echo [WARN] Pull failed for %IMAGE% (attempt %ATTEMPT%/%MAX_RETRIES%)
if %ATTEMPT% lss %MAX_RETRIES% (
    echo [INFO] Waiting %RETRY_DELAY% seconds before retry...
    timeout /t %RETRY_DELAY% /nobreak >nul
    set /a ATTEMPT+=1
    goto :pull_retry_loop
)

echo [ERROR] Failed to pull %IMAGE% after %MAX_RETRIES% attempts
exit /b 1

:build_service_with_retry
set SERVICE=%~1
set ATTEMPT=1

:build_retry_loop
echo [INFO] Building %SERVICE% (attempt %ATTEMPT%/%MAX_RETRIES%)...

docker-compose build --no-cache --pull %SERVICE%
if %errorlevel%==0 (
    echo [INFO] Successfully built %SERVICE%
    goto :eof
)

echo [WARN] Build failed for %SERVICE% (attempt %ATTEMPT%/%MAX_RETRIES%)
if %ATTEMPT% lss %MAX_RETRIES% (
    echo [INFO] Waiting %RETRY_DELAY% seconds before retry...
    timeout /t %RETRY_DELAY% /nobreak >nul
    
    REM Clean up any partial builds
    docker system prune -f --volumes
    
    set /a ATTEMPT+=1
    goto :build_retry_loop
)

echo [ERROR] Failed to build %SERVICE% after %MAX_RETRIES% attempts
exit /b 1

:error
echo [ERROR] Docker build process failed!
exit /b 1

:end
endlocal