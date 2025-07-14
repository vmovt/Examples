import rclpy
import math
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np
from ultralytics import YOLO
from std_msgs.msg import Float32, Int32, String
from geometry_msgs.msg import Point
import time

YOLO_MODEL_PATH = "/home/vadim/ros2_ws/src/test_1/best3.pt"
CUBE_SIZE = 0.05

class Camera_node(Node):
  def __init__(self):
    super().__init__('camera_node')
    self.bridge = CvBridge()
    self.subscription = self.create_subscription(Image, '/camera/image_color', self.listener_callback, 10)
    self.create_subscription(String, 'need_colour', self.need_colour_callback, 1)
    self.create_subscription(Int32, 'camera_on', self.camera_on_callback, 1)

    self.__publisher_float = self.create_publisher(Float32, 'rot_err', 1)
    self.__publisher_int = self.create_publisher(Int32, 'wait_camera', 1)
    self.__publisher_green = self.create_publisher(String, 'green_detected', 1)
    self.__publisher_xyz = self.create_publisher(Point, 'xyz', 1)
    self.__publisher_xyz_send = self.create_publisher(Int32, 'xyz_send', 1)

    self.need_colour_ = None
    self.camera_on_ = 0
    self.cv2_window_created = False
    self.window_name = "Image from Webots with YOLOv8 detections"

    self.flag_on = 1

    try:
      self.model = YOLO(YOLO_MODEL_PATH)
      self.model.conf = 0.2
      self.model.iou = 0.6
      self.get_logger().info("YOLO model loaded successfully.")
    except Exception as e:
      self.get_logger().error(f"Error loading YOLO model: {e}")
      self.model = None

  def need_colour_callback(self, msg):
    self.need_colour_ = msg.data

  def camera_on_callback(self, msg):
    self.camera_on_ = msg.data
    if self.camera_on_ == 0 and self.cv2_window_created:
        cv2.destroyWindow(self.window_name)
        self.cv2_window_created = False

  def listener_callback(self, msg):
    if self.camera_on_ != 1:
        if self.cv2_window_created:
            cv2.destroyWindow(self.window_name)
            self.cv2_window_created = False
        return

    if not self.cv2_window_created:
      cv2.namedWindow(self.window_name)
      self.cv2_window_created = True

    try:
      cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
      image_height, image_width = cv_image.shape[:2]
      image_center_x = image_width // 2
      image_center_y = image_height // 2

      err = Float32()
      err.data = 1.0

      if self.model:
        results = self.model(cv_image)
        annotated_image = cv_image.copy()

        for *xyxy, conf, cls in results[0].boxes.data.tolist():
          x1, y1, x2, y2 = [round(float(x), 2) for x in xyxy]
          #self.get_logger().info(f"Найден объект: {results[0].names[int(cls)]}, уверенность: {conf:.2f}")

          if conf >= 0.2:
            label = f'{results[0].names[int(cls)]} {conf:.2f}'
            cv2.rectangle(annotated_image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

            if results[0].names[int(cls)] == "green-cube":
              colour_wait = String()
              colour_wait.data = "GREEN"
              self.__publisher_green.publish(colour_wait)

              if self.need_colour_ == "GREEN":
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2

                offset_x = center_x - image_center_x
                offset_y = center_y - image_center_y

                xyz = Point()
                xyz.x = (offset_x / (image_width / 2)) * 0.414
                xyz.y = (offset_y / (image_height / 2)) * 0.414
                xyz.z = 0.18
                

                pre_xyz = Point()
                pre_xyz.x = xyz.x / 1.5
                pre_xyz.y = xyz.y / 1.5
                pre_xyz.z = xyz.z * 1.5

                self.__publisher_xyz.publish(pre_xyz)
                time.sleep(1)

                self.__publisher_xyz.publish(xyz)
                time.sleep(1)
                xyz_send = Int32()
                xyz_send.data = 1
                self.__publisher_xyz_send.publish(xyz_send)
                self.need_colour_ = " "

            if results[0].names[int(cls)] == "blue-cube":
              if self.need_colour_ == "WHITE":
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2

                offset_x = center_x - image_center_x
                offset_y = center_y - image_center_y

                xyz = Point()
                xyz.x = (offset_x / (image_width / 2)) * 0.414
                xyz.y = (offset_y / (image_height / 2)) * 0.414
                xyz.z = 0.18
                

                #pre_xyz = Point()
                #pre_xyz.x = xyz.x / 1.5
                #pre_xyz.y = xyz.y / 1.5
                #pre_xyz.z = xyz.z * 1.5

                #self.__publisher_xyz.publish(pre_xyz)
                #time.sleep(1)


                self.__publisher_xyz.publish(xyz)
                time.sleep(1)
                xyz_send = Int32()
                xyz_send.data = 1
                self.__publisher_xyz_send.publish(xyz_send)

                self.need_colour_ = " "

                cv2.destroyWindow(self.window_name)
                self.flag_on = 0

        if self.cv2_window_created and cv2.getWindowProperty(self.window_name, cv2.WND_PROP_VISIBLE) >= 0:
          msg_wait = Int32()
          msg_wait.data = 1
          self.__publisher_int.publish(msg_wait)
        
        if self.flag_on == 1:
          cv2.imshow(self.window_name, annotated_image)
      else:
        if self.flag_on == 1:
          cv2.imshow("Image from Webots", cv_image)

      if self.flag_on == 1:
        self.__publisher_float.publish(err)
        cv2.waitKey(1)

    except Exception as e:
      self.get_logger().error(f'Error processing image: {e}')


def main(args=None):
  rclpy.init(args=args)
  node = Camera_node()
  rclpy.spin(node)
  node.destroy_node()
  rclpy.shutdown()


if __name__ == '__main__':
  main()