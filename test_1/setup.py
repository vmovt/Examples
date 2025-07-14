from setuptools import find_packages, setup

package_name = 'test_1'
data_files = []
data_files.append(('share/ament_index/resource_index/packages', ['resource/' + package_name]))
data_files.append(('share/' + package_name + '/launch', ['launch/robot_launch.py']))
data_files.append(('share/' + package_name + '/worlds', ['worlds/my_world_new.wbt']))
data_files.append(('share/' + package_name + '/resource', ['resource/my_robot.urdf']))
data_files.append(('share/' + package_name + '/config', ['config/pointcloud_to_laserscan_params.yaml']))
data_files.append(('share/' + package_name + '/config', ['config/diff_drive_controller.yaml']))
data_files.append(('share/' + package_name, ['package.xml']))


setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=data_files,
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='vadim',
    maintainer_email='vadim@todo.todo',
    description='TODO: Package description',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'my_robot_driver = test_1.my_robot_driver:main',
            'clock_publisher = test_1.clock_publisher:main',
            'smach = test_1.smach:main',
            'camera_node= test_1.camera_node:main',
        ],
    },
)
