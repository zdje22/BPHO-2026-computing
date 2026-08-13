import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from matplotlib.colors import LinearSegmentedColormap
from scipy.stats import linregress

PHOSPHOR_CMAP = LinearSegmentedColormap.from_list(
    "phosphor", ["black", "#0c3b0c", "#30f30d", "#dfffd4eb"]
)

h    = 6.62607015e-34
m_e  = 9.10938371e-31
e    = 1.602176634e-19
c    = 2.99792458e8

r = 65e-3
d = 0.213e-9
MAX_ORDER = 4
V_range = np.linspace(1000, 5000, 400)

def de_broglie_wavelength(V, relativistic=False):
    """Electron wavelength (m) for accelerating voltage V (volts)."""
    if relativistic:
        return h / np.sqrt(2 * m_e * e * V * (1 + (e * V) / (2 * m_e * c**2)))
    return h / np.sqrt(2 * m_e * e * V)

def bragg_theta(wavelength, n=1):
    sin_theta = n * wavelength / (2 * d)
    sin_theta = np.where(sin_theta <= 1.0, sin_theta, np.nan)
    return np.arcsin(sin_theta)

def ring_radius(V, n=1, relativistic=False):
    lam = de_broglie_wavelength(V, relativistic)
    theta = bragg_theta(lam, n)
    phi = 2 * theta
    x = r * np.sin(phi)
    return x, theta, phi

def visible_orders(V, max_order=MAX_ORDER, relativistic=False):
    orders = []
    for n in range(1, max_order + 1):
        x, theta, phi = ring_radius(V, n, relativistic)
        if np.isnan(x) or phi >= np.pi / 2:
            break
        orders.append((n, x, theta, phi, 1.0 / n))
    return orders

def plot_x_vs_V():
    fig, ax = plt.subplots(figsize=(7, 5))
    for n in range(1, MAX_ORDER + 1):
        x, theta, phi = ring_radius(V_range, n)
        ax.plot(V_range / 1000, x * 1000, label=f"n = {n}")
    ax.set_xlabel("Accelerating voltage V (kV)")
    ax.set_ylabel("Ring radius x (mm)")
    ax.set_title(f"Ring radius vs accelerating voltage  (d = {d*1e9:.3f} nm)")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return fig

def plot_straight_line_check():
    fig, ax = plt.subplots(figsize=(7, 5))
    inv_sqrt_V = 1 / np.sqrt(V_range)

    results = {}
    for n in range(1, MAX_ORDER + 1):
        _, theta, phi = ring_radius(V_range, n)
        sin_half_phi = np.sin(phi / 2)
        ax.plot(inv_sqrt_V, sin_half_phi, '.', markersize=3, label=f"n = {n}")

        mask = ~np.isnan(sin_half_phi)
        slope, intercept, r_value, _, _ = linregress(inv_sqrt_V[mask], sin_half_phi[mask])
        d_extracted = n * h / (2 * slope * np.sqrt(2 * m_e * e))
        results[n] = (slope, intercept, r_value, d_extracted)

    ax.set_xlabel(r"$1/\sqrt{V}$  (V$^{-1/2}$)")
    ax.set_ylabel(r"$\sin(\phi/2)$")
    ax.set_title(r"Straight-line check: $\sin(\phi/2) = \dfrac{nh}{2d\sqrt{2m_eeV}}$")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()

    print("Straight-line fit results (gradient, intercept, R^2, recovered d):")
    for n, (slope, intercept, r_value, d_extracted) in results.items():
        print(f"  n = {n}")
        print(f"    gradient   = {slope:.6e}")
        print(f"    intercept  = {intercept:.3e}  (should be ~0)")
        print(f"    R^2        = {r_value**2:.6f}")
        print(f"    recovered d = {d_extracted*1e9:.4f} nm  (input was {d*1e9:.4f} nm)")
    return fig

def synthetic_screen_image(V, size=400, extent_mm=35, ring_width_mm=0.6,
                            max_order=MAX_ORDER):
    xs = np.linspace(-extent_mm, extent_mm, size)
    X, Y = np.meshgrid(xs, xs)
    R = np.sqrt(X**2 + Y**2)

    image = np.zeros_like(R)
    image += 3.0 * np.exp(-(R / 1.2)**2)

    orders = visible_orders(V, max_order)
    for n, x0, theta, phi, weight in orders:
        x0_mm = x0 * 1000
        image += weight * np.exp(-0.5 * ((R - x0_mm) / (ring_width_mm * (1 + 0.15 * (n - 1))))**2)

    return xs, image, orders

def plot_screen_image(V=3000):
    xs, image, orders = synthetic_screen_image(V)
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(image, cmap=PHOSPHOR_CMAP, extent=[xs.min(), xs.max(), xs.min(), xs.max()],
               origin="lower")
    ax.set_facecolor("black")
    ax.set_xlabel("mm")
    ax.set_ylabel("mm")
    order_str = ", ".join(f"n={n}" for n, *_ in orders)
    ax.set_title(f"Simulated phosphor screen, V = {V/1000:.1f} kV  ({order_str})")
    fig.tight_layout()
    return fig

def interactive_model():
    V0 = 3000
    xs, image, orders = synthetic_screen_image(V0)

    fig, ax = plt.subplots(figsize=(6, 7))
    plt.subplots_adjust(bottom=0.2)
    im = ax.imshow(image, cmap=PHOSPHOR_CMAP, extent=[xs.min(), xs.max(), xs.min(), xs.max()],
                    origin="lower", vmin=0, vmax=3)
    ax.set_facecolor("black")
    ax.set_xlabel("mm")
    ax.set_ylabel("mm")
    title = ax.set_title(f"V = {V0/1000:.2f} kV")

    ax_slider = plt.axes([0.2, 0.06, 0.6, 0.03])
    slider = Slider(ax_slider, "V (kV)", 1.0, 5.0, valinit=V0/1000, valstep=0.05)

    def update(val):
        V = slider.val * 1000
        _, image, orders = synthetic_screen_image(V)
        im.set_data(image)
        order_str = ", ".join(f"n={n}" for n, *_ in orders)
        title.set_text(f"V = {slider.val:.2f} kV   ({order_str})")
        fig.canvas.draw_idle()

    slider.on_changed(update)
    plt.show()

if __name__ == "__main__":
    plot_x_vs_V()
    plot_straight_line_check()
    plt.show()
    interactive_model()
