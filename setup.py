from setuptools import setup, find_packages

version = '0.1.dev1'

setup(
    name='pyash',
    version=version,
    description="A tool to manage simple accounting from a plain text file.",
    long_description=open('README.rst').read(),
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Programming Language :: Unix Shell',
        'Programming Language :: Python :: 3',
    ],
    keywords='',
    author='AFPy Team',
    author_email='tresorerie@afpy.org',
    url='https://github.com/AFPy/pyash/',
    license='MIT',
    packages=find_packages(),
    package_data={'pyash.tests': ['*.dat']},
    zip_safe=False,
    install_requires=['chut', 'jinja2'],
    entry_points={'console_scripts': ['pyash = pyash:pyash']}
)
