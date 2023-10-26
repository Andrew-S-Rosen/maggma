#!/usr/bin/env python


from pathlib import Path

from setuptools import find_packages, setup

module_dir = Path(__file__).resolve().parent

with open(module_dir / "README.md") as f:
    long_desc = f.read()
setup(
    name="maggma",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    description="Framework to develop datapipelines from files on disk to full dissemination API",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    url="https://github.com/materialsproject/maggma",
    author="The Materials Project",
    author_email="feedback@materialsproject.org",
    license="modified BSD",
    packages=find_packages("src"),
    package_dir={"": "src"},
    package_data={"maggma": ["py.typed"]},
    zip_safe=False,
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "setuptools",
        "ruamel.yaml<0.18",
        "pydantic>=2.0",
        "pydantic-settings>=2.0.3",
        "pymongo>=4.2.0",
        "monty>=2023.9.25",
        "mongomock>=3.10.0",
        "pydash>=4.1.0",
        "jsonschema>=3.1.1",
        "tqdm>=4.19.6",
        "mongogrant>=0.3.1",
        "aioitertools>=0.5.1",
        "numpy>=1.17.3",
        "fastapi>=0.42.0",
        "pyzmq>=24.0.1",
        "dnspython>=1.16.0",
        "sshtunnel>=0.1.5",
        "msgpack>=0.5.6",
        "orjson>=3.9.0",
        "boto3>=1.20.41",
        "python-dateutil>=2.8.2",
        "uvicorn>=0.18.3",
    ],
    extras_require={
        "vault": ["hvac>=0.9.5"],
        "memray": ["memray>=1.7.0"],
        "montydb": ["montydb>=2.3.12"],
        "notebook_runner": ["IPython>=8.11", "nbformat>=5.0", "regex>=2020.6"],
        "azure": ["azure-storage-blob>=12.16.0", "azure-identity>=1.12.0"],
        "testing": [
            "pytest",
            "pytest-cov",
            "pytest-mock",
            "pytest-asyncio",
            "pytest-xdist",
            "pre-commit",
            "moto",
            "ruff",
            "responses<0.22.0",
            "types-pyYAML",
            "types-setuptools",
            "types-python-dateutil",
            "starlette[full]",
        ],
        "docs": [
            "mkdocs>=1.4.0",
            "mkdocs-material>=8.3.9",
            "mkdocs-minify-plugin>=0.5.0",
            "mkdocstrings[python]>=0.18.1",
            "jinja2<3.2.0",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Information Technology",
        "Operating System :: OS Independent",
        "Topic :: Other/Nonlisted Topic",
        "Topic :: Database :: Front-Ends",
        "Topic :: Scientific/Engineering",
    ],
    entry_points={"console_scripts": ["mrun = maggma.cli:run"]},
)
