from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='simvestr',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'flask-sqlalchemy',
        'flask-restx',
        'pyjwt',
        'openpyxl',
        'pandas'
    ],
    author="Jihad Meraachli; Khan Schroder-Turner; Kovid Sharma; Simon Garrod; Timothy Brunette",
    author_email="simvestr@gmail.com",
    description="A small example package",
    url='https://github.com/unsw-cse-capstone-project/comp9900-w17a-please-get-degrees-backend',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)