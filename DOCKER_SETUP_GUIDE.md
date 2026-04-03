# Docker Setup & Deployment Guide

## ✅ Docker Configuration Complete!

Your Tic-Tac-Toe with AI application is now fully containerized and ready for deployment.

## Quick Start (Development)

### Start the Application

```bash
docker-compose up -d
```

### Access the Application

```
http://localhost:8000
```

### View Logs

```bash
docker-compose logs -f web
```

### Stop the Application

```bash
docker-compose down
```

## What Was Created

### 1. **Dockerfile**
- Python 3.9-slim base image
- Installs all dependencies from requirements.txt
- Runs Daphne ASGI server on port 8000
- Production-ready configuration

### 2. **docker-compose.yml**
- **Web Service**: Django + Daphne ASGI server
- **Redis Service**: Message broker for WebSocket communication
- Health checks included
- Automatic volume mounting for development
- Network isolation for security

### 3. **.dockerignore**
- Optimizes Docker build by excluding unnecessary files
- Reduces image size and build time

### 4. **.env.example**
- Template for environment variables
- Copy to `.env` and configure for your environment

### 5. **Settings Configuration**
- Updated `tic_tac_toe/settings.py` to support Redis from Docker
- Environment variable support for Redis host/port

## Services Running

```
┌─────────────────────────────────────────────┐
│  Tic-Tac-Toe Docker Setup                  │
├─────────────────────────────────────────────┤
│  Web Service (Daphne)                       │
│  ├─ Port: 8000                              │
│  ├─ Language: Python 3.9                    │
│  ├─ Framework: Django 4.2 + Channels       │
│  └─ ASGI Server: Daphne                    │
│                                             │
│  Redis Service                              │
│  ├─ Port: 6379                              │
│  ├─ Image: redis:7-alpine                  │
│  └─ Purpose: WebSocket message broker      │
│                                             │
│  Network: tictactoe-network                │
│  Volumes: redis_data, static_volume        │
└─────────────────────────────────────────────┘
```

## Useful Commands

### Database Operations
```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Access Django shell
docker-compose exec web python manage.py shell
```

### Redis Operations
```bash
# Check Redis connection
docker-compose exec redis redis-cli ping

# Monitor Redis keys
docker-compose exec redis redis-cli KEYS '*'

# Monitor Redis commands in real-time
docker-compose exec redis redis-cli MONITOR
```

### Container Management
```bash
# View running containers
docker-compose ps

# View logs with timestamps
docker-compose logs -t

# Follow logs in real-time
docker-compose logs -f

# Restart containers
docker-compose restart

# Remove all containers and volumes
docker-compose down -v
```

### Build and Cache
```bash
# Rebuild without cache
docker-compose build --no-cache

# Build only web service
docker-compose build web
```

## Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Configure in `.env`:
```env
DEBUG=True                                    # Set to False in production
SECRET_KEY=your-secret-key-here              # Change in production
ALLOWED_HOSTS=localhost,127.0.0.1,web        # Add your domains
REDIS_HOST=redis                             # Keep as 'redis' for Docker
REDIS_PORT=6379                              # Keep as 6379
GEMINI_API_KEY=your-api-key-here            # Optional: For AI
```

## Development Workflow

### 1. Make Code Changes
```bash
# Edit your Python files - changes auto-reload in Docker
vim game/consumers.py
```

### 2. View Changes
```bash
# Logs will show hot-reload
docker-compose logs -f web
```

### 3. Create New Migrations
```bash
# If you modify models
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

## Troubleshooting

### Port Already in Use
```bash
# Find and kill process using port 8000
lsof -i :8000
kill -9 <PID>

# Or change port in docker-compose.yml:
# ports:
#   - "8001:8000"
```

### Redis Connection Failed
```bash
# Check Redis status
docker-compose exec redis redis-cli ping
# Should return: PONG

# Restart Redis
docker-compose restart redis
```

### Database Issues
```bash
# Reset database (removes all data)
docker-compose down -v
docker-compose up -d

# Or manually clear
docker volume rm allfolder_redis_data
```

### Application Won't Start
```bash
# Check logs
docker-compose logs web

# Check system requirements
docker --version  # Should be 20.10+
docker-compose --version  # Should be 1.29+

# Free up system resources
docker system prune
```

## Production Deployment

### Security Checklist

```bash
# 1. Update .env with production values
DEBUG=False
SECRET_KEY=generate-a-strong-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# 2. Use strong passwords
# 3. Set up HTTPS/SSL certificates
# 4. Use environment-specific database
# 5. Enable CORS properly
# 6. Configure firewall rules
```

### Scaling with Docker

For multiple instances:

```yaml
version: '3.9'
services:
  web:
    deploy:
      replicas: 3  # Scale to 3 instances
      update_config:
        parallelism: 1
        delay: 10s
```

### Using a Reverse Proxy (Nginx)

```bash
# Add to docker-compose.yml
nginx:
  image: nginx:alpine
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf
  depends_on:
    - web
```

## Monitoring

### Check Container Health
```bash
docker-compose ps

# Output should show:
# STATUS: Up X minutes (healthy)
```

### Monitor Resource Usage
```bash
docker stats
```

### View Application Metrics
```bash
# Check request count
docker-compose logs web | grep "HTTP"

# Count WebSocket connections
docker-compose logs web | grep "WebSocket"
```

## Next Steps

1. **Customize**: Update `ALLOWED_HOSTS`, `SECRET_KEY` in production
2. **Database**: Switch to PostgreSQL for production
3. **SSL/TLS**: Configure HTTPS with Let's Encrypt
4. **Monitoring**: Set up logging and monitoring (e.g., ELK stack)
5. **CI/CD**: Set up GitHub Actions for automatic deployment
6. **Load Balancing**: Use container orchestration (Kubernetes)

## Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [Django with Docker](https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/uwsgi/)
- [Channels Deployment](https://channels.readthedocs.io/en/latest/deployment/index.html)

## Support

For issues:
1. Check logs: `docker-compose logs web`
2. Check GitHub: https://github.com/ranjeet3345/TicTacToewithAI
3. Review DOCKER_README.md for detailed information

---

**Status**: ✅ Docker and Docker Compose configured successfully!
