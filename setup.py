from setuptools import setup, find_packages

setup(
    name='getref',
    version='0.1',
    description='Command line interface to dblp',
    author='Martin Isaksson',
    author_email='martin.isaksson@gmail.com',
    keywords='bibtex dblp',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'Environment :: Console'
      ],
    packages=find_packages(),
    install_requires=[
          'simple-term-menu==0.10.5',
          'Pygments==2.8.1',
          'requests==2.25.1'
    ],
    entry_points={
        'console_scripts': ['getref=getref.command_line:main'],
    },
    zip_safe=False
)
