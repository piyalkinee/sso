from setuptools import setup, find_packages

with open("VERSION_SSO", "r") as f:
    VERSION = f.readlines()[0]

setup(
    name="ssosource",
    version=VERSION,
    packages=find_packages(),
    python_requires='>=3.12',
    install_requires=[
        'fastapi==0.115.0',
        'loguru==0.7.2',
        'setproctitle==1.3.3',
        'gunicorn==23.0.0',
        'uvicorn==0.30.6',
        'databases==0.9.0',
        'asyncpg==0.29.0',
        'alembic==1.13.3',
        'python-dotenv==1.0.1',
        'psycopg2-binary==2.9.9',
        'bcrypt==4.2.0',
        'python-jose[cryptography]==3.3.0',
        'greenlet==3.1.1',
        'httpx==0.27.0',
        'google-auth==2.29.0',
        'requests>=2.31.0',
    ],
    extras_require={
        'test': [
            'pytest==8.3.3',
            'pytest-asyncio==0.24.0',
            'pytest-mock==3.14.0',
        ]
    },
)