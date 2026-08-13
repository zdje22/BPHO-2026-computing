import numpy as np
import matplotlib.pyplot as plt
from scipy.constants import h, c, m_e, e

energies_keV = [50, 100, 200, 500, 1000]

theta_deg = np.linspace(0.001, 180, 2000)
theta = np.radians(theta_deg)

results = {}
for E_keV in energies_keV:
    E_joules = E_keV * 1e3 * e
    lam = h * c / E_joules
    alpha = h / (m_e * c * lam)

    frac_shift = alpha * (1 - np.cos(theta))
    lam_prime = lam * (1 + frac_shift)

    KE = h * c * (1 / lam - 1 / lam_prime)
    rest_energy = m_e * c**2
    gamma = 1 + KE / rest_energy
    v = c * np.sqrt(1 - 1 / gamma**2)

    phi = np.arctan2(1.0, (1 + alpha) * np.tan(theta / 2))
    phi_deg = np.degrees(phi)

    results[E_keV] = dict(frac_shift=frac_shift, v=v, phi_deg=phi_deg)

fig1 = plt.figure(figsize=(7, 5.5))
for E_keV in energies_keV:
    plt.plot(theta_deg, results[E_keV]['frac_shift'], label=f'E={E_keV}keV')
plt.xlabel(r'$\theta$ / deg')
plt.ylabel(r'$\Delta\lambda/\lambda$')
plt.title('Compton scattering')
plt.legend(fontsize=8)
plt.grid(alpha=0.3)

fig2 = plt.figure(figsize=(7, 5.5))
for E_keV in energies_keV:
    plt.plot(theta_deg, results[E_keV]['v'] / c, label=f'E={E_keV}keV')
plt.xlabel(r'$\theta$ / deg')
plt.ylabel('v / c')
plt.title('Compton scattering')
plt.legend(fontsize=8)
plt.grid(alpha=0.3)

fig3 = plt.figure(figsize=(7, 5.5))
for E_keV in energies_keV:
    plt.plot(theta_deg, results[E_keV]['phi_deg'], label=f'E={E_keV}keV')
plt.xlabel(r'$\theta$ / deg')
plt.ylabel(r'$\phi$ / deg')
plt.title('Compton scattering')
plt.legend(fontsize=8)
plt.grid(alpha=0.3)

plt.show()
