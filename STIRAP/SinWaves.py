import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QLineEdit
from PyQt5.QtCore import Qt

class SineWaveGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("STIRAP Sine Wave GUI")
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

        self.ax1.set_ylim(-1, 1)
        self.ax2.set_ylim(-1, 1)

        self.x_values = np.linspace(0, 10, 1000)  # More points for smoother plots
        self.y_values1 = np.sin(self.x_values)
        self.y_values2 = np.cos(self.x_values)

        self.plot1, = self.ax1.plot(self.x_values, self.y_values1, 'b-')
        self.plot2, = self.ax2.plot(self.x_values, self.y_values2, 'b-')

        main_layout.addLayout(plots_layout)

        controls_layout = QVBoxLayout()

        control_label = QLabel("Sine Wave Parameters")
        controls_layout.addWidget(control_label, alignment=Qt.AlignCenter)

        self.parameter_layout1 = QVBoxLayout()
        self.parameter_layout2 = QVBoxLayout()

        parameter_labels = ["Amplitude:", "Frequency:", "Phase:"]

        for label_text in parameter_labels:
            parameter_label = QLabel(label_text)
            parameter_input = QLineEdit()
            parameter_input.setText("1.0")  # Set default value
            self.parameter_layout1.addWidget(parameter_label)
            self.parameter_layout1.addWidget(parameter_input)

        for label_text in parameter_labels:
            parameter_label = QLabel(label_text)
            parameter_input = QLineEdit()
            parameter_input.setText("1.0")  # Set default value
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

    def update_wave_function(self, ax, y_values):
        ax.clear()
        ax.plot(self.x_values, y_values, 'b-')

        # Calculate the minimum and maximum values of the sine wave
        min_y = np.min(y_values)
        max_y = np.max(y_values)

        # Set y-axis limits to fit the entire curve
        y_margin = 0.1  # Add a small margin
        ax.set_ylim(min_y - y_margin, max_y + y_margin)

        self.canvas1.draw()
        self.canvas2.draw()

    def on_preview_button_click(self):
        # Get input parameters from the GUI for plot 1
        sin_params1 = []
        for i in range(self.parameter_layout1.count()):
            widget = self.parameter_layout1.itemAt(i).widget()
            if isinstance(widget, QLineEdit):
                input_value = float(widget.text())
                sin_params1.append(input_value)

        # Generate sine wave based on input parameters for plot 1
        y_values1 = sin_params1[0] * np.sin(sin_params1[1] * self.x_values + sin_params1[2])

        # Update the plot for plot 1
        self.update_wave_function(self.ax1, y_values1)

        # Get input parameters from the GUI for plot 2
        sin_params2 = []
        for i in range(self.parameter_layout2.count()):
            widget = self.parameter_layout2.itemAt(i).widget()
            if isinstance(widget, QLineEdit):
                input_value = float(widget.text())
                sin_params2.append(input_value)

        # Generate sine wave based on input parameters for plot 2
        y_values2 = sin_params2[0] * np.sin(sin_params2[1] * self.x_values + sin_params2[2])

        # Update the plot for plot 2
        self.update_wave_function(self.ax2, y_values2)

    def on_laser_button_click(self):
        # Get input parameters from the GUI for plot 1
        sin_params1 = []
        for i in range(self.parameter_layout1.count()):
            widget = self.parameter_layout1.itemAt(i).widget()
            if isinstance(widget, QLineEdit):
                input_value = float(widget.text())
                sin_params1.append(input_value)

        # Get input parameters from the GUI for plot 2
        sin_params2 = []
        for i in range(self.parameter_layout2.count()):
            widget = self.parameter_layout2.itemAt(i).widget()
            if isinstance(widget, QLineEdit):
                input_value = float(widget.text())
                sin_params2.append(input_value)

        # Perform an action using the input parameters (you can add your custom logic here)
        print("Laser shooting with parameters for Plot 1:", sin_params1)
        print("Laser shooting with parameters for Plot 2:", sin_params2)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SineWaveGUI()
    window.show()
    sys.exit(app.exec_())
