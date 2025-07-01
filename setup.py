"""Setup configuration for codebase2xml."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
if readme_path.exists():
    with open(readme_path, "r", encoding="utf-8") as fh:
        long_description = fh.read()
else:
    long_description = "Transform any codebase directory into a comprehensive XML archive"

setup(
    name="codebase2xml",
    version="1.0.0",
    author="Geo Anima",
    author_email="",
    description="Transform any codebase directory into a comprehensive XML archive",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Documentation",
        "Topic :: Text Processing :: Markup :: XML",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        # No external dependencies - uses only Python standard library
    ],
    entry_points={
        "console_scripts": [
            "codebase2xml=codebase2xml.cli:main",
        ],
    },
    keywords=[
        "codebase", "archive", "xml", "backup", "documentation", 
        "code-analysis", "project-structure", "file-tree"
    ],
    project_urls={
        "Bug Reports": "",
        "Source": "",
    },
)