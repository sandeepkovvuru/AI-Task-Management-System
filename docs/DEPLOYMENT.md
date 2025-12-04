# Deployment Guide

## Overview
This guide covers deployment of the AI-Task-Management-System to production using Docker, Docker Compose, and various cloud platforms.

## Prerequisites
- Docker and Docker Compose installed
- Git installed
- Cloud platform account (Heroku, Railway, AWS, Azure, or Google Cloud)
- Domain name (optional but recommended)

## Local Development Deployment

### Using Docker Compose

1. Clone the repository:
```bash
git clone https://github.com/sandeepkovvuru/AI-Task-Management-System.git
cd AI-Task-Management-System
```

2. Create environment files:
```bash
cp .env.example .env
cd backend && cp requirements.txt .
cd ../frontend && cp package.json .
cd ..
```

3. Update `.env` with your configuration:
```bash
vi .env
```

4. Start all services:
```bash
docker-compose up -d
```

5. Verify services:
```bash
docker-compose ps
```

6. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs

7. View logs:
```bash
docker-compose logs -f
```

## Production Deployment (Railway)

Railway is the easiest platform for deploying this application.

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Release v1.0.0"
git push origin main
```

### Step 2: Create Railway Project
1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub"
4. Connect your GitHub account
5. Select this repository

### Step 3: Configure Services

#### MongoDB
1. In Railway dashboard, click "Add"
2. Select "Database" → "MongoDB"
3. Configure credentials and save

#### Redis
1. Click "Add"
2. Select "Database" → "Redis"
3. Configure and save

#### Backend Service
1. Click "Add"
2. Select "GitHub Repo" (select this repo again)
3. In Variables tab, add:
   - MONGODB_URL (from MongoDB service)
   - REDIS_URL (from Redis service)
   - SECRET_KEY (generate new)
   - OPENAI_API_KEY (your API key)
4. Set root directory to `/backend`

#### Frontend Service
1. Click "Add"
2. Create from GitHub
3. Set root directory to `/frontend`
4. Add variables:
   - VITE_API_URL (Railway backend URL)

### Step 4: Deploy
1. Click the deploy button
2. Wait for services to start
3. Access your application from Railway public URL

## Production Deployment (Heroku)

### Prerequisites
- Heroku CLI installed
- Heroku account

### Deployment Steps

1. Login to Heroku:
```bash
heroku login
```

2. Create Heroku apps:
```bash
heroku create ai-task-mgmt-backend
heroku create ai-task-mgmt-frontend
```

3. Add buildpacks:
```bash
# For backend
heroku buildpacks:add heroku/python -a ai-task-mgmt-backend

# For frontend
heroku buildpacks:add heroku/nodejs -a ai-task-mgmt-frontend
```

4. Add MongoDB and Redis:
```bash
# Using Heroku add-ons or external services
heroku addons:create mongolab:sandbox -a ai-task-mgmt-backend
heroku addons:create heroku-redis:premium-0 -a ai-task-mgmt-backend
```

5. Set environment variables:
```bash
heroku config:set SECRET_KEY='your-secret-key' -a ai-task-mgmt-backend
heroku config:set OPENAI_API_KEY='your-api-key' -a ai-task-mgmt-backend
```

6. Deploy backend:
```bash
cd backend
git push heroku main
cd ..
```

7. Deploy frontend:
```bash
cd frontend
git push heroku main
```

## Production Deployment (AWS)

### Using ECS (Elastic Container Service)

1. Build Docker images:
```bash
docker build -t ai-task-backend:latest ./backend
docker build -t ai-task-frontend:latest ./frontend
```

2. Push to ECR:
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

docker tag ai-task-backend:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/ai-task-backend:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/ai-task-backend:latest
```

3. Create ECS cluster and services
4. Configure load balancer
5. Set up RDS for MongoDB/PostgreSQL
6. Configure CloudFront CDN

## Environment Variables for Production

### Critical (MUST CHANGE)
```
SECRET_KEY=generate-a-new-secure-key
MONGODB_URL=your-production-mongodb-url
REDIS_URL=your-production-redis-url
OPENAI_API_KEY=your-openai-api-key
ENVIRONMENT=production
```

### Optional but Recommended
```
CORS_ORIGINS=yourdomain.com,www.yourdomain.com
SMTP_SERVER=smtp.gmail.com
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
AWS_ACCESS_KEY_ID=your-aws-key
S3_BUCKET_NAME=your-bucket-name
```

## Health Checks & Monitoring

### Backend Health Check
```bash
curl http://localhost:8000/health
```

### Database Connection
```bash
curl http://localhost:8000/api/v1/tasks
```

### Setup Monitoring
1. Enable CloudWatch (AWS) or platform-specific monitoring
2. Set up alerts for error rates
3. Monitor database performance
4. Track API response times

## Database Backups

### MongoDB Backup
```bash
mongodump --uri="mongodb://admin:password@localhost:27017" --out=./backup
```

### MongoDB Restore
```bash
mongorestore --uri="mongodb://admin:password@localhost:27017" ./backup
```

## SSL/TLS Certificate

### Using Let's Encrypt
```bash
sudo certbot certonly --standalone -d yourdomain.com
```

### Update nginx configuration:
```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
}
```

## Troubleshooting

### Docker Compose Issues
```bash
# Clear containers and volumes
docker-compose down -v

# Rebuild images
docker-compose build --no-cache

# View detailed logs
docker-compose logs service-name
```

### Database Connection Issues
- Check MONGODB_URL format
- Verify MongoDB service is running
- Check network connectivity

### API Not Responding
- Check backend container logs
- Verify port mapping
- Check environment variables

## Performance Optimization

1. Enable Redis caching
2. Optimize MongoDB queries with indexes
3. Enable gzip compression in nginx
4. Use CDN for static files
5. Implement rate limiting
6. Enable database connection pooling

## Security Checklist

- [ ] Change default credentials
- [ ] Enable HTTPS/SSL
- [ ] Set up firewall rules
- [ ] Enable database encryption
- [ ] Implement rate limiting
- [ ] Set up Web Application Firewall (WAF)
- [ ] Regular security updates
- [ ] Enable audit logging
- [ ] Implement CORS properly
- [ ] Rotate API keys regularly

## Support

For deployment issues, please:
1. Check the logs: `docker-compose logs`
2. Review error messages carefully
3. Check .env file configuration
4. Verify all services are running
5. Create an issue on GitHub
