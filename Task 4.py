import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import EngFormatter
from matplotlib.widgets import CheckButtons

h = 6.62607015e-34      
c = 299792458.0         
e = 1.602176634e-19    

metals = {
    'Silver': 4.3,
    'Aluminum': 4.3,
    'Gold': 5.1,
    'Copper': 4.7,
    'Tin': 4.4,
    'Lead': 4.3,
    'Tungsten': 4.5,
    'Nickel': 4.6,
    'Sodium': 2.4,
}

lam_min_nm = 200.0  
lam_max_nm = 900.0  
lam_nm = np.linspace(lam_min_nm, lam_max_nm, 1500)
lam_m = lam_nm * 1e-9
freq = c / lam_m 

fig, ax = plt.subplots(figsize=(9, 6))

lines = []
dotted_lines = []
labels = []
for name, phi_eV in metals.items():
    labels.append(name)
    phi_J = phi_eV * e
    f_thresh = phi_J / h
    V_raw = (h * freq - phi_J) / e
    V_solid = np.where(V_raw > 0, V_raw, np.nan)
    V_dotted = np.where(V_raw <= 0, V_raw, np.nan)
    ln, = ax.plot(freq, V_solid, label=f"{name} (phi={phi_eV:.2f} eV)")
    ln_dot, = ax.plot(freq, V_dotted, ls=':', color=ln.get_color(), alpha=0.8)
    lines.append(ln)
    dotted_lines.append(ln_dot)


ax.set_xlabel('Frequency (Hz)')
ax.set_ylabel('Stopping potential V_stop (V)')
ax.set_title('Photoelectric Stopping Voltage vs Frequency for Various Metals')
ax.grid(True, which='both', ls='--', alpha=0.5)
leg = ax.legend(loc='upper left', bbox_to_anchor=(1.01, 1))

ax.xaxis.set_major_formatter(EngFormatter(unit='Hz'))

plt.tight_layout()

threshold_lines = []
for name, phi_eV in metals.items():
    phi_J = phi_eV * e
    f_thresh = phi_J / h
    threshold_lines.append(f"{name}: {f_thresh/1e12:.2f} THz")
threshold_text = "\n".join(threshold_lines)
fig.text(0.78, 0.45, threshold_text, fontsize=9, va='center', ha='left',
         bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

check_ax = fig.add_axes([0.76, 0.1, 0.12, 0.18])
checks = CheckButtons(check_ax, labels, [ln.get_visible() for ln in lines])

legend_lines = leg.get_lines() if leg is not None else []

def toggle(label):
    idx = labels.index(label)
    vis = not lines[idx].get_visible()
    lines[idx].set_visible(vis)
    if idx < len(dotted_lines):
        dotted_lines[idx].set_visible(vis)
    if idx < len(legend_lines):
        legend_lines[idx].set_alpha(1.0 if vis else 0.2)
    plt.draw()

checks.on_clicked(toggle)

plt.show()
