# Tic-Tac-Toe with AI - Docker Setup

This project is containerized with Docker and Docker Compose for easy deployment.

## Prerequisites

- Docker (version 20.10+)
- Docker Compose (version 1.29+)

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/ranjeet3345/TicTacToewithAI.git
cd TicTacToewithAI
```

### 2. Set up Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and add your settings:
- `GEMINI_API_KEY` - Your Google Generative AI API key (optional)
- `SECRET_KEY` - Django secret key (change in production)

### 3. Build and Run with Docker Compose

```bash
docker-compose up -d
```

This will:
- Build the Django application image
- Start Redis service
- Run database migrations
- Start the Daphne ASGI server

### 4. Access the Application

Open your browser and navigate to:
```
http://localhost:8000
```

## Available Services

### Web Service (Django + Daphne)
- URL: http://localhost:8000
- Auto-reloads on code changes (development mode)

### Redis Service
- Host: redis
- Port: 6379
- Used for WebSocket communication and Channels layer

## Docker Compose Commands

### Start services
```bash
docker-compose up -d
```

### View logs
```bash
docker-compose logs -f web
docker-compose logs -f redis
```

### Stop services
```bash
docker-compose down
```

### Remove all containers and volumes
```bash
docker-compose down -v
```

### Run migrations manually
```bash
docker-compose exec web python manage.py migrate
```

### Create superuser
```bash
docker-compose exec web python manage.py createsuperuser
```

### Access Django shell
```bash
docker-compose exec web python manage.py shell
```

## Production Deployment

For production, update the following in your environment:

1. Set `DEBUG=False`
2. Set a strong `SECRET_KEY`
3. Update `ALLOWED_HOSTS` with your domain
4. Use a proper database (PostgreSQL, MySQL, etc.)
5. Set up SSL/TLS certificates
6. Use environment-specific settings

### Update docker-compose.yml for Production

```yaml
environment:
  - DEBUG=False
  - SECRET_KEY=your-secure-key
  - ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

## Troubleshooting

### Port Already in Use

If port 8000 or 6379 is already in use, you can change them in `docker-compose.yml`:

```yaml
ports:
  - "8001:8000"  # Map to different port
```

### Redis Connection Error

Ensure Redis service is healthy:
```bash
docker-compose exec redis redis-cli ping
```

### Database Errors

Clear and reinitialize the database:
```bash
docker-compose down -v
docker-compose up -d
```

### Static Files Not Loading

Collect static files:
```bash
docker-compose exec web python manage.py collectstatic --noinput
```

## Project Structure

```
.
├── Dockerfile                 # Docker image configuration
├── docker-compose.yml        # Multi-container setup
├── .dockerignore             # Files to exclude from build
├── .env.example              # Environment variables template
├── requirements.txt          # Python dependencies
├── manage.py                 # Django management script
├── db.sqlite3                # SQLite database (mounted in Docker)
├── tic_tac_toe/             # Django project settings
│   ├── asgi.py              # ASGI configuration for Daphne
│   ├── settings.py          # Django settings
│   ├── urls.py              # URL routing
│   └── wsgi.py              # WSGI configuration
└── game/                    # Game application
    ├── models.py            # Database models
    ├── consumers.py         # WebSocket consumers
    ├── ai.py                # AI logic
    ├── views.py             # Views
    └── templates/           # HTML templates
```

## Features

- **Real-time Multiplayer**: Play with another player using WebSockets
- **AI Opponents**:
  - Minimax Algorithm (Unbeatable)
  - Google Gemini API (Human-like)
- **Async/ASGI**: Built with Django Channels for real-time communication
- **Containerized**: Fully Docker-compatible
- **Redis Integration**: For WebSocket message passing

## Notes

- The application uses SQLite by default (suitable for development)
- WebSocket connections require Redis for message passing
- The `.gitignore` excludes venv, __pycache__, and other build artifacts
- Environment variables are configured in `.env` file

## Support

For issues or questions, please visit the GitHub repository:
https://github.com/ranjeet3345/TicTacToewithAI
