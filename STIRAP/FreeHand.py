import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.lines import Line2D
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QSlider, QPushButton, QComboBox
from PyQt5.QtCore import Qt

# Custom Slider class with custom styles
class Slider(QSlider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: white;
                margin: 2px 0;
            }

            QSlider::handle:horizontal {
                background: #0D66C3;
                border: 2px solid #0D66C3;
                width: 14px;
                margin: -2px 0;
                border-radius: 3px;
            }
        """)

# Main GUI class derived from QMainWindow
class AdjustablePlots(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("STIRAP Free Hand")
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()

        # Create a vertical layout for the plots
        plots_layout = QVBoxLayout()
        self.canvas = FigureCanvas(plt.figure())
        plots_layout.addWidget(self.canvas)

        # Create two subplots for the plots
        self.ax1 = self.canvas.figure.add_subplot(2, 1, 1)
        self.ax2 = self.canvas.figure.add_subplot(2, 1, 2)

        # Label the axes of the plots
        self.ax1.set_ylabel("Amplitude")
        self.ax2.set_ylabel("Amplitude")
        self.ax2.set_xlabel("Time")

        # Set the minimum y-axis limit to -1
        self.ax1.set_ylim(-1, 1)
        self.ax2.set_ylim(-1, 1)

        # Generate initial x and y values for the plots
        self.x_values = np.linspace(0, 2*np.pi, 8)  # Adjusted to 8 points
        self.y_values1 = [0.0, 0, 0, 0, 0, 0, 0, 0]
        self.y_values2 = [0.0, 0, 0, 0, 0, 0, 0, 0]

        # Initialize the plots with initial data points
        self.plot1, = self.ax1.plot(self.x_values, self.y_values1, 'bo')
        self.plot2, = self.ax2.plot(self.x_values, self.y_values2, 'bo')

        # Create lines to connect the points on the plots
        self.lines1 = [Line2D([], [], linestyle='-', color='blue', lw=1) for _ in range(7)]  # Adjusted to 7 lines
        self.lines2 = [Line2D([], [], linestyle='-', color='blue', lw=1) for _ in range(7)]  # Adjusted to 7 lines

        # Add lines to the plots
        for line in self.lines1:
            self.ax1.add_line(line)

        for line in self.lines2:
            self.ax2.add_line(line)

        # Update lines with initial coordinates
        self.update_lines()

        main_layout.addLayout(plots_layout)

        sliders_button_layout = QVBoxLayout()

        self.create_dropdowns()  # Create dropdowns before sliders
        self.create_sliders()

        # Add a button at the bottom
        button = QPushButton("Shoot the Lasers")
        button.clicked.connect(self.on_button_click)
        sliders_button_layout.addWidget(button, alignment=Qt.AlignRight)

        control_label = QLabel("Make your Laser Pulse!")
        sliders_button_layout.addWidget(control_label, alignment=Qt.AlignCenter)

        sliders_button_layout.addLayout(self.plot1_layout)
        sliders_button_layout.addLayout(self.plot2_layout)

        # Add the sliders and button layout to the main layout
        main_layout.addLayout(sliders_button_layout)

        central_widget.setLayout(main_layout)

    # Method to create sliders for each plot
    def create_sliders(self):
        self.plot1_layout = QVBoxLayout()
        self.plot2_layout = QVBoxLayout()

        # Iterate over each plot and create sliders and labels for them
        for i, (ax, label_text, y_values, plot) in enumerate(
                zip([self.ax1, self.ax2], ['Plot 1', 'Plot 2'], [self.y_values1, self.y_values2], [self.plot1, self.plot2])
        ):
            plot_layout = QVBoxLayout()  # Layout for the plot label
            label = QLabel(label_text)  # Label to display the plot name
            plot_layout.addWidget(label, alignment=Qt.AlignCenter)

            dropdown_layout = QVBoxLayout()  # Layout for the dropdown
            dropdown_label = QLabel("Select Preset:")
            dropdown_layout.addWidget(dropdown_label, alignment=Qt.AlignCenter)
            if i == 0:
                dropdown_layout.addWidget(self.dropdown1)
            else:
                dropdown_layout.addWidget(self.dropdown2)

            sliders_layout = QVBoxLayout()  # Layout for the sliders
            sliders = []  # List to store the sliders for each plot

            # Create sliders for each point on the plot
            for j in range(8):  # Adjusted to 8 sliders
                slider = Slider(Qt.Horizontal)  # Horizontal slider
                slider.setRange(-100, 100)  # Set the range of the slider from -100 to 100
                slider.setValue(int(y_values[j] * 100))  # Set the initial value of the slider based on y_values
                slider.valueChanged.connect(lambda val, plot=plot, index=j: self.update_slider(val, plot, index))
                sliders_layout.addWidget(slider)  # Add the slider to the layout
                sliders.append(slider)  # Add the slider to the list

            # Add the plot layout, dropdown layout, and sliders layout to the main layout for each plot
            if i == 0:
                self.plot1_layout.addLayout(plot_layout)
                self.plot1_layout.addLayout(dropdown_layout)
                self.plot1_layout.addLayout(sliders_layout)
                self.plot1_layout.addSpacing(50)
            else:
                self.plot2_layout.addLayout(plot_layout)
                self.plot2_layout.addLayout(dropdown_layout)
                self.plot2_layout.addLayout(sliders_layout)
                self.plot2_layout.addSpacing(50)

            # Store sliders for each plot separately
            if i == 0:
                self.sliders1 = sliders
            else:
                self.sliders2 = sliders

    # Method to create dropdown menus for each plot
    def create_dropdowns(self):
        self.dropdown1 = QComboBox()
        self.dropdown1.addItems(["Free Hand", "Sin Wave", "Cos Wave", "Gaussian"])
        self.dropdown1.currentIndexChanged.connect(self.update_dropdown1)

        self.dropdown2 = QComboBox()
        self.dropdown2.addItems(["Free Hand", "Sin Wave", "Cos Wave", "Gaussian"])
        self.dropdown2.currentIndexChanged.connect(self.update_dropdown2)

    # Method to update plot and sliders based on dropdown selection for Plot 1
    def update_dropdown1(self):
        selected_option = self.dropdown1.currentText()
        if selected_option == "Free Hand":
            pass
        elif selected_option == "Sin Wave":
            self.y_values1 = np.sin(self.x_values)
        elif selected_option == "Cos Wave":
            self.y_values1 = np.cos(self.x_values)
        elif selected_option == "Gaussian":
            self.y_values1 = np.exp(-(self.x_values - np.mean(self.x_values))**2 / (2 * 1**2))  # Gaussian with mean at x middle

        for slider, y_value in zip(self.sliders1, self.y_values1):
            slider.setValue(int(y_value * 100))

        self.plot1.set_ydata(self.y_values1)
        self.update_lines()
        self.canvas.draw_idle()

    # Method to update plot and sliders based on dropdown selection for Plot 2
    def update_dropdown2(self):
        selected_option = self.dropdown2.currentText()
        if selected_option == "Free Hand":
            pass
        elif selected_option == "Sin Wave":
            self.y_values2 = np.sin(self.x_values)
        elif selected_option == "Cos Wave":
            self.y_values2 = np.cos(self.x_values)
        elif selected_option == "Gaussian":
            self.y_values2 = np.exp(-(self.x_values - np.mean(self.x_values))**2 / (2 * 1**2))  # Gaussian with mean at x middle

        for slider, y_value in zip(self.sliders2, self.y_values2):
            slider.setValue(int(y_value * 100))

        self.plot2.set_ydata(self.y_values2)
        self.update_lines()
        self.canvas.draw_idle()

    # Method to update the y-values of the plots based on the slider values
    def update_slider(self, val, plot, index):
        y_values = plot.get_ydata()  # Get the current y-values of the plot
        y_values[index] = val / 100.0  # Update the corresponding y-value based on the slider value
        plot.set_ydata(y_values)  # Set the updated y-values to the plot

        self.update_lines()  # Update the lines connecting the points on the plot

        self.canvas.draw_idle()  # Redraw the plot canvas

    # Method to update the lines connecting the points on the plots
    def update_lines(self):
        for i, (plot, lines) in enumerate([(self.plot1, self.lines1), (self.plot2, self.lines2)]):
            for j, line in enumerate(lines):
                x_values = self.x_values[j:j + 2]  # Get the x-values of two adjacent points
                y_values = plot.get_ydata()[j:j + 2]  # Get the y-values of two adjacent points
                line.set_data(x_values, y_values)  # Update the line with the new coordinates

    # Method to handle button click event
    def on_button_click(self):
        # Print the values of the 16 points on the plots to console
        print("Plot 1 Y-Values:", self.plot1.get_ydata())
        print("Plot 2 Y-Values:", self.plot2.get_ydata())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdjustablePlots()
    window.show()
    sys.exit(app.exec_())
