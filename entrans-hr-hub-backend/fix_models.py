import os

models_dir = 'apps/hr_management/models'
for f in os.listdir(models_dir):
    if f.endswith('.py') and f != '__init__.py':
        filepath = os.path.join(models_dir, f)
        with open(filepath, 'r') as file:
            content = file.read()
        if 'app_label = "hr_management"' not in content and "app_label = 'hr_management'" not in content:
            content = content.replace('class Meta:', 'class Meta:\n        app_label = "hr_management"')
            with open(filepath, 'w') as file:
                file.write(content)
