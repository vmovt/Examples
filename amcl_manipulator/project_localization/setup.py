from setuptools import setup
import os
from glob import glob

package_name = 'project_localization'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*')),
        (os.path.join('share', package_name, 'maps'), glob('maps/*')),
        (os.path.join('share', package_name, 'config'), glob('config/*.txt')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='vadim',
    maintainer_email='vadim@todo.todo',
    description='TODO: Package description',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        'spots_to_file = project_localization.spots_to_file:main',
        ],
    },
)
