import os
from setuptools import setup, find_packages
from acl_webapp import __author__, __version__


def __read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return ''


install_requires = __read('requirements.txt').split('\n')

setup(
    name='acl_webapp',
    author=__author__,
    author_email='alexevseev@gmail.com',
    version=__version__,
    description='Web application with permissions (ACL), '
    'built with tornado, mongodb, motor',
    long_description=__read('README.rst'),
    platforms=('Any'),
    packages=find_packages(),
    install_requires="",  # TODO: check, why tox fails with install_requires
    keywords='tornado mongodb motor async acl example'.split(),
    include_package_data=True,
    license='BSD License',
    package_dir={'acl_webapp': 'acl_webapp'},
    url='/mnt/dev/python_2dbit/test_work_secondary/acl_webapp/',
    # url='https://github.com/st4lk/acl_webapp',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Tornado',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ],
)
