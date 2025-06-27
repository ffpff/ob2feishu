#!/usr/bin/env python3
"""
Obsidian到飞书知识库同步工具
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ob2feishu",
    version="0.1.0",
    author="Obsidian2Feishu Team",
    author_email="",
    description="将Obsidian笔记同步到飞书知识库的工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/ob2feishu",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "ob2feishu=ob2feishu.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
) 