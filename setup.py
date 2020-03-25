"""Script for building the Helpik package. """

from setuptools import setup

try:
    import pypandoc

    LONG_DESCRIPTION = pypandoc.convert('README.md', 'rst')
except (ImportError, OSError):
    # OSError is raised when pandoc is not installed.
    LONG_DESCRIPTION = ('Helpik is the microservice intended for gathering synopses from '
                        'CusDeb Wiki to display them on the client.')

with open('requirements.txt') as outfile:
    REQUIREMENTS_LIST = outfile.read().splitlines()

setup(name='helpik',
      version='0.1',
      description='Helpik package',
      long_description=LONG_DESCRIPTION,
      url='https://github.com/tolstoyevsky/cusdeb-helpik',
      author='Dmitry Ivanko <tmwsls12@gmail.com>, Vladislav Yarovoy <vlad_yarovoy_97@mail.ru>, '
             'Evgeny Golyshev <eugulixes@gmail.com>',
      maintainer='Dmitry Ivanko',
      maintainer_email='Dmitry Ivanko <tmwsls12@gmail.com>',
      license='http://www.apache.org/licenses/LICENSE-2.0',
      scripts=['bin/server.py'],
      packages=['helpik'],
      include_package_data=True,
      data_files=[('', ['requirements.txt', 'LICENSE'])],
      install_requires=REQUIREMENTS_LIST)
