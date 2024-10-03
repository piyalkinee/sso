from setuptools import setup, find_packages

with open("VERSION_SSO", "r") as f:
    VERSION = f.readlines()[0]

setup(
    name="qrmenusource",
    version=VERSION,
    packages=find_packages(),
    python_requires='>=3.12',
    install_requires=[
        'fastapi==0.112.1',
        'loguru==0.7.2',
        'setproctitle==1.3.3',
        'gunicorn==23.0.0',
        'uvicorn==0.30.6',
        'databases==0.9.0',
        'asyncpg==0.29.0',
        'alembic==1.13.2',
        'python-dotenv==1.0.1',
        'psycopg2-binary==2.9.9',
        'bcrypt==4.2.0',
        'python-jose[cryptography]==3.3.0'
    ],
)