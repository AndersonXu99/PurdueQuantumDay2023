import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.lines import Line2D
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QSlider, QPushButton, QComboBox, QLineEdit, QMessageBox, QFormLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from scipy.interpolate import splrep, BSpline
import krotov
import qutip
from qutip import Qobj
import matplotlib.pylab as plt
from scipy.interpolate import splrep, BSpline
from qutip import Qobj
import requests

def Omega_P2_Guess(t, args):
    """Guess for the imaginary part of the pump pulse"""
    return 0.0

def Omega_S2_Guess(t, args):
    """Guess for the imaginary part of the Stokes pulse"""
    return 0.0

def Hamiltonian(Omega_P1_Smooth, Omega_S1_Smooth, E1=0.0, E2=10.0, E3=5.0, Omega_P=9.5, Omega_S=4.5):
    """Lambda-system Hamiltonian in the RWA"""

    # detunings
    P = E1 + Omega_P - E2
    S = E3 + Omega_S - E2

    H_0 = Qobj([[P, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, S]])

    HP_Re = -0.5 * Qobj([[0.0, 1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 0.0]])
    HP_Im = -0.5 * Qobj([[0.0, 1.0j, 0.0], [-1.0j, 0.0, 0.0], [0.0, 0.0, 0.0]])

    HS_Re = -0.5 * Qobj([[0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0]])
    HS_Im = -0.5 * Qobj([[0.0, 0.0, 0.0], [0.0, 0.0, 1.0j], [0.0, -1.0j, 0.0]])

    return [
        H_0,
        [HP_Re, Omega_P1_Smooth],
        [HP_Im, Omega_P2_Guess],
        [HS_Re, Omega_S1_Smooth],
        [HS_Im, Omega_S2_Guess],
    ]

def RWA_Target_State(Ket_3, E2=10.0, Omega_S=4.5, T=5):
    return np.exp(1j * (E2 - Omega_S) * T) * Ket_3

def Plot_Pulses(pulse, tlist, label):
    fig, ax = plt.subplots()
    if callable(pulse):
        pulse = np.array([pulse(t, args=None) for t in tlist])
    ax.plot(tlist, pulse)
    ax.set_xlabel('time')
    ax.set_ylabel('%s pulse amplitude' % label)
    #plt.show() 

def Plot_Population(result):
    fig, ax = plt.subplots()
    ax.plot(result.times, result.expect[0], label='1')
    ax.plot(result.times, result.expect[1], label='2')
    ax.plot(result.times, result.expect[2], label='3')
    ax.legend()
    ax.set_xlabel('time')
    ax.set_ylabel('population')
    plt.show()

def Omega_Smooth(Omega_Inputs, T_end):
    # Pre-established Time-Domain
    T_axis = np.arange(0, T_end + 1)

    # Random Values given by User
    tck = splrep(T_axis, Omega_Inputs, s=0)

    # Making the random values into Smooth Function (time below is also pre-established)
    t_smooth = np.linspace(0, T_end, 500)
    Pulse_smooth = BSpline(*tck)(t_smooth)

    return Pulse_smooth

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

        # Set the window size to cover the entire screen
        self.setWindowState(Qt.WindowFullScreen)

        # Set the background color to white
        # self.setStyleSheet("color: black;")
        
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()

        left_layout = QVBoxLayout()
        left_form_layout = QFormLayout()

        self.user_name = ""
        self.currentScore = 0
        self.highScore = 0

        self.name_prompt = QLabel("Please enter your name:")
        self.name_input = QLineEdit()
        #left_layout.addWidget(self.name_prompt)
        #left_layout.addWidget(self.name_input)
        left_form_layout.addRow(self.name_prompt)
        left_form_layout.addRow(self.name_input)

        self.name_button = QPushButton("Enter")
        self.name_button.clicked.connect(self.name_button_click)
        #left_layout.addWidget(self.name_button)

        left_form_layout.addRow(self.name_button)

        self.reset_button = QPushButton("End Session and Send Your High Score!")
        self.reset_button.clicked.connect(self.reset_button_click)

        left_layout.addLayout(left_form_layout)

        left_layout.addWidget(self.reset_button)
        self.reset_button.setEnabled(False)

        image = QLabel()
        map = QPixmap("489844_1_En_19_Fig1_HTML.png")
        scaled_map = map.scaled(400, 400, Qt.KeepAspectRatio)
        image.setPixmap(scaled_map)
        image.setAlignment(Qt.AlignCenter)

        left_layout.addWidget(image)

        image2 = QLabel()
        map2 = QPixmap("PU_LOGO.png")
        scaled_map2 = map2.scaled(400, 400, Qt.KeepAspectRatio)
        image2.setPixmap(scaled_map2)
        image2.setAlignment(Qt.AlignCenter)

        left_layout.addWidget(image2)
        

        # Create a vertical layout for the initial plots on the left
        left_plots_layout = QVBoxLayout()
        self.canvas = FigureCanvas(plt.figure())
        left_plots_layout.addWidget(self.canvas)

        # Create two subplots for the initial plots
        self.ax1 = self.canvas.figure.add_subplot(2, 1, 1)
        self.ax2 = self.canvas.figure.add_subplot(2, 1, 2)

        # Label the axes of the plots
        self.ax1.set_title("Laser Pulses")
        self.ax1.set_ylabel("Amplitude")
        self.ax2.set_ylabel("Amplitude")
        self.ax2.set_xlabel("Time")

        # Set the minimum y-axis limit to -1
        self.ax1.set_ylim(-1, 1)
        self.ax2.set_ylim(-1, 1)

        # Generate initial x and y values for the plots
        self.x_values = np.linspace(0, 2 * np.pi, 10)  # Adjusted to 8 points
        self.y_values1 = [0.0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.y_values2 = [0.0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        # Initialize the plots with initial data points
        self.plot1, = self.ax1.plot(self.x_values, self.y_values1, 'bo')
        self.plot2, = self.ax2.plot(self.x_values, self.y_values2, 'bo')

        # Create lines to connect the points on the plots
        self.lines1 = [Line2D([], [], linestyle='-', color='blue', lw=1) for _ in range(9)]  # Adjusted to 7 lines
        self.lines2 = [Line2D([], [], linestyle='-', color='blue', lw=1) for _ in range(9)]  # Adjusted to 7 lines

        # Add lines to the plots
        for line in self.lines1:
            self.ax1.add_line(line)

        for line in self.lines2:
            self.ax2.add_line(line)

        # Update lines with initial coordinates
        self.update_lines()

        main_layout.addLayout(left_layout)

        # Add left_plots_layout to the main layout
        main_layout.addLayout(left_plots_layout)

        # Create a vertical layout for sliders, dropdown menus, and buttons in the center
        sliders_button_layout = QVBoxLayout()

        self.create_dropdowns()  # Create dropdowns before sliders
        self.create_sliders()

        # Add a button at the bottom
        button = QPushButton("Shoot the Lasers")
        button.clicked.connect(self.on_button_click)
        sliders_button_layout.addWidget(button, alignment=Qt.AlignCenter)
        button.setEnabled(False)

        control_label = QLabel("Make your Laser Pulse!")
        sliders_button_layout.addWidget(control_label, alignment=Qt.AlignCenter)

        sliders_button_layout.addLayout(self.plot1_layout)
        sliders_button_layout.addLayout(self.plot2_layout)

        # Add sliders_button_layout to the main layout
        main_layout.addLayout(sliders_button_layout)

        # Create a vertical layout for the new plots on the right
        new_plots_layout = QVBoxLayout()
        self.canvas2 = FigureCanvas(plt.figure())
        new_plots_layout.addWidget(self.canvas2)

        # Create three new subplots for the new plots
        self.ax3 = self.canvas2.figure.add_subplot(3, 1, 1)
        self.ax4 = self.canvas2.figure.add_subplot(3, 1, 2)
        self.ax5 = self.canvas2.figure.add_subplot(3, 1, 3)

        # Label the axes of the new plots
        self.ax3.set_title("Population Distributions")
        self.ax3.set_ylabel("Population (Level 1)")
        self.ax4.set_ylabel("Population (Level 2)")
        self.ax5.set_ylabel("Population (Level 3)")
        self.ax5.set_xlabel("Time")

        # Set the minimum y-axis limit for the new plots
        self.ax3.set_ylim(0, 1)
        self.ax4.set_ylim(0, 1)
        self.ax5.set_ylim(0, 1)

        # Initialize the new plots with initial data (empty)
        self.plot3, = self.ax3.plot([], [], 'g-')
        self.plot4, = self.ax4.plot([], [], 'b-')
        self.plot5, = self.ax5.plot([], [], 'r-')

        # Add new_plots_layout to the main layout
        main_layout.addLayout(new_plots_layout)

        central_widget.setLayout(main_layout)


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
            for j in range(10):  # Adjusted to 10 sliders
                slider = Slider(Qt.Horizontal)  # Horizontal slider
                slider.setRange(-100, 100)  # Set the range of the slider from -100 to 100
                if j == 0 or j == 9:  # Set the initial value to 0.0 for the constant data points
                    slider.setValue(0)
                    slider.setEnabled(False)  # Disable sliders for constant data points
                else:
                    slider.setValue(int(y_values[j - 1] * 100))  # Set the initial value based on y_values
                slider.valueChanged.connect(lambda val, plot=plot, index=j - 1: self.update_slider(val, plot, index))
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
            self.y_values1[0] = 0
            self.y_values1[9] = 0
        elif selected_option == "Gaussian":
            self.y_values1 = np.exp(-(self.x_values - np.mean(self.x_values)) ** 2 / (2 * 1 ** 2))  # Gaussian with mean at x middle

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
            self.y_values2 = np.exp(-(self.x_values - np.mean(self.x_values)) ** 2 / (2 * 1 ** 2))  # Gaussian with mean at x middle

        for slider, y_value in zip(self.sliders2, self.y_values2):
            slider.setValue(int(y_value * 100))

        self.plot2.set_ydata(self.y_values2)
        self.update_lines()
        self.canvas.draw_idle()

    def update_slider(self, val, plot, index):
        y_values = plot.get_ydata()  # Get the current y-values of the plot
        y_values[index + 1] = val / 100.0  # Update the corresponding y-value based on the slider value
        plot.set_ydata(y_values)  # Set the updated y-values to the plot

        self.update_lines()  # Update the lines connecting the points on the plot

        self.canvas.draw_idle()  # Redraw the plot canvas


    def update_lines(self):
        for i, (plot, lines) in enumerate([(self.plot1, self.lines1), (self.plot2, self.lines2)]):
            x_values = self.x_values
            y_values = plot.get_ydata()

            for j, line in enumerate(lines):
                if j < len(lines) - 1:  # Adjusted the range to include all points
                    x_data = x_values[j:j + 2]  # Connect adjacent points
                    y_data = y_values[j:j + 2]
                else:
                    x_data = x_values[-2:]  # Connect the last two points
                    y_data = y_values[-2:]

                line.set_data(x_data, y_data)  # Update the line with the new coordinates

        self.canvas.draw_idle()  # Redraw the plot canvas


    def reset_button_click(self):

        self.name_button.setEnabled(True)
            # Reset the sliders to their default values (0.0)
        for slider in self.sliders1 + self.sliders2:
            slider.setValue(0)
    
        # Clear the plots on the right
        self.plot3.set_data([], [])
        self.plot4.set_data([], [])
        self.plot5.set_data([], [])
    
        self.ax3.set_ylabel("Population (Level 1)")
        self.ax4.set_ylabel("Population (Level 2)")
        self.ax5.set_ylabel("Population (Level 3)")
    
        self.canvas2.draw()
        self.update_lines()  # Update the lines on the left plots
    
        self.canvas.draw_idle()  # Redraw the left plots

        Stringbuilder = "https://gmscoreboard.com/api/set-score/?tagid=94b47096b96f2864e21376a548822b09&player=" + self.user_name + "&score=" + str(self.highScore)
        response = requests.get(Stringbuilder)
        self.user_name = ""
        self.currentScore = 0
        self.highScore = 0


    def name_button_click(self):
        user_name = self.name_input.text()

        if not user_name:
            QMessageBox.warning(self, "Warning", "Please enter your name.")
            return
        
        self.name_button.setEnabled(False)
        self.reset_button.setEnabled(True)
        self.user_name = user_name


    # Method to handle button click event
    def on_button_click(self):


        # Sending the data from the plot to the backend function
        # User Inputs Random Values
        T_end = 9

        #We smooth the Values
        Omega_P1_Smooth = Omega_Smooth(self.plot1.get_ydata(), T_end)
        Omega_S1_Smooth = Omega_Smooth(self.plot2.get_ydata(), T_end)

        ##We Solve the System
        H = Hamiltonian(Omega_P1_Smooth, Omega_S1_Smooth)

        Ket_1 = qutip.Qobj(np.array([1.0, 0.0, 0.0]))
        Ket_2 = qutip.Qobj(np.array([0.0, 1.0, 0.0]))
        Ket_3 = qutip.Qobj(np.array([0.0, 0.0, 1.0]))

        Proj_1 = qutip.ket2dm(Ket_1)
        Proj_2 = qutip.ket2dm(Ket_2)
        Proj_3 = qutip.ket2dm(Ket_3)

        # Target State Definition
        Psi_Target = RWA_Target_State(Ket_3)

        # Instantiating Control Objective
        Objective = krotov.Objective(initial_state=Ket_1, target=Psi_Target, H=H)

        # Show Pulse Plots
        t = np.linspace(0, T_end, 500)
        Plot_Pulses(H[1][1], t, 'Ωₚ')
        Plot_Pulses(H[3][1], t, 'Ωₛ')

        Guess_Dynamics = Objective.mesolve(t, e_ops=[Proj_1, Proj_2, Proj_3])

        #print("-----------------------------")
        #percentage1 = "{:.2f}%".format(Guess_Dynamics.expect[0][499] * 100)
        #percentage2 = "{:.2f}%".format(Guess_Dynamics.expect[1][499] * 100)
        #percentage3 = "{:.2f}%".format(Guess_Dynamics.expect[2][499] * 100)

        #print(f"Percentage of Level 1: {percentage1}")
        #print(f"Percentage of Level 2: {percentage2}")
        #print(f"Percentage of Level 3: {percentage3}")
        #print("-----------------------------")

        self.currentScore = int(Guess_Dynamics.expect[2][499] * 100)

        if self.currentScore > int(self.highScore):
            self.highScore = self.currentScore

        self.update_population_plots(Guess_Dynamics)

    # Method to update the population plots on the right
    def update_population_plots(self, result):
        self.plot3.set_data(result.times, result.expect[0])
        self.plot4.set_data(result.times, result.expect[1])
        self.plot5.set_data(result.times, result.expect[2])

        self.ax3.set_ylabel("Population (Level 1)")
        self.ax4.set_ylabel("Population (Level 2)")
        self.ax5.set_ylabel("Population (Level 3)")
        self.ax5.set_xlabel("Time") 

        self.ax3.relim()
        self.ax4.relim()
        self.ax5.relim()
        self.ax3.autoscale_view()
        self.ax4.autoscale_view()
        self.ax5.autoscale_view()

        self.canvas2.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdjustablePlots()
    window.show()
    sys.exit(app.exec_())