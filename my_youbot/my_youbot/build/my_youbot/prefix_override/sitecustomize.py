import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/vadim/ros2_ws/src/my_youbot/install/my_youbot'
