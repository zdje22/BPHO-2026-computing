import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button

def randomwalk(N, s):
    x = np.zeros(N)
    y = np.zeros(N)
    for i in range(1, N):
        theta = np.random.rand() * 2 * np.pi
        x[i] = x[i-1] + s * np.cos(theta)
        y[i] = y[i-1] + s * np.sin(theta)
    return x, y


def plot_random_walk(N, s=1.0):
    x, y = randomwalk(N, s)
    line.set_data(x, y)
    end_scatter.set_offsets([[x[-1], y[-1]]])
    distance = np.hypot(x[-1], y[-1])
    dist_text.set_text(f"Distance: {distance:.2f}")
    ax.set_title(f"2D Random Walk ({N} Steps)")
    ax.relim()
    ax.autoscale_view()
    fig.canvas.draw_idle()


initial_N = 1000
fig, ax = plt.subplots(figsize=(8, 8))
plt.subplots_adjust(bottom=0.22, right=0.75)

x, y = randomwalk(initial_N, 1.0)
line, = ax.plot(x, y, lw=0.5, color='blue')
start_scatter = ax.scatter(0, 0, color='red', label='Start')
end_scatter = ax.scatter(x[-1], y[-1], color='black', label='End')
ax.set_title(f"2D Random Walk ({initial_N} Steps)")
ax.legend()
ax.axis('equal')
distance = np.hypot(x[-1], y[-1])
dist_text = fig.text(0.78, 0.55, f"Distance: {distance:.2f}", fontsize=11, va='center', ha='left', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

slider_ax = fig.add_axes([0.15, 0.10, 0.7, 0.03])
step_slider = Slider(
    ax=slider_ax,
    label='Number of steps',
    valmin=5,
    valmax=10000,
    valinit=initial_N,
    valstep=5,
    color='blue',
)

slider_ax2 = fig.add_axes([0.15, 0.05, 0.55, 0.03])
s_slider = Slider(
    ax=slider_ax2,
    label='step size',
    valmin=0.1,
    valmax=5.0,
    valinit=1.0,
    valstep=0.1,
    color='blue',
)

button_ax = fig.add_axes([0.78, 0.45, 0.13, 0.04])
reset_button = Button(button_ax, 'Reset',color='white', hovercolor='lightblue')


def update(val):
    N = int(step_slider.val)
    s = s_slider.val
    plot_random_walk(N, s)


def reset(event):
    step_slider.reset()
    s_slider.reset()
    plot_random_walk(initial_N, s_slider.val)

step_slider.on_changed(update)
s_slider.on_changed(update)
reset_button.on_clicked(reset)
plt.show()