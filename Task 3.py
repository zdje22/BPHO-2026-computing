import numpy as np
import matplotlib.pyplot as plt

h = 6.626e-34
c = 3.0e8
kB = 1.381e-23
sigma = 5.670e-8
R = 8.314

wavelength = np.linspace(1e-9, 2500e-9, 2000)

def planck(wavelength, T):
    a = 2 * h * c**2
    b = h * c / (wavelength * kB * T)
    with np.errstate(over='ignore'):
        intensity = a / (wavelength**5 * (np.exp(b) - 1))
    return intensity

temperatures = [4000, 5000, 6000]

wavelength_full = np.linspace(1e-9, 200000e-9, 200000)

def radiant_exitance(T):
    B = planck(wavelength_full, T)
    M = np.pi * np.trapezoid(B, wavelength_full)
    return M

T_range = np.linspace(300, 8000, 60)
M_numerical = np.array([radiant_exitance(T) for T in T_range])
M_stefan_boltzmann = sigma * T_range**4

einstein_temperatures = {
    'Au': 170,
    'Cu': 343.5,
    'Ti': 420,
    'Al': 428,
    'Fe': 470,
    'Si': 645,
    'C':  2230,
}

T_solid = np.linspace(1, 800, 800)

def einstein_heat_capacity(T, theta_E):
    x = theta_E / T
    with np.errstate(over='ignore', invalid='ignore'):
        C = 3 * R * (x**2 * np.exp(x)) / (np.exp(x) - 1)**2
    return C

fig1 = plt.figure(1, figsize=(7, 5.5))
ax1 = fig1.add_subplot(111)
for T in temperatures:
    intensity = planck(wavelength, T)
    ax1.plot(wavelength * 1e9, intensity, label=f'T = {T} K')
ax1.set_xlabel('Wavelength / nm')
ax1.set_ylabel('Spectral radiance')
ax1.set_title('Black body radiation')
ax1.legend()
fig1.tight_layout()

fig2 = plt.figure(2, figsize=(7, 5.5))
ax2 = fig2.add_subplot(111)
ax2.plot(T_range, M_numerical, 'o', color='tab:blue', markersize=4)
ax2.plot(T_range, M_stefan_boltzmann, '-', color='tab:red', linewidth=2,
          label='$\\sigma T^4$')
ax2.set_xlabel('Temperature / K')
ax2.set_ylabel('Radiant exitance / W m$^{-2}$')
ax2.set_title('Integrated Planck radiance vs $\\sigma T^4$')
ax2.legend()
fig2.tight_layout()

fig3 = plt.figure(3, figsize=(7, 5.5))
ax3 = fig3.add_subplot(111)
for element, theta_E in einstein_temperatures.items():
    C = einstein_heat_capacity(T_solid, theta_E)
    ax3.plot(T_solid, C, label=f'{element} ({theta_E} K)')

ax3.axhline(3 * R, color='k', linestyle='--', linewidth=1)
ax3.set_xlabel('T / K')
ax3.set_ylabel('Molar heat capacity / J mol$^{-1}$K$^{-1}$')
ax3.set_title('Einstein model of solid molar heat capacity')
ax3.legend(fontsize=8)
ax3.set_ylim(0, 27)
fig3.tight_layout()

plt.show()
