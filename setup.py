from setuptools import setup, find_packages


setup(
    name="wave-alarm",  # Name of the package
    packages=find_packages(),  # Automatically find all packages in the directory
    install_requires=[  # List of dependencies
        'pandas',
        'requests',
        'python-dotenv',
        'datetime',
        'dotenv',
        'streamlit',
        'ipython',
        'ipykernel'
    ],
    include_package_data=True,  # Include other files such as .env if necessary
)