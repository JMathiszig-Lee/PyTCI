import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PyTCI",
    version="0.3",
    author="Jakob Mathiszig-Lee",
    author_email="jakob@mathisziglee.co.uk",
    description="A package for target controlled infusions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JMathiszig-Lee/PyTCI",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)