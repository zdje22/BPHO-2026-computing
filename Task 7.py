import numpy as np
import matplotlib.pyplot as plt
from scipy import integrate, constants

h    = constants.h
hbar = constants.hbar
m    = constants.electron_mass

L = constants.physical_constants["Bohr radius"][0]
def energy(n, m=m, L=L):
    return n**2 * h**2 / (8 * m * L**2)

n_max = 6
n_vals = np.arange(1, n_max + 1)
E_vals_J  = energy(n_vals)
E_vals_eV = E_vals_J / constants.e

print("Energy levels:")
for n, E in zip(n_vals, E_vals_eV):
    print(f"  n = {n}:  E = {E:.4f} eV")

fig1, ax1 = plt.subplots(figsize=(6, 5))
ax1.plot(n_vals, E_vals_eV, 'o-', color='crimson')
ax1.set_xlabel("Quantum number, n")
ax1.set_ylabel("Energy / eV")
ax1.set_title("Energy vs quantum number")
ax1.grid(alpha=0.3)
fig1.tight_layout()

def psi(n, x, L=L):
    inside = (x >= 0) & (x <= L)
    out = np.zeros_like(x)
    out[inside] = np.sqrt(2 / L) * np.sin(n * np.pi * x[inside] / L)
    return out

def prob_density(n, x, L=L):
    return psi(n, x, L)**2

x = np.linspace(0, L, 2000)
x_ang = x * 1e10

fig2, ax2 = plt.subplots(figsize=(6, 5))
colors = ['tab:blue', 'tab:green', 'tab:red']
for n, c in zip([1, 2, 3], colors):
    pdf = prob_density(n, x)
    ax2.plot(x_ang, pdf, color=c, label=f"n = {n}  E = {E_vals_eV[n-1]:.4f} eV")

ax2.set_xlabel("x / angstroms")
ax2.set_ylabel("Probability density")
ax2.set_title(f"Particle in a box\nm = {m:.4e} kg,  L = {L*1e10:.4f} Å")
ax2.legend()
ax2.grid(alpha=0.3)
fig2.tight_layout()

def delta_x_analytic(n, L=L):
    return L * np.sqrt(1/12 - 1/(2 * n**2 * np.pi**2))

def delta_p_analytic(n, L=L):
    return n * np.pi * hbar / L

def delta_x_numeric(n, L=L, npts=20000):
    xx = np.linspace(0, L, npts)
    pdf = prob_density(n, xx, L)
    x_mean  = integrate.simpson(xx * pdf, xx)
    x2_mean = integrate.simpson(xx**2 * pdf, xx)
    return np.sqrt(x2_mean - x_mean**2)

def delta_p_numeric(n, L=L, npts=20000):
    xx = np.linspace(0, L, npts)
    psi_n = psi(n, xx, L)
    dpsi_dx = np.gradient(psi_n, xx)
    d2psi_dx2 = np.gradient(dpsi_dx, xx)
    p2_mean = -hbar**2 * integrate.simpson(psi_n * d2psi_dx2, xx)
    return np.sqrt(p2_mean)

print("\nUncertainty principle check (Delta_x * Delta_p >= hbar/2):")
print(f"{'n':>2}  {'Dx (analytic)':>15}  {'Dp (analytic)':>15}  "
      f"{'Dx*Dp':>12}  {'hbar/2':>10}  {'ratio':>6}")
for n in n_vals:
    dx = delta_x_analytic(n)
    dp = delta_p_analytic(n)
    product = dx * dp
    ratio = product / (hbar / 2)
    print(f"{n:>2}  {dx:15.4e}  {dp:15.4e}  {product:12.4e}  "
          f"{hbar/2:10.4e}  {ratio:6.3f}")

products = [delta_x_analytic(n) * delta_p_analytic(n) for n in n_vals]

fig3, ax3 = plt.subplots(figsize=(6, 5))
ax3.plot(n_vals, products, 'o-', color='purple', label=r"$\Delta x \, \Delta p$")
ax3.axhline(hbar / 2, color='k', linestyle='--', label=r"Heisenberg bound: $\hbar/2$")
ax3.set_xlabel("Quantum number, n")
ax3.set_ylabel(r"$\Delta x \, \Delta p$ (J s)")
ax3.set_title("Uncertainty Principle")
ax3.legend()
ax3.grid(alpha=0.3)
fig3.tight_layout()

plt.show()
