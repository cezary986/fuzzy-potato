import setuptools

with open("../README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fuzzy-potato",
    version='0.0.1',
    author="Cezary Maszczyk",
    author_email="cezary.maszczyk@gmail.com",
    description="Library for string fuzzy matching",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="h",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU License",
    ],
    python_requires='>=3.6',
)