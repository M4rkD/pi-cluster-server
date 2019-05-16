import numpy as np
import kinectlib.kinectlib as kinect
import cluster_manager
import datetime
import calendar
from computedrag import compute_drag_for_simulation
from images_to_pdf.pdfgen import PDFPrinter
from display.matplotlib_widget import PlotCanvas
from postplotting import vtk_to_plot

from settings import nmeasurements


class Controller(object):
    def __init__(self, parent=None):

        # instance variables
        self.offset = [0, 0]
        self.scale = [1.0, 1.0]
        self.drag = cluster_manager.load_drag()
        self.current_name = 'Simulation'
        self.outline = None
        self.transformed_outline = None
        self.contour = np.array([[]])

        self.calibrate()

    def calibrate(self):
        self.background = kinect.measure_depth(nmeasurements)

    def capture(self):
        rgb, rgb_with_outline, depth, outline = kinect.images_and_outline(
            self.background,
            self.scale,
            self.offset)

        # Set as current capture images
        self.capture_frame = rgb
        self.capture_frame_with_outline = rgb_with_outline
        self.capture_depth = depth
        
        # Set contour for simulation
        self.contour = outline

        return self.capture_frame, self.capture_depth

    def get_capture_images(self):
        return self.capture_frame, self.capture_depth

    def name_changed(self, name, email):
        self.current_name = name
        self.current_email = email

    def get_user_details(self):
        return self.current_name, self.current_email

    def start_simulation(self):

        index = self.get_epoch()

        # save simulation details for later
        simulation = {
            'index': index,
            'name': self.current_name,
            'email': self.current_email,
            'rgb': self.capture_frame,
            'rgb_with_contour': self.capture_frame_with_outline,
            'depth': self.capture_depth,
            'background': self.background,
            'contour': self.contour
        }

        cluster_manager.save_simulation(simulation)

        cluster_manager.queue_run(self.contour, simulation['index'])

        return index

    def simulation_postprocess(self, index):
        drag = compute_drag_for_simulation(index)
        
        self.drag = np.append(self.drag, np.array([[index, drag]]), axis = 0)
        cluster_manager.save_drag(self.drag)

        simulation = cluster_manager.load_simulation(index)
        simulation['drag'] = drag
        cluster_manager.save_simulation(simulation)

    def print_simulation(self, index, send_to_printer = True):
        simulation = cluster_manager.load_simulation(index)
        rgb = simulation['rgb']
        depth = simulation['depth']
        rgb = simulation['rgb_with_contour']

        a = PlotCanvas()
        vtk_filename = cluster_manager.run_filepath(index, 'elmeroutput0010.vtk')
        vtk_to_plot(a, vtk_filename, 16, True, False, True, None)
        data = np.fromstring(a.tostring_rgb(), dtype=np.uint8, sep='')
        data = data.reshape(a.get_width_height()[::-1] + (3, ))

        a = PlotCanvas()
        vtk_to_plot(a, vtk_filename, 16, True,False,True,None)

        filename = str(index)+'.pdf'

        generator = PDFPrinter(filename, rgb, depth, data, data,
                                simulation['name'], simulation['drag'])
        generator.run(send_to_printer = send_to_printer)

    def best_simulations(self):
        nsims = 10
        drag = np.array(self.drag)
        drag_sorted_indices = np.argsort(drag[:, 1])
        drag_sorted_indices = np.flip(drag_sorted_indices)
        best_indices = drag[drag_sorted_indices[0:nsims], 0]

        simulations = {}
        for index in best_indices:
            simulations[index] = cluster_manager.load_simulation(index)

        return simulations

    def get_epoch(self):
        now = datetime.datetime.utcnow()
        timestamp = calendar.timegm(now.utctimetuple())
        return timestamp