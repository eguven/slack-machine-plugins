import os
import sys

from shutil import rmtree
from setuptools import find_packages, setup, Command

from machine_plugins import __meta__ as meta

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md')) as f:
    long_description = f.read()


class PublishCommand(Command):
    """
    Support setup.py publish.
    Graciously taken from https://github.com/kennethreitz/setup.py
    """

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def _remove_builds(self, msg):
        self.status(msg)
        for subdir in ['dist', 'build', '.egg', 'slack_machine_plugins.egg-info']:
            try:
                rmtree(os.path.join(here, subdir))
            except FileNotFoundError:
                pass

    def run(self):
        try:
            self._remove_builds('Removing previous builds…')
        except FileNotFoundError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system('{0} setup.py sdist bdist_wheel'.format(sys.executable))

        self.status('Uploading the package to PyPi via Twine…')
        os.system('twine upload dist/*')

        self._remove_builds('Removing builds…')
        sys.exit()


setup(
    name=meta.__title__,
    version=meta.__version__,
    description=meta.__description__,
    long_description=long_description,
    long_description_content_type='text/markdown',
    license=meta.__license__,
    url=meta.__url__,
    author=meta.__author__,
    tests_require=['pytest', 'pytest-cov', 'coverage'],
    install_requires=[],
    python_requires='~=3.8',  # haven't tested anything else
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Communications :: Chat',
        'Topic :: Internet',
        'Topic :: Office/Business',
    ],
    keywords='slack bot framework ai utilities',
    packages=find_packages(),
    cmdclass={
        'publish': PublishCommand,
    },
)
