import numpy as np
import matplotlib.pyplot as plt

h = 6.626e-34
c = 3.0e8
eV = 1.602e-19
Z = 1

def energy_level(n, Z=1):
    return -13.6 * Z**2 / n**2

series_names = {1: 'Lyman', 2: 'Balmer', 3: 'Paschen', 4: 'Brackett', 5: 'Pfund'}
n_max = 8

results = {name: {'wavelength': [], 'energy': []} for name in series_names.values()}

for n1 in series_names:
    for n2 in range(n1 + 1, n_max + 1):
        delta_E_eV = energy_level(n2, Z) - energy_level(n1, Z)
        delta_E_J = delta_E_eV * eV
        wavelength = h * c / delta_E_J
        
        name = series_names[n1]
        results[name]['energy'].append(delta_E_eV)
        results[name]['wavelength'].append(wavelength * 1e9)

colors = {'Lyman': 'purple', 'Balmer': 'blue', 'Paschen': 'green', 
          'Brackett': 'orange', 'Pfund': 'red'}

for name, data in results.items():
    plt.scatter(data['wavelength'], data['energy'], 
                label=name, color=colors[name], s=15)

plt.xlabel('Wavelength / nm')
plt.ylabel('Photon energy / eV')
plt.title('Bohr model of Hydrogenic atom photon emmissions: Z = 1')
plt.legend()
plt.xlim(0, 8000)
plt.show()
