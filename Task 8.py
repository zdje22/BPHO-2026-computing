import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

def classical_mismatch(theta_deg, phi_deg):
    theta = np.radians(theta_deg)
    phi = np.radians(phi_deg)
    p_match = (np.cos(theta) ** 2) * (np.cos(phi) ** 2) + \
              (np.sin(theta) ** 2) * (np.sin(phi) ** 2)
    return 1 - p_match

def quantum_mismatch(theta_deg, phi_deg):
    delta = np.radians(phi_deg - theta_deg)
    return np.sin(delta) ** 2

fig = plt.figure(figsize=(8.5, 8.5))

ax_a = fig.add_axes([0.08, 0.55, 0.38, 0.38])
ax_b = fig.add_axes([0.54, 0.55, 0.38, 0.38])

for ax, label in ((ax_a, "Detector A"), (ax_b, "Detector B")):
    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-1.3, 1.3)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(label, fontsize=12, fontweight="bold")
    circle = plt.Circle((0, 0), 1.0, fill=False, color="lightgray", lw=1)
    ax.add_patch(circle)
    ax.annotate("", xy=(1.15, 0), xytext=(-1.15, 0),
                arrowprops=dict(arrowstyle="-", color="lightgray", lw=1))
    ax.annotate("", xy=(0, 1.15), xytext=(0, -1.15),
                arrowprops=dict(arrowstyle="-", color="lightgray", lw=1))

arrow_a = ax_a.annotate("", xy=(1, 0), xytext=(0, 0),
                         arrowprops=dict(arrowstyle="-|>", color="#34985F",
                                          lw=3, mutation_scale=20))
arrow_a_neg = ax_a.annotate("", xy=(-1, 0), xytext=(0, 0),
                             arrowprops=dict(arrowstyle="-", color="#34985F",
                                              lw=3))
theta_text = ax_a.text(0, -1.25, "", ha="center", fontsize=11)

arrow_b = ax_b.annotate("", xy=(1, 0), xytext=(0, 0),
                         arrowprops=dict(arrowstyle="-|>", color="#3A70DB",
                                          lw=3, mutation_scale=20))
arrow_b_neg = ax_b.annotate("", xy=(-1, 0), xytext=(0, 0),
                             arrowprops=dict(arrowstyle="-", color="#3A70DB",
                                              lw=3))
phi_text = ax_b.text(0, -1.25, "", ha="center", fontsize=11)

ax_prob = fig.add_axes([0.08, 0.30, 0.84, 0.16])
ax_prob.axis("off")

bar_classical = ax_prob.barh([1], [0.0], color="#CF5831", height=0.5)
bar_quantum = ax_prob.barh([0], [0.0], color="#378ADD", height=0.5)
ax_prob.set_xlim(0, 1)
ax_prob.set_ylim(-0.6, 1.6)
ax_prob.set_yticks([0, 1])
ax_prob.set_yticklabels(["Quantum", "Classical"], fontsize=11)
ax_prob.set_xlabel("P(mismatch)")
ax_prob.axvline(0, color="black", lw=0.8)

label_classical = ax_prob.text(0.02, 1, "", va="center", fontsize=11,
                                fontweight="bold")
label_quantum = ax_prob.text(0.02, 0, "", va="center", fontsize=11,
                              fontweight="bold")

ax_theta = fig.add_axes([0.15, 0.14, 0.7, 0.03])
ax_phi = fig.add_axes([0.15, 0.08, 0.7, 0.03])

s_theta = Slider(ax_theta, r"$\theta$ (deg)", -180, 180, valinit=30, valstep=1)
s_phi = Slider(ax_phi, r"$\phi$ (deg)", -180, 180, valinit=0, valstep=1)


def update(_event=None):
    theta = s_theta.val
    phi = s_phi.val

    tr = np.radians(theta)
    pr = np.radians(phi)

    arrow_a.xy = (np.cos(tr), np.sin(tr))
    arrow_a_neg.xy = (-np.cos(tr), -np.sin(tr))
    theta_text.set_text(rf"$\theta$ = {theta:.0f}$^\circ$")

    arrow_b.xy = (np.cos(pr), np.sin(pr))
    arrow_b_neg.xy = (-np.cos(pr), -np.sin(pr))
    phi_text.set_text(rf"$\phi$ = {phi:.0f}$^\circ$")

    p_cl = classical_mismatch(theta, phi)
    p_qm = quantum_mismatch(theta, phi)

    bar_classical[0].set_width(p_cl)
    bar_quantum[0].set_width(p_qm)

    label_classical.set_text(f"Classical: {p_cl * 100:.1f}%")
    label_quantum.set_text(f"Quantum: {p_qm * 100:.1f}%")

    fig.canvas.draw_idle()


s_theta.on_changed(update)
s_phi.on_changed(update)
update()

fig.suptitle("Quantum cryptography",
             fontsize=14, fontweight="bold", y=0.99)

if __name__ == "__main__":
    plt.show()
