import os
import re

def fix_imports(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace "from backend.X import Y" with "from X import Y"
    new_content = re.sub(r'^(\s*)from backend\.', r'\1from ', content, flags=re.MULTILINE)
    # Replace "import backend.X" with "import X"
    new_content = re.sub(r'^(\s*)import backend\.', r'\1import ', content, flags=re.MULTILINE)
    
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {file_path}")

def main():
    backend_dir = os.path.abspath(os.path.dirname(__file__))
    
    exclude_dirs = ['venv', '.pytest_cache', '__pycache__', 'qdrant_storage', '.git']

    for root, dirs, files in os.walk(backend_dir):
        # Filter dirs
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        # Ensure __init__.py exists
        init_file = os.path.join(root, '__init__.py')
        if not os.path.exists(init_file) and root != backend_dir:
            try:
                with open(init_file, 'w') as f:
                    pass
                print(f"Created {init_file}")
            except Exception as e:
                pass

        for file in files:
            if file.endswith('.py') and file != 'fix_imports.py':
                fix_imports(os.path.join(root, file))

if __name__ == '__main__':
    main()
