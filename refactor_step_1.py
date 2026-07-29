import os
import shutil

base_dir = "/home/pranav/Desktop/IntelliGaurd/backend/agents/security_agent"

def main():
    # 1. Update tests to point to the new location of schemas
    test_api_path = os.path.join(base_dir, "tests", "test_api.py")
    if os.path.exists(test_api_path):
        with open(test_api_path, "r") as f:
            content = f.read()
        content = content.replace("agents.security_agent.schemas", "backend.shared.models.communication")
        with open(test_api_path, "w") as f:
            f.write(content)
            
    # Delete schemas.py since we moved it
    schemas_path = os.path.join(base_dir, "schemas.py")
    if os.path.exists(schemas_path):
        os.remove(schemas_path)

if __name__ == "__main__":
    main()
