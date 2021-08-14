import setuptools
from pkg_resources import parse_requirements

with open("requirements.txt") as f:
    requirements = [str(r) for r in parse_requirements(f)]

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="django-user-email-extension",
    version="2.2.4",
    author="Arie Lev",
    author_email="levinson.arie@gmail.com",
    description="User model extender for django",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ArieLevs/Django-User-Email-Extension",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Framework :: Django :: 3.0",
    ],
)
