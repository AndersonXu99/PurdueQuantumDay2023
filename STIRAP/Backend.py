import os
import numpy as np
import scipy
import matplotlib
import matplotlib.pylab as plt
from scipy.interpolate import splrep, BSpline
import krotov
import qutip
from qutip import Qobj

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


def RWA_Target_State(Ket_3, E2 = 10.0, Omega_S = 4.5, T = 5):
    return np.exp(1j * (E2 - Omega_S) * T) * Ket_3

def Plot_Pulses(pulse, tlist, label):
    fig, ax = plt.subplots()
    if callable(pulse):
        pulse = np.array([pulse(t, args=None) for t in tlist])
    ax.plot(tlist, pulse)
    ax.set_xlabel('time')
    ax.set_ylabel('%s pulse amplitude' % label)
    plt.show()  # Remove the 'fig' argument here
    
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
    #Pre-established Time-Domain
    T_axis = np.arange(0, T_end + 1)

    #Random Values given by User
    tck = splrep(T_axis, Omega_Inputs, s=0)

    #Making the random values into Smooth Function (time below is also pre-established)
    t_smooth = np.linspace(0, T_end, 500)
    Pulse_smooth = BSpline(*tck)(t_smooth)

    return Pulse_smooth
