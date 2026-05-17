# fullstack_developer_capstone - Premium Auto Dealers

> **Project:** fullstack_developer_capstone  
> **Repository:** xrwvm-fullstack_developer_capstone  

Full-stack car dealership web application with Django backend, React frontend, Express/MongoDB microservice, and sentiment analysis.

## Architecture

- **Django Application**: Main web app serving static pages, dynamic templates, and REST APIs
- **Express/MongoDB Service**: Microservice managing dealers and reviews
- **Sentiment Analyzer**: External service for review sentiment analysis
- **React Frontend**: User registration component
- **CI/CD**: GitHub Actions for linting and testing

## Project Structure

```
├── server/                    # Django application
│   ├── djangoproj/            # Django project settings
│   ├── djangoapp/             # Django app (models, views, APIs)
│   ├── frontend/              # Static files and React components
│   └── manage.py              # Django management script
├── dealership_service/        # Express + MongoDB microservice
│   ├── server.js              # Express API server
│   ├── models/                # Mongoose models
│   ├── Dockerfile
│   └── docker-compose.yml
└── .github/workflows/         # CI/CD pipeline
```

## Setup Instructions

### Prerequisites
- Python 3.12+
- Node.js 18+
- MongoDB (or Docker)
- Docker (optional, for containerized deployment)

### 1. Start the Express/MongoDB Service

Using Docker:
```bash
cd dealership_service
docker-compose up -d
```

Or manually:
```bash
cd dealership_service
npm install
# Ensure MongoDB is running on localhost:27017
node server.js
```

### 2. Start the Django Application

```bash
cd server
python3 -m venv djangoenv
source djangoenv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations djangoapp
python manage.py migrate
python manage.py seed_data
python manage.py createsuperuser
python manage.py runserver
```

### 3. Access the Application

- **Home**: http://localhost:8000/djangoapp/
- **About**: http://localhost:8000/about/
- **Contact**: http://localhost:8000/contact/
- **Admin**: http://localhost:8000/admin/

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /djangoapp/get_cars/` | Get all car makes and models |
| `GET /djangoapp/get_dealers/` | Get all dealers |
| `GET /djangoapp/get_dealers/<state>/` | Get dealers by state |
| `GET /djangoapp/api/dealer/<id>/` | Get dealer by ID |
| `GET /djangoapp/review/dealer/<id>/` | Get reviews for a dealer |
| `POST /djangoapp/add_review/` | Submit a review |
| `POST /djangoapp/login/` | User login |
| `GET /djangoapp/logout/` | User logout |
| `POST /djangoapp/register/` | User registration |
| `GET /djangoapp/analyze/<text>/` | Analyze review sentiment |

## cURL Examples

```bash
# Login
curl -X POST http://localhost:8000/djangoapp/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Get all dealers
curl http://localhost:8000/djangoapp/get_dealers/

# Get dealers by state
curl http://localhost:8000/djangoapp/get_dealers/KS/

# Get dealer by ID
curl http://localhost:8000/djangoapp/api/dealer/1/

# Get reviews for dealer
curl http://localhost:8000/djangoapp/review/dealer/1/

# Analyze sentiment
curl http://localhost:8000/djangoapp/analyze/Fantastic%20services/
```

## Deployment

The application can be deployed to Kubernetes using the provided Docker configuration. Update `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` in `server/djangoproj/settings.py` with your deployment URL.
