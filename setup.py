from setuptools import find_packages, setup

setup(
    name='coronalms',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'flask-wtf',
        'Flask-FontAwesome',
        'flask-login',
        'flask-migrate',
        'flask-sqlalchemy',
        'flask_bootstrap',
        'flask-markdown',
        'flask-pagedown',
        'babel'
    ],
)