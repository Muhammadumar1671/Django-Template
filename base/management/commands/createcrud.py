"""
Django management command to auto-generate CRUD APIs for models.

Usage:
    python manage.py createcrud <app_name> <models_file>
    
Example:
    python manage.py createcrud products apps/products/models.py
    
This will:
1. Scan the models file for all Django models
2. Generate serializers, viewsets, services, and URLs
3. Automatically add app to INSTALLED_APPS
4. Automatically add URLs to main urls.py
"""

import os
import re
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Auto-generate CRUD APIs and configure app automatically'

    def add_arguments(self, parser):
        parser.add_argument(
            'app_name',
            type=str,
            help='Name of the app (e.g., users, products)'
        )
        parser.add_argument(
            'models_file',
            type=str,
            help='Path to the models file (e.g., apps/products/models.py)'
        )
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='Overwrite existing files'
        )

    def handle(self, *args, **options):
        app_name = options['app_name']
        models_file = options['models_file']
        overwrite = options['overwrite']

        # Validate models file exists
        if not os.path.exists(models_file):
            raise CommandError(f"Models file '{models_file}' does not exist")

        self.stdout.write(self.style.SUCCESS(f'\n🚀 Starting CRUD generation for app: {app_name}'))
        self.stdout.write(f'📁 Models file: {models_file}\n')

        # Extract models from the file
        model_classes = self.extract_models(models_file)
        
        if not model_classes:
            raise CommandError(f"No Django models found in '{models_file}'")

        self.stdout.write(self.style.SUCCESS(f'✅ Found {len(model_classes)} model(s):'))
        for model_name in model_classes.keys():
            self.stdout.write(f'   - {model_name}')

        # Get app directory
        models_path = Path(models_file)
        if models_path.parent.name == 'models':
            app_dir = models_path.parent.parent
        else:
            app_dir = models_path.parent

        # Create necessary directories
        self.create_directories(app_dir)

        # Generate files
        self.generate_serializers(app_dir, app_name, model_classes, overwrite)
        self.generate_viewsets(app_dir, app_name, model_classes, overwrite)
        self.generate_services(app_dir, app_name, model_classes, overwrite)
        self.generate_urls(app_dir, app_name, model_classes, overwrite)
        
        # Create apps.py if it doesn't exist
        self.create_apps_config(app_dir, app_name, overwrite)
        
        # Automatically add to INSTALLED_APPS
        self.add_to_installed_apps(app_name)
        
        # Automatically add to main urls.py
        self.add_to_main_urls(app_name)

        self.stdout.write(self.style.SUCCESS('\n✨ CRUD generation completed successfully!'))
        self.stdout.write(self.style.SUCCESS('✅ App added to INSTALLED_APPS'))
        self.stdout.write(self.style.SUCCESS('✅ URLs added to main urls.py'))
        self.stdout.write('\n📝 Next steps:')
        self.stdout.write(f'   1. Run migrations: python manage.py makemigrations {app_name}')
        self.stdout.write(f'   2. Run migrate: python manage.py migrate')
        self.stdout.write(f'   3. Your API is ready at: http://localhost:8000/api/{app_name}/\n')

    def extract_models(self, models_file):
        """Extract all Django model classes from a Python file using AST parsing."""
        import ast
        
        model_classes = {}
        
        try:
            with open(models_file, 'r') as f:
                tree = ast.parse(f.read(), filename=models_file)
        except Exception as e:
            raise CommandError(f"Error parsing models file: {e}")
        
        # Find all class definitions
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if class inherits from models.Model
                for base in node.bases:
                    base_name = None
                    if isinstance(base, ast.Attribute):
                        if isinstance(base.value, ast.Name) and base.value.id == 'models' and base.attr == 'Model':
                            base_name = 'Model'
                    elif isinstance(base, ast.Name):
                        if base.id == 'Model':
                            base_name = 'Model'
                    
                    if base_name:
                        model_classes[node.name] = node
                        break

        return model_classes

    def create_directories(self, app_dir):
        """Create necessary directories for the app structure."""
        directories = ['serializers', 'views', 'services']
        for dir_name in directories:
            dir_path = app_dir / dir_name
            dir_path.mkdir(exist_ok=True)
            init_file = dir_path / '__init__.py'
            if not init_file.exists():
                init_file.touch()

    def generate_serializers(self, app_dir, app_name, model_classes, overwrite):
        """Generate individual serializer files for each model."""
        serializers_dir = app_dir / 'serializers'
        
        for model_name in model_classes.keys():
            serializer_file = serializers_dir / f'{model_name.lower()}_serializer.py'
            
            if serializer_file.exists() and not overwrite:
                self.stdout.write(self.style.WARNING(f'⚠️  Skipping {serializer_file.name}'))
                continue

            content = f'''"""Serializer for {model_name} model."""

from rest_framework import serializers
from apps.{app_name}.models import {model_name}


class {model_name}Serializer(serializers.ModelSerializer):
    """Serializer for {model_name} model with full CRUD support."""
    
    class Meta:
        model = {model_name}
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
'''
            serializer_file.write_text(content)
            self.stdout.write(self.style.SUCCESS(f'✅ Generated: serializers/{serializer_file.name}'))

        # Update __init__.py
        init_file = serializers_dir / '__init__.py'
        init_content = '"""Auto-generated serializers."""\n\n'
        for model_name in model_classes.keys():
            init_content += f'from .{model_name.lower()}_serializer import {model_name}Serializer\n'
        init_content += '\n__all__ = [\n'
        for model_name in model_classes.keys():
            init_content += f"    '{model_name}Serializer',\n"
        init_content += ']\n'
        init_file.write_text(init_content)

    def generate_viewsets(self, app_dir, app_name, model_classes, overwrite):
        """Generate individual viewset files for each model."""
        views_dir = app_dir / 'views'

        for model_name in model_classes.keys():
            viewset_file = views_dir / f'{model_name.lower()}_viewset.py'
            
            if viewset_file.exists() and not overwrite:
                self.stdout.write(self.style.WARNING(f'⚠️  Skipping {viewset_file.name}'))
                continue

            content = f'''"""ViewSet for {model_name} model."""

from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.{app_name}.models import {model_name}
from apps.{app_name}.serializers import {model_name}Serializer
from apps.{app_name}.services.{model_name.lower()}_service import {model_name}Service


class {model_name}ViewSet(viewsets.ModelViewSet):
    """
    ViewSet for {model_name} with full CRUD operations.
    
    Endpoints:
    - GET    /api/{app_name}/{model_name.lower()}s/     - List all
    - POST   /api/{app_name}/{model_name.lower()}s/     - Create new
    - GET    /api/{app_name}/{model_name.lower()}s/{{id}}/ - Retrieve one
    - PUT    /api/{app_name}/{model_name.lower()}s/{{id}}/ - Update (full)
    - PATCH  /api/{app_name}/{model_name.lower()}s/{{id}}/ - Update (partial)
    - DELETE /api/{app_name}/{model_name.lower()}s/{{id}}/ - Delete
    """
    queryset = {model_name}.objects.all()
    serializer_class = {model_name}Serializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Uncomment and customize as needed:
    # filterset_fields = ['field1', 'field2']
    # search_fields = ['field1', 'field2']
    # ordering_fields = ['created_at', 'updated_at']
    # ordering = ['-created_at']
    
    def get_queryset(self):
        """Override to add custom filtering."""
        return {model_name}Service.get_all()
    
    def perform_create(self, serializer):
        """Use service layer for creation."""
        {model_name}Service.create(serializer.validated_data)
    
    def perform_update(self, serializer):
        """Use service layer for updates."""
        {model_name}Service.update(serializer.instance, serializer.validated_data)
    
    def perform_destroy(self, instance):
        """Use service layer for deletion."""
        {model_name}Service.delete(instance)
'''
            viewset_file.write_text(content)
            self.stdout.write(self.style.SUCCESS(f'✅ Generated: views/{viewset_file.name}'))

        # Update __init__.py
        init_file = views_dir / '__init__.py'
        init_content = '"""Auto-generated viewsets."""\n\n'
        for model_name in model_classes.keys():
            init_content += f'from .{model_name.lower()}_viewset import {model_name}ViewSet\n'
        init_content += '\n__all__ = [\n'
        for model_name in model_classes.keys():
            init_content += f"    '{model_name}ViewSet',\n"
        init_content += ']\n'
        init_file.write_text(init_content)

    def generate_services(self, app_dir, app_name, model_classes, overwrite):
        """Generate individual service files for each model."""
        services_dir = app_dir / 'services'

        for model_name in model_classes.keys():
            service_file = services_dir / f'{model_name.lower()}_service.py'
            
            if service_file.exists() and not overwrite:
                self.stdout.write(self.style.WARNING(f'⚠️  Skipping {service_file.name}'))
                continue

            content = f'''"""Service layer for {model_name} model."""

from django.db import transaction
from apps.{app_name}.models import {model_name}


class {model_name}Service:
    """Business logic for {model_name}."""
    
    @staticmethod
    def get_all():
        """Get all {model_name} instances."""
        return {model_name}.objects.all()
    
    @staticmethod
    def get_by_id(id):
        """Get {model_name} by ID."""
        return {model_name}.objects.filter(id=id).first()
    
    @staticmethod
    @transaction.atomic
    def create(data):
        """Create a new {model_name}."""
        return {model_name}.objects.create(**data)
    
    @staticmethod
    @transaction.atomic
    def update(instance, data):
        """Update an existing {model_name}."""
        for key, value in data.items():
            setattr(instance, key, value)
        instance.save()
        return instance
    
    @staticmethod
    @transaction.atomic
    def delete(instance):
        """Delete a {model_name}."""
        instance.delete()
'''
            service_file.write_text(content)
            self.stdout.write(self.style.SUCCESS(f'✅ Generated: services/{service_file.name}'))

        # Update __init__.py
        init_file = services_dir / '__init__.py'
        init_content = '"""Auto-generated services."""\n\n'
        for model_name in model_classes.keys():
            init_content += f'from .{model_name.lower()}_service import {model_name}Service\n'
        init_content += '\n__all__ = [\n'
        for model_name in model_classes.keys():
            init_content += f"    '{model_name}Service',\n"
        init_content += ']\n'
        init_file.write_text(init_content)

    def generate_urls(self, app_dir, app_name, model_classes, overwrite):
        """Generate URL routes for all viewsets."""
        urls_file = app_dir / 'urls.py'

        if urls_file.exists() and not overwrite:
            self.stdout.write(self.style.WARNING(f'⚠️  Skipping urls.py'))
            return

        content = f'''"""URL routes for {app_name} app."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.{app_name}.views import (
'''
        for model_name in model_classes.keys():
            content += f'    {model_name}ViewSet,\n'
        
        content += ''')\n
router = DefaultRouter()
'''
        for model_name in model_classes.keys():
            url_name = f"{model_name.lower()}s"
            content += f"router.register(r'{url_name}', {model_name}ViewSet, basename='{model_name.lower()}')\n"

        content += f'''
app_name = '{app_name}'

urlpatterns = [
    path('', include(router.urls)),
]
'''
        urls_file.write_text(content)
        self.stdout.write(self.style.SUCCESS(f'✅ Generated: urls.py'))

    def create_apps_config(self, app_dir, app_name, overwrite):
        """Create apps.py configuration file."""
        apps_file = app_dir / 'apps.py'
        
        if apps_file.exists() and not overwrite:
            return

        content = f'''from django.apps import AppConfig


class {app_name.capitalize()}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.{app_name}'
    label = '{app_name}'
'''
        apps_file.write_text(content)
        self.stdout.write(self.style.SUCCESS(f'✅ Generated: apps.py'))

    def add_to_installed_apps(self, app_name):
        """Automatically add app to INSTALLED_APPS in settings."""
        settings_file = Path('base/core/base.py')
        
        if not settings_file.exists():
            self.stdout.write(self.style.WARNING('⚠️  Could not find base/core/base.py'))
            return

        content = settings_file.read_text()
        app_entry = f"'apps.{app_name}'"
        
        # Check if already added
        if app_entry in content:
            self.stdout.write(self.style.WARNING(f'⚠️  App already in INSTALLED_APPS'))
            return

        # Find LOCAL_APPS and add the app
        pattern = r"(LOCAL_APPS\s*=\s*\[)([^\]]*)(])"
        
        def add_app(match):
            start = match.group(1)
            apps = match.group(2)
            end = match.group(3)
            
            # Add the new app
            if apps.strip():
                return f"{start}{apps}\n    {app_entry},\n{end}"
            else:
                return f"{start}\n    {app_entry},\n{end}"
        
        new_content = re.sub(pattern, add_app, content, flags=re.DOTALL)
        settings_file.write_text(new_content)

    def add_to_main_urls(self, app_name):
        """Automatically add app URLs to main urls.py."""
        urls_file = Path('base/urls.py')
        
        if not urls_file.exists():
            self.stdout.write(self.style.WARNING('⚠️  Could not find base/urls.py'))
            return

        content = urls_file.read_text()
        url_pattern = f"path('api/{app_name}/', include('apps.{app_name}.urls'))"
        
        # Check if already added
        if f"api/{app_name}/" in content:
            self.stdout.write(self.style.WARNING(f'⚠️  URLs already added'))
            return

        # Ensure 'include' is imported
        if 'from django.urls import' in content and 'include' not in content:
            content = content.replace(
                'from django.urls import path',
                'from django.urls import path, include'
            )

        # Find urlpatterns and add the new path
        pattern = r"(urlpatterns\s*=\s*\[)([^\]]*)(])"
        
        def add_url(match):
            start = match.group(1)
            patterns = match.group(2)
            end = match.group(3)
            
            return f"{start}{patterns}\n    {url_pattern},\n{end}"
        
        new_content = re.sub(pattern, add_url, content, flags=re.DOTALL)
        urls_file.write_text(new_content)
