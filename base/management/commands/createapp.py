"""
Interactive Django app generator with CRUD APIs.

Usage:
    python manage.py createapp
    
This interactive command will:
1. Ask for app name
2. Optionally ask if you want to create models
3. Guide you through creating models interactively
4. Generate complete CRUD APIs automatically
5. Configure everything (INSTALLED_APPS, URLs, etc.)
"""

import os
import re
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Interactive app generator with CRUD APIs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--app-name',
            type=str,
            help='App name (skip interactive prompt)'
        )
        parser.add_argument(
            '--no-models',
            action='store_true',
            help='Skip model creation'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n🚀 Django App Generator with Auto-CRUD\n'))
        
        # Get app name
        app_name = options.get('app_name')
        if not app_name:
            app_name = self.get_input('Enter app name (e.g., products, users, blog): ')
        
        if not app_name or not app_name.isidentifier():
            raise CommandError('Invalid app name. Use only letters, numbers, and underscores.')
        
        # Check if app already exists
        app_dir = Path('apps') / app_name
        if app_dir.exists():
            overwrite = self.get_yes_no(f'App "{app_name}" already exists. Overwrite?')
            if not overwrite:
                self.stdout.write(self.style.WARNING('Aborted.'))
                return
        
        # Create app directory
        app_dir.mkdir(parents=True, exist_ok=True)
        self.stdout.write(self.style.SUCCESS(f'✅ Created app directory: apps/{app_name}/'))
        
        # Create __init__.py
        (app_dir / '__init__.py').touch()
        
        # Create apps.py
        self.create_apps_config(app_dir, app_name)
        
        # Ask about models
        create_models = not options.get('no_models')
        if create_models:
            create_models = self.get_yes_no('\nDo you want to create models now?', default=True)
        
        if create_models:
            models = self.create_models_interactively(app_dir, app_name)
            if models:
                # Generate CRUD
                self.generate_crud(app_dir, app_name, models)
        else:
            # Just create empty models.py
            models_file = app_dir / 'models.py'
            models_file.write_text('''from django.db import models


# Create your models here.
''')
            self.stdout.write(self.style.SUCCESS('✅ Created empty models.py'))
        
        # Add to INSTALLED_APPS
        self.add_to_installed_apps(app_name)
        
        # Add to URLs if models were created
        if create_models and models:
            self.add_to_main_urls(app_name)
        
        # Final instructions
        self.stdout.write(self.style.SUCCESS('\n✨ App created successfully!'))
        self.stdout.write('\n📝 Next steps:')
        if create_models and models:
            self.stdout.write(f'   1. Run migrations: python manage.py makemigrations {app_name}')
            self.stdout.write(f'   2. Run migrate: python manage.py migrate')
            self.stdout.write(f'   3. Your API is ready at: http://localhost:8000/api/{app_name}/')
        else:
            self.stdout.write(f'   1. Add models to apps/{app_name}/models.py')
            self.stdout.write(f'   2. Run: python manage.py generatecrud {app_name}')
        self.stdout.write('')

    def get_input(self, prompt):
        """Get user input."""
        return input(self.style.WARNING(prompt)).strip()

    def get_yes_no(self, prompt, default=False):
        """Get yes/no input from user."""
        default_str = 'Y/n' if default else 'y/N'
        response = input(self.style.WARNING(f'{prompt} [{default_str}]: ')).strip().lower()
        if not response:
            return default
        return response in ['y', 'yes']

    def create_models_interactively(self, app_dir, app_name):
        """Guide user through creating models."""
        self.stdout.write(self.style.SUCCESS('\n📋 Model Creation Wizard'))
        self.stdout.write('You can create multiple models. Press Enter without a name to finish.\n')
        
        models = []
        while True:
            model_name = self.get_input(f'Enter model name (or press Enter to finish): ')
            if not model_name:
                break
            
            if not model_name[0].isupper():
                model_name = model_name.capitalize()
            
            if not model_name.isidentifier():
                self.stdout.write(self.style.ERROR('Invalid model name. Use only letters and numbers.'))
                continue
            
            self.stdout.write(f'\n🔧 Creating model: {model_name}')
            fields = self.get_model_fields()
            
            models.append({
                'name': model_name,
                'fields': fields
            })
            
            self.stdout.write(self.style.SUCCESS(f'✅ Model "{model_name}" configured\n'))
        
        if not models:
            self.stdout.write(self.style.WARNING('No models created.'))
            return None
        
        # Generate models.py
        self.write_models_file(app_dir, app_name, models)
        return models

    def get_model_fields(self):
        """Get fields for a model."""
        self.stdout.write('Add fields (common fields like id, created_at, updated_at are added automatically)')
        self.stdout.write('Press Enter without a field name to finish.\n')
        
        fields = []
        field_types = {
            '1': ('CharField', 'max_length=255'),
            '2': ('TextField', ''),
            '3': ('IntegerField', ''),
            '4': ('BooleanField', 'default=True'),
            '5': ('DateTimeField', 'auto_now_add=True'),
            '6': ('DateField', ''),
            '7': ('EmailField', ''),
            '8': ('DecimalField', 'max_digits=10, decimal_places=2'),
            '9': ('ForeignKey', ''),
        }
        
        while True:
            field_name = self.get_input('  Field name (or Enter to finish): ')
            if not field_name:
                break
            
            if not field_name.isidentifier():
                self.stdout.write(self.style.ERROR('  Invalid field name.'))
                continue
            
            self.stdout.write('  Field type:')
            self.stdout.write('    1. CharField (text, max 255 chars)')
            self.stdout.write('    2. TextField (long text)')
            self.stdout.write('    3. IntegerField (number)')
            self.stdout.write('    4. BooleanField (true/false)')
            self.stdout.write('    5. DateTimeField (date and time)')
            self.stdout.write('    6. DateField (date only)')
            self.stdout.write('    7. EmailField (email)')
            self.stdout.write('    8. DecimalField (decimal number)')
            self.stdout.write('    9. ForeignKey (relation)')
            
            choice = self.get_input('  Choose (1-9): ')
            if choice not in field_types:
                self.stdout.write(self.style.ERROR('  Invalid choice.'))
                continue
            
            field_type, default_params = field_types[choice]
            
            # Ask for additional options
            nullable = self.get_yes_no('  Allow null/blank?', default=False)
            
            params = []
            if default_params:
                params.append(default_params)
            if nullable:
                params.append('null=True, blank=True')
            
            fields.append({
                'name': field_name,
                'type': field_type,
                'params': ', '.join(params) if params else ''
            })
            
            self.stdout.write(self.style.SUCCESS(f'  ✅ Added: {field_name}\n'))
        
        return fields

    def write_models_file(self, app_dir, app_name, models):
        """Write models.py file."""
        content = 'from django.db import models\n\n\n'
        
        for model in models:
            content += f'class {model["name"]}(models.Model):\n'
            content += f'    """Model for {model["name"]}."""\n\n'
            
            # Add fields
            for field in model['fields']:
                params = f'({field["params"]})' if field['params'] else '()'
                content += f'    {field["name"]} = models.{field["type"]}{params}\n'
            
            # Add timestamps
            content += '    created_at = models.DateTimeField(auto_now_add=True)\n'
            content += '    updated_at = models.DateTimeField(auto_now=True)\n\n'
            
            # Add Meta
            content += '    class Meta:\n'
            content += f'        db_table = \'{app_name}_{model["name"].lower()}\'\n'
            content += '        ordering = [\'-created_at\']\n\n'
            
            # Add __str__
            first_field = model['fields'][0]['name'] if model['fields'] else 'id'
            content += '    def __str__(self):\n'
            content += f'        return str(self.{first_field})\n\n\n'
        
        models_file = app_dir / 'models.py'
        models_file.write_text(content)
        self.stdout.write(self.style.SUCCESS(f'✅ Created models.py with {len(models)} model(s)'))

    def generate_crud(self, app_dir, app_name, models):
        """Generate CRUD files."""
        self.stdout.write(self.style.SUCCESS('\n🔧 Generating CRUD APIs...'))
        
        # Import the generation functions from createcrud command
        from base.management.commands.createcrud import Command as CrudCommand
        
        crud_cmd = CrudCommand()
        
        # Extract model names
        model_classes = {model['name']: None for model in models}
        
        # Create directories
        crud_cmd.create_directories(app_dir)
        
        # Generate files
        crud_cmd.generate_serializers(app_dir, app_name, model_classes, overwrite=True)
        crud_cmd.generate_viewsets(app_dir, app_name, model_classes, overwrite=True)
        crud_cmd.generate_services(app_dir, app_name, model_classes, overwrite=True)
        crud_cmd.generate_urls(app_dir, app_name, model_classes, overwrite=True)
        crud_cmd.generate_admin(app_dir, app_name, model_classes, overwrite=True)

    def create_apps_config(self, app_dir, app_name):
        """Create apps.py configuration file."""
        apps_file = app_dir / 'apps.py'
        
        content = f'''from django.apps import AppConfig


class {app_name.capitalize()}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.{app_name}'
    label = '{app_name}'
'''
        apps_file.write_text(content)
        self.stdout.write(self.style.SUCCESS(f'✅ Created apps.py'))

    def add_to_installed_apps(self, app_name):
        """Automatically add app to INSTALLED_APPS in settings."""
        settings_file = Path('base/core/base.py')
        
        if not settings_file.exists():
            return

        content = settings_file.read_text()
        app_entry = f"'apps.{app_name}'"
        
        if app_entry in content:
            return

        pattern = r"(LOCAL_APPS\s*=\s*\[)([^\]]*)(])"
        
        def add_app(match):
            start = match.group(1)
            apps = match.group(2)
            end = match.group(3)
            
            if apps.strip():
                return f"{start}{apps}\n    {app_entry},\n{end}"
            else:
                return f"{start}\n    {app_entry},\n{end}"
        
        new_content = re.sub(pattern, add_app, content, flags=re.DOTALL)
        settings_file.write_text(new_content)
        self.stdout.write(self.style.SUCCESS('✅ Added to INSTALLED_APPS'))

    def add_to_main_urls(self, app_name):
        """Automatically add app URLs to main urls.py."""
        urls_file = Path('base/urls.py')
        
        if not urls_file.exists():
            return

        content = urls_file.read_text()
        url_pattern = f"path('api/{app_name}/', include('apps.{app_name}.urls'))"
        
        if f"api/{app_name}/" in content:
            return

        if 'from django.urls import' in content and 'include' not in content:
            content = content.replace(
                'from django.urls import path',
                'from django.urls import path, include'
            )

        pattern = r"(urlpatterns\s*=\s*\[)([^\]]*)(])"
        
        def add_url(match):
            start = match.group(1)
            patterns = match.group(2)
            end = match.group(3)
            
            return f"{start}{patterns}\n    {url_pattern},\n{end}"
        
        new_content = re.sub(pattern, add_url, content, flags=re.DOTALL)
        urls_file.write_text(new_content)
        self.stdout.write(self.style.SUCCESS('✅ Added to main urls.py'))
