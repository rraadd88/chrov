#!/usr/bin/env python
"""Development.

### release new version

    git commit -am "version bump";git push public main
    python setup.py --version
    git tag -a v$(python setup.py --version) -m "upgrade";git push --tags

"""

import sys
if (sys.version_info[0]) != (3):
    raise RuntimeError('Python 3 required ')

import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()
    
requirements = {
'base':[
    # "roux @ git+https://github.com/rraadd88/roux.git@master",
    "roux",
        ## requirements from roux 
        'scipy',
        'seaborn',
        'numpy>=1.17.3',
        'pandas>=0.25.3',
        'pyyaml>=5.1',
        'matplotlib>=2.2',
    ],
## development and maintenance
'dev':[
    'pytest',
    'jupyter','ipywidgets','ipykernel',
    'black',
    'coveralls == 3.*',
    'flake8',
    'isort',
    'pytest-cov == 2.*',
    'testbook',
    'papermill',
    'lazydocs', 'regex', ## docs
    # 'sphinx','recommonmark',
],
}

extras_require={k:l for k,l in requirements.items() if not k=='base'}
## all: extra except dev
extras_require['all']=[l for k,l in extras_require.items() if not k=='dev']
### flatten
extras_require['all']=[s for l in extras_require['all'] for s in l]
### unique
extras_require['all']=list(set(extras_require['all']))

# main setup command
setuptools.setup(
    name='chrov',
    version='0.0.3',
    author='Rohan Dandage',
    author_email='rohanadandage@gmail.com',
    url='https://github.com/rraadd88/chrov',
    description='chrov:',    
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='General Public License v. 3',
    packages=setuptools.find_packages('.',exclude=['test','tests', 'unit','deps','data','examples']),
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=requirements['base'],
    extras_require=extras_require,
    # entry_points={
    # 'console_scripts': ['chrov = chrov.run:parser.dispatch',],
    # },
    python_requires='>=3.7, <4',
)