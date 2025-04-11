from setuptools import setup, find_packages

setup(
    name="hr_logs",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'flask',
        'flask-login',
        'flask-sqlalchemy',
        'bcrypt',
        'email-validator',
        'gunicorn'
    ],
)
