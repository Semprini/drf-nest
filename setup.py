import os

from distutils.core import setup

def find_packages(srcdir):
    package_list = []
    badnames=["__pycache__",]
    #goodnames=[".html",]
    
    for root, dirs, files in os.walk(srcdir):
        if not any(bad in root for bad in badnames):
            if "__init__.py" in files:# or any(s for s in files if any(xs in s for xs in goodnames)):
                package_list.append( root.replace("/",".").replace("\\",".").strip('.') )
    return package_list

packages = find_packages('drf_nest/')

setup(name='drf_nest',
    version='0.1-alpha',
    packages=packages,
    package_data={'':['README.md'], 'drf_nest': ['templates/*.html',]},
)
