import numpy as np
import kinectlib.kinectlib as kinect
import simulation_proxy
import matplotlib.pyplot as plt
import cv2

from settings import nmeasurements


class Controller(object):
    def __init__(self, parent=None):

        # instance variables
        self.offset = [0, 5]
        self.scale = [1.0, 1.0]
        self.current_name = 'Simulation'
        self.current_email = ''
        self.outline = None
        self.transformed_outline = None
        self.contour = np.array([[]])
        self.capture_frame = None
        self.capture_depth = None

        self.calibrate()

    def calibrate(self):
        self.background = kinect.measure_depth(nmeasurements)

    def capture(self):
        rgb, rgb_with_outline, depth, outline = kinect.images_and_outline(
            self.background, self.scale, self.offset)

        # Set as current capture images
        self.capture_frame = rgb
        self.capture_frame_with_outline = rgb_with_outline
        self.capture_depth = depth

        # Set contour for simulation
        self.contour = outline

        return self.capture_frame, self.capture_depth

    def capture_and_show(self):
        self.capture()
        plt.imshow(self.capture_depth)
        plt.show()

    def get_capture_images(self):
        return self.capture_frame, self.capture_depth

    def set_user_details(self, name, email):
        self.current_name = name
        self.current_email = email

    def get_user_details(self):
        return self.current_name, self.current_email

    def start_simulation(self):

        # If no capture frame, then capture one before submitting
        if self.capture_frame is None:
            self.capture()

        index = simulation_proxy.dispatch({
            'name': self.current_name,
            'email': self.current_email,
            'rgb': self.capture_frame,
            'rgb_with_contour': self.capture_frame_with_outline,
            'depth': self.capture_depth,
            'background': self.background,
            'contour': self.contour
        })

        return index

    def best_simulations(self):
        nsims = 10
        return simulation_proxy.best_simulations(nsims)

    def list_simulations(self):
        return simulation_proxy.all_available_indices_and_names()

    def get_activity(self):
        return simulation_proxy.fetch_activity()

    def get_simulation(self, index):
        return simulation_proxy.load_simulation(index)

    def get_simulation_name(self, index):
        return simulation_proxy.load_simulation_name(index)

    def get_completion_percentage(self, index):
        return simulation_proxy.get_run_completion_percentage(index)

    def get_rgb_image_with_scaled_contour(self, rgb_frame):
        contour = kinect.scale_and_translate_contour(self.contour, self.scale,
                                                     self.offset)

        rgb_with_contour = rgb_frame.copy()

        cv2.drawContours(rgb_with_contour, [contour], -1, (0, 0, 255), 2)

        return rgb_with_contour

    def get_motion(self, large):
        return 10 if large else 1

    def move_offset_up(self, large=False):
        self.offset[1] -= self.get_motion(large)

    def move_offset_down(self, large=False):
        self.offset[1] += self.get_motion(large)

    def move_offset_left(self, large=False):
        self.offset[0] -= self.get_motion(large)

    def move_offset_right(self, large=False):
        self.offset[0] += self.get_motion(large)

    def scale_up(self, value):
        self.scale[0] += value
        self.scale[1] += value

    def scale_down(self, value):
        self.scale[0] -= value
        self.scale[1] -= value
