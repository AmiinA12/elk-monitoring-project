# Installation Guide - ELK Monitoring Platform

Complete installation and deployment guide for the E-Commerce Log Monitoring Platform.

## Prerequisites

### Required Software
- **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
  - Version: 20.10 or higher
  - Download: https://www.docker.com/products/docker-desktop
- **Git** (for version control)
  - Download: https://git-scm.com/downloads
- **Python 3.9+** (for running data generation scripts locally)
  - Download: https://www.python.org/downloads/

### System Requirements
- **RAM**: Minimum 8GB (16GB recommended)
- **Disk Space**: Minimum 10GB free
- **CPU**: 2+ cores recommended
- **OS**: Windows 10/11, macOS 10.14+, or Linux

---

## Quick Start (5 Minutes)

```powershell
# 1. Clone or navigate to project
cd C:\Users\AminA\Desktop\mini_projet_log\elk-monitoring-project

# 2. Copy environment file
Copy-Item .env.example .env

# 3. Start all services
docker-compose up -d

# 4. Wait 2-3 minutes for services to initialize

# 5. Open the application
start http://localhost:8000
```

---

## Detailed Installation Steps

### Step 1: Verify Docker Installation

```powershell
# Check Docker version
docker --version
docker-compose --version

# Verify Docker is running
docker info
```

Expected output:
```
Docker version 24.x.x
Docker Compose version v2.x.x
```

### Step 2: Configure Environment Variables

The `.env` file contains all configuration settings. Key variables:

```bash
# Elasticsearch Configuration
ELASTICSEARCH_HOST=elasticsearch
ELASTICSEARCH_PORT=9200

# MongoDB Configuration
MONGO_USERNAME=admin
MONGO_PASSWORD=admin123
MONGO_DATABASE=elk_metadata

# Application Settings
FLASK_ENV=development
MAX_UPLOAD_SIZE=104857600  # 100MB
```

**⚠️ Security Note**: Change passwords in production environments!

### Step 3: Start the Infrastructure

```powershell
# Navigate to project directory
cd elk-monitoring-project

# Pull latest Docker images (first time only)
docker-compose pull

# Start all services in detached mode
docker-compose up -d

# View logs (optional)
docker-compose logs -f
```

### Step 4: Verify Services are Running

```powershell
# Check container status
docker-compose ps
```

All services should show status: `Up` or `Up (healthy)`

Expected services:
- `elk_elasticsearch` - Port 9200
- `elk_logstash` - Ports 5044, 5000, 9600
- `elk_kibana` - Port 5601
- `elk_mongodb` - Port 27017
- `elk_redis` - Port 6379
- `elk_webapp` - Port 8000

### Step 5: Wait for Services to Initialize

Elasticsearch and Kibana take 2-3 minutes to fully start:

```powershell
# Test Elasticsearch
Invoke-WebRequest http://localhost:9200

# Test Kibana (may take longer)
Invoke-WebRequest http://localhost:5601

# Test Web Application
Invoke-WebRequest http://localhost:8000/health
```

### Step 6: Generate Test Data

```powershell
# Install Python dependencies (if running locally)
pip install faker pandas

# Generate 100 sample e-commerce logs
python scripts/generate_test_data.py --count 100

# Check generated files
dir data\test
```

### Step 7: Upload Data to Logstash

```powershell
# Copy test data to uploads folder (watched by Logstash)
Copy-Item "data\test\*.csv" "data\uploads\" -Force
Copy-Item "data\test\*.json" "data\uploads\" -Force
```

Logstash will automatically:
1. Detect new files in `data/uploads/`
2. Parse CSV/JSON content
3. Index data into Elasticsearch

Wait ~30 seconds for processing.

### Step 8: Verify Data in Elasticsearch

```powershell
# Check document count
Invoke-RestMethod http://localhost:9200/logs-*/_count
```

Expected output:
```json
{
  "count": 100,
  "_shards": {...}
}
```

### Step 9: Access the Applications

Open your browser and navigate to:

- **Web Application**: http://localhost:8000
  - Dashboard, Upload, Search interfaces
- **Kibana**: http://localhost:5601
  - Data exploration and visualization
- **Elasticsearch API**: http://localhost:9200
  - Direct API access

---

## Post-Installation Setup

### Configure Kibana

Follow the [KIBANA_SETUP.md](./KIBANA_SETUP.md) guide to:
1. Create index patterns
2. Build visualizations
3. Create dashboards

### First-Time Kibana Access

1. Open http://localhost:5601
2. Click "Explore on my own" (skip tutorial)
3. Go to **Stack Management** → **Index Patterns**
4. Create pattern: `logs-*` with time field `@timestamp`

---

## Useful Docker Commands

### Viewing Logs

```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f webapp
docker-compose logs -f elasticsearch
docker-compose logs -f logstash
```

### Restart Services

```powershell
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart webapp
```

### Stop Services

```powershell
# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ DELETES DATA)
docker-compose down -v
```

### Rebuild After Code Changes

```powershell
# Rebuild webapp container
docker-compose build webapp

# Restart with new image
docker-compose up -d webapp
```

### Access Container Shell

```powershell
# Access webapp container
docker exec -it elk_webapp /bin/bash

# Access Elasticsearch container
docker exec -it elk_elasticsearch /bin/bash
```

### Check Resource Usage

```powershell
# Monitor container resources
docker stats
```

---

## Troubleshooting

### Issue: Elasticsearch won't start

**Symptoms**: Container keeps restarting

**Solutions**:
1. Increase Docker memory to 4GB minimum:
   - Docker Desktop → Settings → Resources → Memory
2. Check logs:
   ```powershell
   docker-compose logs elasticsearch
   ```
3. On Linux, may need to increase `vm.max_map_count`:
   ```bash
   sudo sysctl -w vm.max_map_count=262144
   ```

### Issue: Kibana shows "Kibana server not ready"

**Solution**: Wait 2-3 minutes. Kibana needs Elasticsearch to be fully ready.

### Issue: Webapp returns 500 errors

**Possible causes**:
1. Elasticsearch/MongoDB/Redis not ready yet
2. Check health endpoint:
   ```powershell
   Invoke-RestMethod http://localhost:8000/health
   ```
3. View webapp logs:
   ```powershell
   docker-compose logs webapp
   ```

### Issue: Logstash not processing files

**Check**:
1. Files are in `data/uploads/` folder
2. Files have correct extension (.csv or .json)
3. View Logstash logs:
   ```powershell
   docker-compose logs logstash
   ```

### Issue: Port already in use

**Error**: `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Solution**:
1. Find process using the port:
   ```powershell
   netstat -ano | findstr :8000
   ```
2. Stop the process or change port in `docker-compose.yml`

### Issue: Docker Desktop not starting

**Solutions**:
1. Restart Docker Desktop
2. Check if Hyper-V/WSL2 is enabled (Windows)
3. Reinstall Docker Desktop

---

## Updating the Application

```powershell
# Pull latest changes (if using Git)
git pull

# Rebuild containers
docker-compose down
docker-compose build
docker-compose up -d
```

---

## Data Persistence

Data is persisted in Docker volumes:
- `elasticsearch_data` - All indexed logs
- `mongodb_data` - Upload metadata
- `redis_data` - Cache data

To back up data:
```powershell
# List volumes
docker volume ls

# Create backup
docker run --rm -v elasticsearch_data:/data -v ${PWD}:/backup alpine tar czf /backup/es-backup.tar.gz -C /data .
```

---

## Production Deployment Checklist

Before deploying to production:

- [ ] Change all default passwords in `.env`
- [ ] Set `FLASK_ENV=production`
- [ ] Configure proper SSL/TLS certificates
- [ ] Set up firewall rules
- [ ] Enable Elasticsearch security (X-Pack)
- [ ] Configure backup schedules
- [ ] Set resource limits in `docker-compose.yml`
- [ ] Enable monitoring and alerting
- [ ] Review and harden Docker container security

---

## Next Steps

1. ✅ Follow [KIBANA_SETUP.md](./KIBANA_SETUP.md) for visualization setup
2. ✅ Explore the web application at http://localhost:8000
3. ✅ Generate more test data and experiment
4. ✅ Customize for your specific use case

---

**Need Help?**
- Check Docker logs: `docker-compose logs -f`
- Verify health: http://localhost:8000/health
- Elasticsearch API: http://localhost:9200/_cluster/health

**✅ Installation Complete!** Your ELK Monitoring Platform is ready to use.
