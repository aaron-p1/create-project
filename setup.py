from setuptools import setup, find_packages

setup(
    name='create-project',
    version='0.1.1',
    install_requires=[
        'pyyaml',
        'inquirer'
    ],
    packages=find_packages(),
    package_data={
        'create_project': [
            'definitions/**',
            'definitions/**/.*',
            'templates/**',
            'templates/**/.*'
        ]
    },
    entry_points={
        'console_scripts': [
            'create-project = create_project:main',
        ],
    },
)
