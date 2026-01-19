from setuptools import setup, find_packages

setup(
    name="medical-telegram-warehouse",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.114.0",
        "uvicorn[standard]==0.29.0",
        "sqlalchemy==2.0.28",
        "asyncpg==0.29.0",
        "pydantic==2.6.1",
        "python-dotenv==1.0.0",
        "pytest==8.0.0",
        "pytest-asyncio==0.23.2",
        "httpx==0.27.0",
    ],
)
