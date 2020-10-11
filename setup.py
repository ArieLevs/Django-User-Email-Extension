import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="django-user-email-extension",
    version="2.1.2",
    author="Arie Lev",
    author_email="levinson.arie@gmail.com",
    description="User model extender for django",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ArieLevs/Django-User-Email-Extension",
    packages=setuptools.find_packages(),
    install_requires=[
        # pytz is already part of django
        # 'pytz==2020.1',

        'django>=3.0.7',
        'django-countries==6.1.2',

        # needed by django-phonenumber-field
        'phonenumbers==8.12.2',
        'django-phonenumber-field==4.0.0',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Framework :: Django :: 3.0",
    ],
)
