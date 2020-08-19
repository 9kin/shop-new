#!/usr/bin/env python

"""The setup script."""

from setuptools import find_packages, setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

requirements = [
    "flask",
    "flask-table",  # easy html table
    "flask_admin",  # admin panel
    "flask_login",  # simple flask login
    "flask_restful",  # rest api
    "flask_wtf",  # wtforms
    "flask-wtf",
    "python-dotenv",  # .env
    "peewee",  # simple and small ORM
    "elasticsearch==7.9.0",  # we also want to improve  to version 9.x + asyncio + aiohttp + fast_indexing
    "tqdm",  # progressbar
    "sphinx_revealjs",  # TODO remove (for docs)
    "markdown",  # (rst ?)
    "flask_profiler",  # profiler
    "rich",  # cli
    "black",  # TODO remove (for lint)
    "isort",  # TODO remove (for lint)
    "wtf-peewee",  # for flask_admin
    "Click>=7.0",
]

setup_requirements = []

test_requirements = []

setup(
    author="Ivan",
    author_email="cf2html.github@mail.ru",
    python_requires=">=3.5",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="very simple and fast flask shop",
    entry_points={},
    install_requires=requirements,
    license="MIT license",
    long_description=readme,
    include_package_data=True,
    keywords="shop",
    name="shop",
    packages=find_packages(include=["shop", "shop.*"]),
    setup_requires=setup_requirements,  # TODO
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/9kin/shop",
    version="0.1.0",
    zip_safe=False,
)
