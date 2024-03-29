import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="igneous",
    version="1.1.1",
    author="Rubrik Inc",
    author_email="info@igneous.io",
    description="Rubrik NAS Cloud Direct API Python SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/igneous-systems/python-igneous",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
