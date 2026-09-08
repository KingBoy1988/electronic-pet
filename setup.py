from setuptools import setup, find_packages

setup(
    name="electronic-pet",
    version="1.0.0",
    description="A desktop electronic pet application built with Python and PySide6",
    author="KingBoy1988",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "PySide6>=6.5.0",
    ],
    entry_points={
        "console_scripts": [
            "electronic-pet=main:main",
        ],
    },
    python_requires=">=3.8",
)
