import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QLineEdit
from PyQt5.QtCore import Qt

class BlackmanPulseGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("STIRAP Blackman Pulse")
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()

        plots_layout = QVBoxLayout()

        self.canvas1 = FigureCanvas(plt.figure(figsize=(6, 4)))  # Adjust the figure size
        self.canvas2 = FigureCanvas(plt.figure(figsize=(6, 4)))  # Adjust the figure size

        plots_layout.addWidget(self.canvas1)
        plots_layout.addWidget(self.canvas2)

        self.ax1 = self.canvas1.figure.add_subplot(1, 1, 1)
        self.ax2 = self.canvas2.figure.add_subplot(1, 1, 1)

        main_layout.addLayout(plots_layout)

        controls_layout = QVBoxLayout()

        control_label = QLabel("Blackman Pulse Parameters")
        controls_layout.addWidget(control_label, alignment=Qt.AlignCenter)

        self.parameter_layout1 = QVBoxLayout()
        self.parameter_layout2 = QVBoxLayout()

        parameter_labels = ["Amplitude:", "Center:", "Width:"]
        default_values = [1.0, 10.0, 5.0]  # Default values for amplitude, center, and width

        for label_text, default_value in zip(parameter_labels, default_values):
            parameter_label = QLabel(label_text)
            parameter_input = QLineEdit()
            parameter_input.setText(str(default_value))  # Set default value
            self.parameter_layout1.addWidget(parameter_label)
            self.parameter_layout1.addWidget(parameter_input)

        for label_text, default_value in zip(parameter_labels, default_values):
            parameter_label = QLabel(label_text)
            parameter_input = QLineEdit()
            parameter_input.setText(str(default_value))  # Set default value
            self.parameter_layout2.addWidget(parameter_label)
            self.parameter_layout2.addWidget(parameter_input)

        # Add labels to distinguish the input boxes for Plot 1 and Plot 2
        plot1_label = QLabel("Plot 1 Parameters:")
        controls_layout.addWidget(plot1_label)
        controls_layout.addLayout(self.parameter_layout1)

        plot2_label = QLabel("Plot 2 Parameters:")
        controls_layout.addWidget(plot2_label)
        controls_layout.addLayout(self.parameter_layout2)

        preview_button = QPushButton("Preview")
        preview_button.clicked.connect(self.on_preview_button_click)
        controls_layout.addWidget(preview_button)

        laser_button = QPushButton("Shoot the Laser")
        laser_button.clicked.connect(self.on_laser_button_click)
        controls_layout.addWidget(laser_button)

        main_layout.addLayout(controls_layout)

        central_widget.setLayout(main_layout)

    def update_wave_function(self, ax, x_values, y_values):
        ax.clear()
        ax.plot(x_values, y_values, 'b-')

        # Set x-axis limits to [0, 20]
        ax.set_xlim(0, 20)

        # Calculate the minimum and maximum values of the curve
        min_y = np.min(y_values)
        max_y = np.max(y_values)

        # Set y-axis limits to fit the entire curve
        y_margin = 0.1  # Add a small margin
        ax.set_ylim(min_y - y_margin, max_y + y_margin)

        self.canvas1.draw()
        self.canvas2.draw()

    def on_preview_button_click(self):
        # Get input parameters from the GUI for plot 1
        blackman_params1 = []
        for i in range(self.parameter_layout1.count()):
            widget = self.parameter_layout1.itemAt(i).widget()
            if isinstance(widget, QLineEdit):
                input_value = float(widget.text())
                blackman_params1.append(input_value)

        # Generate Blackman pulse based on input parameters for plot 1
        amplitude1, center1, width1 = blackman_params1
        x_values1 = np.linspace(0, 20, 1000)
        shifted_x_values1 = x_values1 - center1
        y_values1 = amplitude1 * np.blackman(len(x_values1)) * np.sinc(shifted_x_values1 / width1)

        # Update the plot for plot 1
        self.update_wave_function(self.ax1, x_values1, y_values1)

        # Get input parameters from the GUI for plot 2
        blackman_params2 = []
        for i in range(self.parameter_layout2.count()):
            widget = self.parameter_layout2.itemAt(i).widget()
            if isinstance(widget, QLineEdit):
                input_value = float(widget.text())
                blackman_params2.append(input_value)

        # Generate Blackman pulse based on input parameters for plot 2
        amplitude2, center2, width2 = blackman_params2
        x_values2 = np.linspace(0, 20, 1000)
        shifted_x_values2 = x_values2 - center2
        y_values2 = amplitude2 * np.blackman(len(x_values2)) * np.sinc(shifted_x_values2 / width2)

        # Update the plot for plot 2
        self.update_wave_function(self.ax2, x_values2, y_values2)

    def on_laser_button_click(self):
        # Get input parameters from the GUI for plot 1
        blackman_params1 = []
        for i in range(self.parameter_layout1.count()):
            widget = self.parameter_layout1.itemAt(i).widget()
            if isinstance(widget, QLineEdit):
                input_value = float(widget.text())
                blackman_params1.append(input_value)

        # Get input parameters from the GUI for plot 2
        blackman_params2 = []
        for i in range(self.parameter_layout2.count()):
            widget = self.parameter_layout2.itemAt(i).widget()
            if isinstance(widget, QLineEdit):
                input_value = float(widget.text())
                blackman_params2.append(input_value)

        # Perform an action using the input parameters (you can add your custom logic here)
        print("Laser shooting with parameters for Plot 1:", blackman_params1)
        print("Laser shooting with parameters for Plot 2:", blackman_params2)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BlackmanPulseGUI()
    window.show()
    sys.exit(app.exec_())
