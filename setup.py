from setuptools import setup, find_packages

setup(
    name="KvickStore",
    version="0.0.1",
    author="Rishabh Mediratta",
    author_email="panicpark60@gmail.com",
    version="{{VERSION_PLACEHOLDER}}",
    url="https://github.com/rm206/KvickStore",
    download_url="https://github.com/rm206/KvickStore/archive/refs/tags/v0.0.1.tar.gz",
    description="A quick and simple key-value store for Python applications",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/rm206/KvickStore",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",  # Indicates package is pre-production
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
