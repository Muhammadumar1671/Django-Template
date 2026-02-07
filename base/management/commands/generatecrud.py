"""
Generate CRUD APIs for an existing app with models.

Usage:
    python manage.py generatecrud <app_name>
    
This will scan the app's models.py and generate CRUD APIs for all models.
"""

import ast
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Generate CRUD APIs for existing app models'

    def add_arguments(self, parser):
        parser.add_argument(
            'app_name',
            type=str,
            help='Name of the app (e.g., users, products)'
        )
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='Overwrite existing files'
        )

    def handle(self, *args, **options):
        app_name = options['app_name']
        overwrite = options['overwrite']
        
        # Find app directory
        app_dir = Path('apps') / app_name
        if not app_dir.exists():
            raise CommandError(f'App "apps/{app_name}" does not exist')
        
        # Find models.py
        models_file = app_dir / 'models.py'
        if not models_file.exists():
            raise CommandError(f'models.py not found in apps/{app_name}/')
        
        self.stdout.write(self.style.SUCCESS(f'\n🚀 Generating CRUD for app: {app_name}'))
        
        # Extract models
        model_classes = self.extract_models(models_file)
        
        if not model_classes:
            raise CommandError(f'No Django models found in apps/{app_name}/models.py')
        
        self.stdout.write(self.style.SUCCESS(f'✅ Found {len(model_classes)} model(s):'))
        for model_name in model_classes.keys():
            self.stdout.write(f'   - {model_name}')
        
        # Import generation functions
        from base.management.commands.createcrud import Command as CrudCommand
        
        crud_cmd = CrudCommand()
        crud_cmd.stdout = self.stdout
        crud_cmd.style = self.style
        
        # Create directories
        crud_cmd.create_directories(app_dir)
        
        # Generate files
        crud_cmd.generate_serializers(app_dir, app_name, model_classes, overwrite)
        crud_cmd.generate_viewsets(app_dir, app_name, model_classes, overwrite)
        crud_cmd.generate_services(app_dir, app_name, model_classes, overwrite)
        crud_cmd.generate_urls(app_dir, app_name, model_classes, overwrite)
        crud_cmd.generate_admin(app_dir, app_name, model_classes, overwrite)
        
        # Add to INSTALLED_APPS if not already
        crud_cmd.add_to_installed_apps(app_name)
        
        # Add to main urls.py if not already
        crud_cmd.add_to_main_urls(app_name)
        
        self.stdout.write(self.style.SUCCESS('\n✨ CRUD generation completed!'))
        self.stdout.write(self.style.SUCCESS('✅ App configured in INSTALLED_APPS'))
        self.stdout.write(self.style.SUCCESS('✅ URLs configured'))
        self.stdout.write('\n📝 Next steps:')
        self.stdout.write(f'   1. Run migrations: python manage.py makemigrations {app_name}')
        self.stdout.write(f'   2. Run migrate: python manage.py migrate')
        self.stdout.write(f'   3. Your API is ready at: http://localhost:8000/api/{app_name}/\n')

    def extract_models(self, models_file):
        """Extract all Django model classes from models.py using AST parsing."""
        model_classes = {}
        
        try:
            with open(models_file, 'r') as f:
                tree = ast.parse(f.read(), filename=str(models_file))
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
