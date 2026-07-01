from setuptools import setup
import os
from glob import glob

package_name = 'lab7_kalman'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*'))),
        (os.path.join('share', package_name, 'config'), glob(os.path.join('config', '*.yaml'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='nvm',
    maintainer_email='nvm@todo.todo',
    description='Laboratorio 7: Localización y Filtro de Kalman',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'infrared = lab7_kalman.infrared:main',
            'kalman_1d = lab7_kalman.kalman_1d:main',
            'move3x2y = lab7_kalman.move3x2y:main',
            'trackTruthPose = lab7_kalman.trackTruthPose:main',
            'plot_filtered = lab7_kalman.plot_filtered:main',
        ],
    },
)
