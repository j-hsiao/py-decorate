from setuptools import setup
from jhsiao.namespace import make_ns
make_ns('jhsiao')
setup(
    name='jhsiao-decorate',
    version='0.0.1',
    author='Jason Hsiao',
    author_email='oaishnosaj@gmail.com',
    description='Various decorators.',
    packages=['jhsiao', 'jhsiao.decorate'],
    install_requires=['jhsiao-utils @ git+https://github.com/j-hsiao/py-utils.git']
)
