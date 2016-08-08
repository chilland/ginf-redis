try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension

config = {
    'description': 'ginf-redis - redis based implementation of HRL geoinference algorithm',
    'author': 'Ben Johnson',
    'e-mail': 'ben@gophronesis.com',
    'version': '0.0.1',
    'install_requires': ['Flask==0.10.1', 'Flask-RESTful==0.3.5', 'tornado==4.1',
                         'redis==2.10.5', 'redis-py-cluster==1.2.0'],
    'packages': ['ginf'],
    'name': 'ginf'
}

setup(**config)
