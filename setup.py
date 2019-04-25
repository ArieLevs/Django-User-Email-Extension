import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="django-user-email-extension",
    version="1.0.8",
    author="Arie Lev",
    author_email="levinson.arie@gmail.com",
    description="User model extender for django",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ArieLevs/Django-User-Email-Extension",
    packages=setuptools.find_packages(),
    install_requires=['django>=2.1.7'],
    classifiers=(
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Framework :: Django :: 2.1",
    ),
)
