from setuptools import setup, find_packages

setup(
    name = "y",
    version = "0.1",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=["ply", "pytz"],
    entry_points = {
        'console_scripts': [
            'y = y:main',
        ],
    }
)

