from setuptools import setup, find_packages

setup(
    name="auth_service",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "python-jose[cryptography]",
        "passlib[bcrypt]",
        "python-multipart",
        "motor",
    ],
) 