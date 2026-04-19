from setuptools import setup, find_packages

setup(
    name="envoy-cli",
    version="0.1.0",
    description="A lightweight CLI for managing and syncing .env files with encryption support.",
    author="envoy contributors",
    packages=find_packages(exclude=["tests*"]),
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0",
        "cryptography>=41.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "envoy=envoy.cli:cli",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: Utilities",
    ],
)
