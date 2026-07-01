import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'autlab7'

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
    ] + package_files('urdf') + package_files('models') + package_files('worlds') + package_files('config') + package_files('launch'), 
    install_requires=['setuptools'],

    zip_safe=True,
    maintainer='alex',
    maintainer_email='alex@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'infrared = autlab7.infrared:main',
            'move3x2 = autlab7.move3x2:main',
            'record_trajectories = autlab7.record_trajectories:main',
            'move_and_record = autlab7.move_and_record:main',
            'ekf_odom = autlab7.ekf_odom:main',
            'ukf_odom = autlab7.ukf_odom:main',
            'ekf_odom_imu = autlab7.ekf_odom_imu:main',
            'ukf_odom_imu = autlab7.ukf_odom_imu:main',
        ],
    },
)
