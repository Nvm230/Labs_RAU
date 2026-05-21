import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'autlab3'

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            file_path = os.path.join(path, filename)
            install_path = os.path.join('share', package_name, path)
            paths.append((install_path, [file_path]))
    return paths

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
    ('share/ament_index/resource_index/packages',
        ['resource/' + package_name]),
    ('share/' + package_name, ['package.xml']),
    ] + package_files('urdf') + package_files('models') + package_files('worlds') + package_files('launch'), 
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='alex',
    maintainer_email='jlopezm@utec.edu.pe',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
        	'show_image = autlab3.show_image:main',
        ],
    },
)
