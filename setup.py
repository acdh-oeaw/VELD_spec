from setuptools import setup

setup(
    name="veld_spec",
    version="0.1.31",
    author="Stefan Resch",
    author_email="stefan.resch@oeaw.ac.at",
    description="VELD specification",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/acdh-oeaw/VELD_spec",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=["PyYAML>=6.0.2"],
    packages=["veld_spec"],
    package_data={"veld_spec": ["README.md"]},
)
