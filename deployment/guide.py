"""
Deployment guide and production configuration
"""
import os
import subprocess
import sys
from pathlib import Path


class DeploymentGuide:
    """Guide for deploying the Agentic POC"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.requirements = [
            "docker",
            "docker-compose",
            "ollama"
        ]
    
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are installed"""
        print("🔍 Checking deployment prerequisites...")
        
        all_good = True
        
        # Check Docker
        try:
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Docker: {result.stdout.strip()}")
            else:
                print("❌ Docker: Not installed or not accessible")
                all_good = False
        except FileNotFoundError:
            print("❌ Docker: Not installed")
            all_good = False
        
        # Check Docker Compose
        try:
            result = subprocess.run(['docker-compose', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Docker Compose: {result.stdout.strip()}")
            else:
                # Try docker compose (newer syntax)
                result = subprocess.run(['docker', 'compose', 'version'], capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✅ Docker Compose: {result.stdout.strip()}")
                else:
                    print("❌ Docker Compose: Not installed or not accessible")
                    all_good = False
        except FileNotFoundError:
            print("❌ Docker Compose: Not installed")
            all_good = False
        
        # Check Ollama (optional for containerized deployment)
        try:
            result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Ollama: {result.stdout.strip()}")
            else:
                print("⚠️  Ollama: Not accessible (will use containerized version)")
        except FileNotFoundError:
            print("ℹ️  Ollama: Not installed locally (will use containerized version)")
        
        return all_good
    
    def generate_docker_compose(self):
        """Generate docker-compose.yml for production deployment"""
        docker_compose_content = """version: '3.8'

services:
  # Qdrant Vector Database
  qdrant:
    image: qdrant/qdrant:v1.7.4
    container_name: agentic_qdrant
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage
    environment:
      - QDRANT__SERVICE__HTTP_PORT=6333
      - QDRANT__SERVICE__GRPC_PORT=6334
    restart: unless-stopped
    networks:
      - agentic_network

  # Ollama for Local LLM
  ollama:
    image: ollama/ollama:latest
    container_name: agentic_ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_HOST=0.0.0.0:11434
    restart: unless-stopped
    networks:
      - agentic_network
    # GPU support (uncomment if you have NVIDIA GPU)
    # deploy:
    #   resources:
    #     reservations:
    #       devices:
    #         - driver: nvidia
    #           count: 1
    #           capabilities: [gpu]

  # Main Application
  agentic_app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: agentic_app
    ports:
      - "8000:8000"
    volumes:
      - ./business_rules:/app/business_rules:ro
      - ./logs:/app/logs
    environment:
      - QDRANT_URL=http://qdrant:6333
      - OLLAMA_BASE_URL=http://ollama:11434
      - API_HOST=0.0.0.0
      - API_PORT=8000
      - LOG_LEVEL=INFO
    depends_on:
      - qdrant
      - ollama
    restart: unless-stopped
    networks:
      - agentic_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Nginx Reverse Proxy (optional)
  nginx:
    image: nginx:alpine
    container_name: agentic_nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - agentic_app
    restart: unless-stopped
    networks:
      - agentic_network

volumes:
  qdrant_data:
  ollama_data:

networks:
  agentic_network:
    driver: bridge
"""
        
        compose_file = self.project_root / "docker-compose.yml"
        compose_file.write_text(docker_compose_content)
        print(f"✅ Generated docker-compose.yml at {compose_file}")
    
    def generate_dockerfile(self):
        """Generate Dockerfile for the application"""
        dockerfile_content = """# Multi-stage build for Python application
FROM python:3.11-slim as builder

# Set build arguments
ARG POETRY_VERSION=1.7.1

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==$POETRY_VERSION

# Set poetry configuration
RUN poetry config virtualenvs.create false

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-dev --no-interaction --no-ansi

# Production stage
FROM python:3.11-slim

# Create application user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs business_rules

# Set permissions
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Start command
CMD ["python", "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
        
        dockerfile = self.project_root / "Dockerfile"
        dockerfile.write_text(dockerfile_content)
        print(f"✅ Generated Dockerfile at {dockerfile}")
    
    def generate_nginx_config(self):
        """Generate Nginx configuration"""
        nginx_config = """events {
    worker_connections 1024;
}

http {
    upstream agentic_app {
        server agentic_app:8000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

    server {
        listen 80;
        server_name localhost;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";

        # Rate limiting
        limit_req zone=api burst=20 nodelay;

        # API endpoints
        location /api/ {
            proxy_pass http://agentic_app/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Timeouts
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }

        # Health check
        location /health {
            proxy_pass http://agentic_app/health;
            access_log off;
        }

        # Static files (if any)
        location /static/ {
            alias /app/static/;
            expires 30d;
        }
    }

    # SSL configuration (uncomment and configure for HTTPS)
    # server {
    #     listen 443 ssl http2;
    #     server_name your-domain.com;
    #
    #     ssl_certificate /etc/nginx/ssl/cert.pem;
    #     ssl_certificate_key /etc/nginx/ssl/key.pem;
    #     ssl_protocols TLSv1.2 TLSv1.3;
    #     ssl_ciphers HIGH:!aNULL:!MD5;
    #
    #     location / {
    #         proxy_pass http://agentic_app;
    #         proxy_set_header Host $host;
    #         proxy_set_header X-Real-IP $remote_addr;
    #         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    #         proxy_set_header X-Forwarded-Proto $scheme;
    #     }
    # }
}
"""
        
        nginx_file = self.project_root / "nginx.conf"
        nginx_file.write_text(nginx_config)
        print(f"✅ Generated nginx.conf at {nginx_file}")
    
    def generate_deployment_script(self):
        """Generate deployment script"""
        deploy_script = """#!/bin/bash

set -e

echo "🚀 Deploying Agentic Business Rules POC"

# Check if docker-compose is available
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    echo "❌ Docker Compose not found"
    exit 1
fi

# Stop existing containers
echo "🛑 Stopping existing containers..."
$COMPOSE_CMD down

# Pull latest images
echo "📥 Pulling latest images..."
$COMPOSE_CMD pull

# Build application image
echo "🏗️  Building application image..."
$COMPOSE_CMD build agentic_app

# Start services
echo "🚀 Starting services..."
$COMPOSE_CMD up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check health
echo "🔍 Checking service health..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Application is healthy"
else
    echo "❌ Application health check failed"
    $COMPOSE_CMD logs agentic_app
    exit 1
fi

# Initialize Ollama model (if needed)
echo "🤖 Initializing Ollama model..."
docker exec agentic_ollama ollama pull llama2:7b || echo "⚠️  Ollama model initialization may take time"

echo "🎉 Deployment complete!"
echo "🌐 Application available at: http://localhost:8000"
echo "📊 Qdrant available at: http://localhost:6333/dashboard"
echo "🤖 Ollama available at: http://localhost:11434"

echo ""
echo "📖 Next steps:"
echo "1. Check logs: $COMPOSE_CMD logs -f agentic_app"
echo "2. Test API: curl http://localhost:8000/health"
echo "3. View Qdrant dashboard: http://localhost:6333/dashboard"
"""
        
        deploy_script_file = self.project_root / "deploy.sh"
        deploy_script_file.write_text(deploy_script)
        deploy_script_file.chmod(0o755)
        print(f"✅ Generated deploy.sh at {deploy_script_file}")
    
    def generate_monitoring_config(self):
        """Generate monitoring configuration"""
        monitoring_compose = """# Additional monitoring services for docker-compose.yml
# Add these services to your existing docker-compose.yml

  # Prometheus for metrics
  prometheus:
    image: prom/prometheus:latest
    container_name: agentic_prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/usr/share/prometheus/console_libraries'
      - '--web.console.templates=/usr/share/prometheus/consoles'
    networks:
      - agentic_network

  # Grafana for visualization
  grafana:
    image: grafana/grafana:latest
    container_name: agentic_grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana-datasources.yml:/etc/grafana/provisioning/datasources/datasources.yml:ro
      - ./monitoring/grafana-dashboards.yml:/etc/grafana/provisioning/dashboards/dashboards.yml:ro
      - ./monitoring/dashboards:/var/lib/grafana/dashboards:ro
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
    networks:
      - agentic_network

volumes:
  prometheus_data:
  grafana_data:
"""
        
        monitoring_dir = self.project_root / "monitoring"
        monitoring_dir.mkdir(exist_ok=True)
        
        (monitoring_dir / "docker-compose-monitoring.yml").write_text(monitoring_compose)
        print(f"✅ Generated monitoring configuration in {monitoring_dir}")
    
    def run_deployment_guide(self):
        """Run the complete deployment guide"""
        print("🏗️  Agentic POC Deployment Guide")
        print("=" * 50)
        
        if not self.check_prerequisites():
            print("\n❌ Please install missing prerequisites before continuing")
            return False
        
        print("\n📝 Generating deployment files...")
        self.generate_dockerfile()
        self.generate_docker_compose()
        self.generate_nginx_config()
        self.generate_deployment_script()
        self.generate_monitoring_config()
        
        print("\n🎉 Deployment files generated successfully!")
        print("\n📋 Next steps:")
        print("1. Review and customize the generated files")
        print("2. Run: ./deploy.sh")
        print("3. Access the application at http://localhost:8000")
        print("4. Monitor with Grafana at http://localhost:3000 (admin/admin123)")
        
        return True


if __name__ == "__main__":
    guide = DeploymentGuide()
    guide.run_deployment_guide()