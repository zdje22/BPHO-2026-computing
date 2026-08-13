import numpy as np
from scipy.special import genlaguerre, factorial
from scipy.special import sph_harm_y
def sph_harm(m, l, phi, theta):
    return sph_harm_y(l, m, theta, phi)
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from skimage import measure

A0 = 0.52917721067
RY_EV = 13.605693009 

def radial_wavefunction(n, l, r, Z=1):
    a = A0 / Z
    rho = 2 * r / (n * a)
    norm = np.sqrt(
        (2 / (n * a)) ** 3 * factorial(n - l - 1) / (2 * n * factorial(n + l))
    )
    laguerre = genlaguerre(n - l - 1, 2 * l + 1)(rho)
    return norm * np.exp(-rho / 2) * rho ** l * laguerre

def angular_wavefunction(l, m, theta, phi, real=True):
    Y_pos = sph_harm(abs(m), l, phi, theta)
    if not real:
        return sph_harm(m, l, phi, theta)

    if m == 0:
        return np.real(Y_pos)
    elif m > 0:
        return np.sqrt(2) * (-1) ** m * np.real(Y_pos)
    else:
        return np.sqrt(2) * (-1) ** m * np.imag(Y_pos)

def psi(n, l, m, r, theta, phi, Z=1, real=True):
    return radial_wavefunction(n, l, r, Z) * angular_wavefunction(l, m, theta, phi, real)

def prob_density(n, l, m, x, y, z, Z=1, real=True):
    r = np.sqrt(x ** 2 + y ** 2 + z ** 2)
    r_safe = np.where(r == 0, 1e-12, r)
    theta = np.arccos(np.clip(z / r_safe, -1, 1))
    phi = np.arctan2(y, x)
    wf = psi(n, l, m, r, theta, phi, Z, real)
    return np.abs(wf) ** 2

def energy_eV(n, Z=1):
    return -RY_EV * Z ** 2 / n ** 2

def plot_2d_slice(n, l, m, Z=1, extent=8, npts=400, cmap="jet"):
    x = np.linspace(-extent, extent, npts)
    y = np.linspace(-extent, extent, npts)
    X, Y = np.meshgrid(x, y)
    Zc = np.zeros_like(X)

    dens = prob_density(n, l, m, X, Y, Zc, Z)
    dens = dens / dens.max()

    fig, ax = plt.subplots(figsize=(5, 5))
    im = ax.pcolormesh(X, Y, dens, cmap=cmap, shading="auto", vmin=0, vmax=1)
    ax.set_xlabel("x /Angstroms")
    ax.set_ylabel("y /Angstroms")
    ax.set_title(f"z=0 plane Z={Z} A=1 3D L={l} M={m}")
    ax.set_aspect("equal")
    fig.colorbar(im, ax=ax)
    fig.tight_layout()
    return fig

def plot_3d_isosurface(n, l, m, Z=1, extent=10, npts=90, iso_frac=0.15,
                        cmap="jet"):
    grid = np.linspace(-extent, extent, npts)
    X, Y, Zc = np.meshgrid(grid, grid, grid, indexing="ij")

    dens = prob_density(n, l, m, X, Y, Zc, Z)
    dens = dens / dens.max()

    level = iso_frac * dens.max()
    verts, faces, normals, values = measure.marching_cubes(dens, level=level)

    spacing = grid[1] - grid[0]
    verts = verts * spacing + grid[0]

    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, projection="3d")

    face_vals = values[faces].mean(axis=1)
    face_vals = (face_vals - face_vals.min()) / (np.ptp(face_vals) + 1e-12)
    colors = plt.get_cmap(cmap)(face_vals)

    mesh = ax.plot_trisurf(
        verts[:, 0], verts[:, 1], faces, verts[:, 2],
        linewidth=0, antialiased=False, shade=True
    )
    mesh.set_fc(colors)

    ax.set_xlabel("x in Angstroms")
    ax.set_ylabel("y in Angstroms")
    ax.set_zlabel("z in Angstroms")
    E = energy_eV(n, Z)
    ax.set_title(f"Z={Z}, A=1, orbital 3D E={E:.4f}eV\nM={m}")
    fig.tight_layout()
    return fig

def interactive_2d(n0=3, l0=2, m0=-2, Z=1, extent=8, npts=250, cmap="jet"):
    from matplotlib.widgets import Slider

    x = np.linspace(-extent, extent, npts)
    X, Y = np.meshgrid(x, x)
    Zc = np.zeros_like(X)

    fig, ax = plt.subplots(figsize=(6, 7))
    plt.subplots_adjust(bottom=0.28)

    dens = prob_density(n0, l0, m0, X, Y, Zc, Z)
    dens = dens / dens.max()
    im = ax.pcolormesh(X, Y, dens, cmap=cmap, shading="auto", vmin=0, vmax=1)
    ax.set_xlabel("x / angstroms")
    ax.set_ylabel("y / angstroms")
    ax.set_aspect("equal")
    title = ax.set_title(f"z=0 plane Z={Z} A=1 3D L={l0} M={m0}  E={energy_eV(n0,Z):.4f} eV")
    fig.colorbar(im, ax=ax)

    ax_n = plt.axes([0.25, 0.15, 0.55, 0.03])
    ax_l = plt.axes([0.25, 0.10, 0.55, 0.03])
    ax_m = plt.axes([0.25, 0.05, 0.55, 0.03])
    s_n = Slider(ax_n, "n", 1, 6, valinit=n0, valstep=1)
    s_l = Slider(ax_l, "l", 0, 5, valinit=l0, valstep=1)
    s_m = Slider(ax_m, "m", -5, 5, valinit=m0, valstep=1)

    def update(_):
        n = int(s_n.val)
        l = int(min(s_l.val, n - 1))
        m = int(np.clip(s_m.val, -l, l))
        s_l.eventson = False; s_l.set_val(l); s_l.eventson = True
        s_m.eventson = False; s_m.set_val(m); s_m.eventson = True

        dens = prob_density(n, l, m, X, Y, Zc, Z)
        dens = dens / dens.max()
        im.set_array(dens.ravel())
        title.set_text(f"z=0 plane Z={Z} A=1 3D L={l} M={m}  E={energy_eV(n,Z):.4f} eV")
        fig.canvas.draw_idle()

    s_n.on_changed(update)
    s_l.on_changed(update)
    s_m.on_changed(update)
    plt.show()

def interactive_3d(n0=3, l0=2, m0=0, Z=1, extent=10, npts=60, iso_frac=0.15, cmap="jet"):
    """Live-updating 3D isosurface with n/l/m sliders (recomputes on release)."""
    from matplotlib.widgets import Slider

    grid = np.linspace(-extent, extent, npts)
    X, Y, Zc = np.meshgrid(grid, grid, grid, indexing="ij")
    spacing = grid[1] - grid[0]

    def compute_mesh(n, l, m):
        dens = prob_density(n, l, m, X, Y, Zc, Z)
        dens = dens / dens.max()
        level = iso_frac * dens.max()
        verts, faces, normals, values = measure.marching_cubes(dens, level=level)
        verts = verts * spacing + grid[0]
        return verts, faces, values

    fig = plt.figure(figsize=(6, 7))
    plt.subplots_adjust(bottom=0.22)
    ax = fig.add_subplot(111, projection="3d")

    verts, faces, values = compute_mesh(n0, l0, m0)
    mesh = ax.plot_trisurf(verts[:, 0], verts[:, 1], faces, verts[:, 2],
                            linewidth=0, antialiased=False, shade=True, cmap=cmap)
    ax.set_xlabel("x in Angstroms")
    ax.set_ylabel("y in Angstroms")
    ax.set_zlabel("z in Angstroms")
    title = ax.set_title(f"Z={Z}, A=1, orbital 3D E={energy_eV(n0,Z):.4f}eV\nM={m0}")

    ax_n = plt.axes([0.25, 0.12, 0.55, 0.03])
    ax_l = plt.axes([0.25, 0.07, 0.55, 0.03])
    ax_m = plt.axes([0.25, 0.02, 0.55, 0.03])
    s_n = Slider(ax_n, "n", 1, 5, valinit=n0, valstep=1)
    s_l = Slider(ax_l, "l", 0, 4, valinit=l0, valstep=1)
    s_m = Slider(ax_m, "m", -4, 4, valinit=m0, valstep=1)

    def update(_):
        nonlocal mesh
        n = int(s_n.val)
        l = int(min(s_l.val, n - 1))
        m = int(np.clip(s_m.val, -l, l))
        s_l.eventson = False; s_l.set_val(l); s_l.eventson = True
        s_m.eventson = False; s_m.set_val(m); s_m.eventson = True

        mesh.remove()
        verts, faces, values = compute_mesh(n, l, m)
        mesh = ax.plot_trisurf(verts[:, 0], verts[:, 1], faces, verts[:, 2],
                                linewidth=0, antialiased=False, shade=True, cmap=cmap)
        title.set_text(f"Z={Z}, A=1, orbital 3D E={energy_eV(n,Z):.4f}eV\nM={m}")
        fig.canvas.draw_idle()

    s_n.on_changed(update)
    s_l.on_changed(update)
    s_m.on_changed(update)
    plt.show()

if __name__ == "__main__":
    interactive_2d(n0=3, l0=2, m0=-2)
    interactive_3d(n0=3, l0=2, m0=0)
