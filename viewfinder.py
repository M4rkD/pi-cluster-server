from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import cv2, sys, time, os
import numpy as np
from leaderboard import LeaderboardWidget
from video_capture import QVideoWidget
from pyside_dynamic import loadUiWidget
from activity_monitor import ActivityPlotter
from matplotlib_widget import PlotCanvas
from postplotting import vtk_to_plot
from cluster_run import get_run_completion_percentage, run_filepath

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))


class ViewfinderDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = loadUiWidget(
            os.path.join(SCRIPT_DIRECTORY, 'designer/viewfinder.ui'),
            customWidgets=[
                QVideoWidget, LeaderboardWidget, ActivityPlotter, PlotCanvas
            ])
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.ui)

        self.image_index = 0
        self.run_queue = []
        self.currently_shown_simulation = None

        # cycle simulation image every 5ms seconds (for video effect)
        timer = QTimer(self)
        timer.timeout.connect(self.update_simulation_views)
        timer.start(5)

        self.progress_slots = [self.ui.slot1, self.ui.slot2, self.ui.slot3]
        self.indices_in_slots = [None, None, None]

    def switch_stack(self, index):
        self.ui.leftStack.setCurrentIndex(index)
        self.ui.rightStack.setCurrentIndex(index)

    def set_current_simulation_index(self, index):
        self.current_simulation_index = index
        self.image_index = 0
        self.update_simulation_views()
        self.switch_stack(1)

    def switch_to_viewfinder(self):
        self.switch_stack(0)

    def switch_to_simulation_view(self, simulation):
        self.currently_shown_simulation = simulation
        self.update_simulation_views()
        self.switch_stack(1)

    def update_simulation_views(self):
        ntimesteps = 10
        if self.ui.leftStack.currentIndex() == 0:
            return

        # clear screen
        self.ui.left_view.figure.clear()
        self.ui.right_view.figure.clear()

        if not self.currently_shown_simulation is None:
            image = self.currently_shown_simulation['rgb']
            vtk_file = run_filepath(self.currently_shown_simulation['index'],
                                    f'elmeroutput{self.image_index:04}.vtk')

            if self.image_index > 0:
                vtk_to_plot(self.ui.left_view, vtk_file, 1, False, True, False,
                            image)
                vtk_to_plot(self.ui.right_view, vtk_file, 1, True, False, True,
                            None)

            self.image_index = (self.image_index + 1) % (ntimesteps + 1)

    def set_currently_shown_simulation(self, index):
        datafile = run_filepath(index, 'simulation.npy')
        self.currently_shown_simulation = np.load(datafile)

    def set_progress(self, index_run, progress):
        slot_number = self.indices_in_slots.index(index_run)
        self.progress_slots[slot_number].setValue(progress)

    def queue_simulation(self, index_run, name):
        self.run_queue.append((index_run, name))
        self.update_queue()

    def update_queue(self):
        text = 'Queue: ' + ', '.join([q[1] for q in self.run_queue])
        self.ui.queue.setText(text)

    def start_simulation(self, index_run, slot):
        # remove from queue
        names = [q[1] for q in self.run_queue]
        run_indices = [q[0] for q in self.run_queue]
        i = run_indices.index(index_run)
        name = names[i]

        del self.run_queue[i]
        self.update_queue()

        # move from queue to progress + reset progress
        pbar = self.progress_slots[slot]
        pbar.setValue(0)
        pbar.setFormat(f'{name} : %p%')
        self.indices_in_slots[slot] = index_run

    def finish_simulation(self, index_run):
        slot_number = self.indices_in_slots.index(index_run)
        pbar = self.progress_slots[slot_number]
        pbar.setValue(0)
        self.indices_in_slots[slot_number] = None
        pbar.setFormat('Idle')

    def start_progress_checking(self):
        # check for progress every 10 seconds
        progress_timer = QTimer(self)
        progress_timer.timeout.connect(self.update_progress)
        progress_timer.start(10000)

    def update_progress(self):
        print('checking progress')
        for index in self.indices_in_slots:
            percent = get_run_completion_percentage(index)
            self.set_progress(index, percent)


def main():
    app = QApplication(sys.argv)
    window = ViewfinderDialog()

    def finish_simulation():
        window.finish_simulation(15)
        window.finish_simulation(25)

    def update_progress():
        window.set_progress(15, 50)
        window.set_progress(25, 75)
        QTimer.singleShot(1000, finish_simulation)

    def start_simulation():
        window.start_simulation(15, 1)
        window.start_simulation(25, 2)
        QTimer.singleShot(1000, update_progress)

    def queue_simulation():
        window.queue_simulation(15, 'My Name')
        window.queue_simulation(25, 'Another Name')
        QTimer.singleShot(1000, start_simulation)

    QTimer.singleShot(1000, queue_simulation)
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
