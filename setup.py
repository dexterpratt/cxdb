import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cxdb",
    version="0.1.1",
    author="CXDB Developers",
    author_email="author@example.com",
    description="A lightweight, in-memory graph database that supports basic Cypher operations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/cxdb",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pandas",
        "ndex2",
        "ply",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "flake8",
        ],
    },
)