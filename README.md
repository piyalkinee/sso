## 🛠️ Setting Up the Environment
First, install all dependencies:

```bash
    python3 -m venv venv           # Create a virtual environment
    source venv/bin/activate       # Activate the virtual environment
    pip install poetry             # Install Poetry
    poetry install                 # Install project dependencies
```

## 🔖 Setting App Version  
To check the current version in console:
```bash
    poetry version # to check current version
    poetry version <version> # for example [poetry version 0.0.5]
```

If you want to get version in script, use next lines:
```python
import importlib.metadata
VERSION = importlib.metadata.version("source")
```