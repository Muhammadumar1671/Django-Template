# Django Auto-CRUD Template

A powerful Django starter template that **automatically generates complete CRUD APIs** from your models with a single command. Everything is configured automatically - just define your models and run one command!

## 🚀 Main Feature: One-Command CRUD Generation

```bash
python manage.py createcrud products apps/products/models.py
```

**This single command does EVERYTHING:**
- ✅ Scans your models file and detects all Django models
- ✅ Generates serializers in `serializers/` folder (one file per model)
- ✅ Generates viewsets in `views/` folder (one file per model)
- ✅ Generates services in `services/` folder (one file per model)
- ✅ Generates `urls.py` with RESTful routing
- ✅ Creates `apps.py` configuration
- ✅ **Automatically adds app to INSTALLED_APPS**
- ✅ **Automatically adds URLs to main urls.py**

**That's it! Your API is ready to use.**

---

## 📋 Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/Muhammadumar1671/Django-Template.git
cd Django-Template
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env if needed
```

### 3. Run Initial Migrations

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
```

### 4. Create Your First CRUD API

```bash
# Create app directory
mkdir -p apps/products

# Create your models
cat > apps/products/models.py << 'EOF'
from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'categories'
    
    def __str__(self):
        return self.name
EOF

# Create __init__.py
touch apps/products/__init__.py

# Generate CRUD APIs (ONE COMMAND!)
python manage.py createcrud products apps/products/models.py

# Run migrations
python manage.py makemigrations products
python manage.py migrate

# Start server
python manage.py runserver
```

### 5. Test Your API

Your API is now available at:
- `http://localhost:8000/api/products/products/` - Product CRUD
- `http://localhost:8000/api/products/categories/` - Category CRUD
- `http://localhost:8000/admin/` - Admin interface

---

## 📁 Generated Structure

After running `createcrud`, your app will have this structure:

```
apps/products/
├── __init__.py
├── apps.py                    # Auto-generated
├── models.py                  # You create this
├── serializers/               # Auto-generated
│   ├── __init__.py
│   ├── product_serializer.py
│   └── category_serializer.py
├── views/                     # Auto-generated
│   ├── __init__.py
│   ├── product_viewset.py
│   └── category_viewset.py
├── services/                  # Auto-generated
│   ├── __init__.py
│   ├── product_service.py
│   └── category_service.py
└── urls.py                    # Auto-generated
```

---

## 🎯 What Gets Generated

### Serializers (`serializers/product_serializer.py`)

```python
from rest_framework import serializers
from apps.products.models import Product

class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model with full CRUD support."""
    
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
```

### ViewSets (`views/product_viewset.py`)

```python
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for Product with full CRUD operations."""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Customize filtering, searching, ordering as needed
```

### Services (`services/product_service.py`)

```python
from django.db import transaction
from apps.products.models import Product

class ProductService:
    """Business logic for Product."""
    
    @staticmethod
    def get_all():
        return Product.objects.all()
    
    @staticmethod
    @transaction.atomic
    def create(data):
        return Product.objects.create(**data)
    
    # + update, delete, get_by_id methods
```

### URLs (`urls.py`)

```python
from rest_framework.routers import DefaultRouter
from apps.products.views import ProductViewSet, CategoryViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    path('', include(router.urls)),
]
```

---

## 🔧 Command Options

### Basic Usage

```bash
python manage.py createcrud <app_name> <models_file>
```

### Overwrite Existing Files

```bash
python manage.py createcrud products apps/products/models.py --overwrite
```

This will regenerate all files, overwriting existing ones.

---

## 📊 API Endpoints

After generation, you get these endpoints for each model:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/products/products/` | List all products |
| POST | `/api/products/products/` | Create new product |
| GET | `/api/products/products/{id}/` | Get specific product |
| PUT | `/api/products/products/{id}/` | Update product (full) |
| PATCH | `/api/products/products/{id}/` | Update product (partial) |
| DELETE | `/api/products/products/{id}/` | Delete product |

**Built-in features:**
- Filtering: `?field=value`
- Searching: `?search=query`
- Ordering: `?ordering=-created_at`
- Pagination: Automatic

---

## ✨ Additional Features

### 🎨 Modern Admin Interface
- **Unfold Admin** - Beautiful, modern Django admin
- Responsive design
- Clean and intuitive

### ⚙️ Pre-configured Settings
- **Environment-based config** - Separate dev/prod settings
- **Django REST Framework** - Full API support
- **JWT Authentication** - Secure token-based auth
- **CORS Support** - Cross-origin requests
- **Celery Integration** - Async task processing
- **Redis Caching** - High-performance caching
- **Django Channels** - WebSocket support

### 🛠️ Developer-Friendly
- **SQLite for dev** - No database setup needed
- **PostgreSQL for prod** - Production-ready
- **Clean console output** - No SQL query spam
- **Organized structure** - Apps in `apps/` folder
- **Service layer** - Proper separation of concerns

---

## 📁 Project Structure

```
django-plugin/
├── apps/                      # All your Django apps
│   └── your_app/
│       ├── models.py
│       ├── serializers/
│       ├── views/
│       ├── services/
│       └── urls.py
├── base/                      # Main project
│   ├── core/
│   │   ├── base.py           # Base settings
│   │   ├── development.py    # Dev settings
│   │   └── production.py     # Prod settings
│   ├── management/
│   │   └── commands/
│   │       └── createcrud.py # Magic command!
│   ├── settings.py           # Settings router
│   └── urls.py               # Main URLs
├── logs/                     # Application logs
├── staticfiles/              # Static files
├── .env                      # Environment variables
├── .gitignore               # Git ignore rules
├── manage.py                # Django management
├── requirements.txt         # Dependencies
└── README.md               # This file
```

---

## 🎨 Customization

After generation, customize the generated code:

### Add Filtering

In `views/product_viewset.py`:

```python
class ProductViewSet(viewsets.ModelViewSet):
    # ...
    filterset_fields = ['is_active', 'price']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at']
    ordering = ['-created_at']
```

### Add Custom Actions

```python
from rest_framework.decorators import action
from rest_framework.response import Response

class ProductViewSet(viewsets.ModelViewSet):
    # ...
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only active products."""
        active_products = self.queryset.filter(is_active=True)
        serializer = self.get_serializer(active_products, many=True)
        return Response(serializer.data)
```

### Add Business Logic

In `services/product_service.py`:

```python
class ProductService:
    # ...
    
    @staticmethod
    def get_active_products():
        """Get all active products."""
        return Product.objects.filter(is_active=True)
    
    @staticmethod
    def search_by_name(name):
        """Search products by name."""
        return Product.objects.filter(name__icontains=name)
```

---

## 🔒 Authentication

By default, all endpoints require JWT authentication.

### Get Token

```bash
POST /api/token/
{
    "username": "your_username",
    "password": "your_password"
}
```

### Use Token

```bash
GET /api/products/products/
Authorization: Bearer <your_access_token>
```

### Change Permissions

In `views/product_viewset.py`:

```python
from rest_framework.permissions import AllowAny, IsAdminUser

class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]  # Public access
    
    # Or per-action permissions:
    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [IsAdminUser()]
        return [AllowAny()]
```

---

## 🌍 Environment Variables

Key variables in `.env`:

```env
# Environment
DJANGO_ENV=development  # or 'production'

# Security
DJANGO_SECRET_KEY=your-secret-key

# Database (optional - defaults to SQLite)
USE_POSTGRES=False
DB_NAME=django_db
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

# Redis (optional)
REDIS_URL=redis://localhost:6379/1

# Celery (optional)
CELERY_BROKER_URL=redis://localhost:6379/0
```

---

## 🚀 Deployment

### Production Checklist

1. Set `DJANGO_ENV=production`
2. Configure PostgreSQL database
3. Set up Redis for caching
4. Set secure `SECRET_KEY`
5. Configure `ALLOWED_HOSTS`
6. Use Gunicorn/uWSGI
7. Set up Nginx/Apache
8. Enable HTTPS

### Example Production Setup

```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn base.wsgi:application --bind 0.0.0.0:8000
```

---

## 💡 Best Practices

1. **Keep models simple** - One model per business entity
2. **Use services** - Put business logic in services, not views
3. **Customize after generation** - Generated code is a starting point
4. **Add tests** - Create tests for models and APIs
5. **Document your APIs** - Add docstrings to viewsets
6. **Use transactions** - Wrap complex operations in `@transaction.atomic`
7. **Validate data** - Add custom validation in serializers/services

---

## 🐛 Troubleshooting

### Command not found

Make sure `'base'` is in `INSTALLED_APPS` in `base/core/base.py`.

### Import errors

Ensure:
- App has `__init__.py` and `apps.py`
- Models file has no syntax errors
- App is in `apps/` directory

### URLs not working

Check:
- App was added to INSTALLED_APPS
- URLs were added to main `urls.py`
- You ran migrations

---

## 📚 Tech Stack

- **Django 6.0+** - Web framework
- **Django REST Framework** - API framework
- **SimpleJWT** - JWT authentication
- **django-filter** - Filtering support
- **Unfold** - Modern admin interface
- **Celery** - Async tasks
- **Redis** - Caching & message broker
- **Channels** - WebSocket support
- **PostgreSQL** - Production database
- **WhiteNoise** - Static file serving

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 🎓 Example Workflow

```bash
# 1. Create app directory
mkdir -p apps/blog

# 2. Create models
cat > apps/blog/models.py << 'EOF'
from django.db import models

class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
EOF

# 3. Create __init__.py
touch apps/blog/__init__.py

# 4. Generate CRUD (ONE COMMAND DOES EVERYTHING!)
python manage.py createcrud blog apps/blog/models.py

# 5. Run migrations
python manage.py makemigrations blog
python manage.py migrate

# 6. Start server
python manage.py runserver

# 7. Your API is ready!
# http://localhost:8000/api/blog/posts/
```

---

**Built with ❤️ for rapid Django API development**

**Happy Coding! 🚀**
