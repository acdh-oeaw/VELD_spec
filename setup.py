from setuptools import setup, find_packages

setup(
    name="VeldSpec",
    version="0.1.1",
    author="Stefan Resch",
    author_email="stefan.resch@oeaw.aca.t",
    description="VELD specification",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/acdh-oeaw/VELD_spec",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "PyYAML>=6.0.2",
        "jsonschema>=4.23.0",
    ],
)

