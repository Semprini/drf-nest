import os
import setuptools


def find_packages(srcdir):
    package_list = []
    badnames = ["__pycache__", "venv", ]
    for root, dirs, files in os.walk(srcdir):
        if not any(bad in root for bad in badnames):
            if "__init__.py" in files:
                package_list.append(root.replace("/", ".").replace("\\", ".").strip('.'))
    return package_list


packages = find_packages('./drf_nest')

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(name='drf_nest',
                 version='0.1a3',
                 packages=["drf_nest", ] + packages,
                 author='Semprini',
                 description='Django rest framework extension to handle writable nested fields',
                 long_description=long_description,
                 long_description_content_type='text/markdown',
                 url='https://github.com/Semprini/drf-nest',
                 package_data={'': ['README.md'], 'drf_nest': ['templates/admin/*.html', ]},
                 classifiers=[
                     "Programming Language :: Python :: 3",
                     "License :: OSI Approved :: GNU General Public License (GPL)",
                     "Operating System :: OS Independent",
                 ],
                 install_requires=[
                     "django>=3",
                     "djangorestframework>=3.7.7",
                     "django-filter>=0.15.3",
                 ],
                 python_requires='>=3.7',
                 )
