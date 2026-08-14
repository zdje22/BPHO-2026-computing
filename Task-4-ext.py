import random
import sys

import pygame

HC_EV_NM = 1239.841984  
METALS = {
    "Silver (Ag)":     4.3,
    "Aluminium (Al)":  4.3,
    "Gold (Au)":       5.1,
    "Copper (Cu)":     4.7,
    "Tin (Sn)":        4.4,
    "Lead (Pb)":       4.3,
    "Tungsten (W)":    4.5,
    "Nickel (Ni)":     4.6,
    "Sodium (Na)":     2.4,
}
METAL_NAMES = list(METALS.keys())

WAVELENGTH_MIN, WAVELENGTH_MAX = 200, 800   # nm
VOLTAGE_MIN, VOLTAGE_MAX = -8.0, 8.0        # volts

WINDOW_W, WINDOW_H = 1100, 700

WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
AXES_BORDER = (30, 30, 30)
GRID_GRAY = (221, 221, 221)
LABEL_GRAY = (90, 90, 90)
SLIDER_TRACK = (200, 200, 200)
SLIDER_FILL = (31, 87, 219)      
SLIDER_MARK = (214, 39, 40)      
BOX_BORDER = (60, 60, 60)
RED_DOT = (214, 39, 40)
STATUS_GREEN = (44, 160, 44)
STATUS_ORANGE = (255, 127, 14)
STATUS_RED = (214, 39, 40)
ELECTRON_BLUE = (31, 87, 219)


def photon_energy_eV(wavelength):
    return HC_EV_NM / wavelength


def max_KE_eV(wavelength, metal):
    return photon_energy_eV(wavelength) - METALS[metal]


def stopping_voltage(wavelength, metal):
    ke = max_KE_eV(wavelength, metal)
    return ke if ke > 0 else 0.0


def wavelength_to_rgb(wavelength):
    w = wavelength
    if w < 380:
        return (140, 90, 255)
    if w > 750:
        return (150, 20, 20)

    if 380 <= w < 440:
        r = -(w - 440) / (440 - 380); g = 0.0; b = 1.0
    elif 440 <= w < 490:
        r = 0.0; g = (w - 440) / (490 - 440); b = 1.0
    elif 490 <= w < 510:
        r = 0.0; g = 1.0; b = -(w - 510) / (510 - 490)
    elif 510 <= w < 580:
        r = (w - 510) / (580 - 510); g = 1.0; b = 0.0
    elif 580 <= w < 645:
        r = 1.0; g = -(w - 645) / (645 - 580); b = 0.0
    else:
        r = 1.0; g = 0.0; b = 0.0

    if 380 <= w < 420:
        factor = 0.3 + 0.7 * (w - 380) / (420 - 380)
    elif 700 <= w <= 750:
        factor = 0.3 + 0.7 * (750 - w) / (750 - 700)
    else:
        factor = 1.0

    return tuple(max(0, min(255, int(255 * c * factor))) for c in (r, g, b))


class Electron:
    __slots__ = ("x", "y", "vx", "vy", "alive", "turned_around")

    def __init__(self, x, y, vx):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = random.uniform(-40, 40)
        self.alive = True
        self.turned_around = False


class Slider:
    """A thin horizontal slider styled like matplotlib.widgets.Slider:
    a gray track, a blue filled bar up to the current value, a thin red
    tick marking the initial value, and the current value printed to
    the right."""

    def __init__(self, x, y, w, min_val, max_val, value, label, fmt="{:.0f}"):
        self.x, self.y, self.w = x, y, w
        self.min_val, self.max_val = min_val, max_val
        self.value = value
        self.init_value = value
        self.label = label
        self.fmt = fmt
        self.dragging = False
        self.h = 14

    def _frac(self, val):
        return (val - self.min_val) / (self.max_val - self.min_val)

    def rect(self):
        return pygame.Rect(self.x, self.y - self.h // 2 - 8, self.w, self.h + 16)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect().collidepoint(event.pos):
                self.dragging = True
                self._set_from_mouse(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._set_from_mouse(event.pos[0])

    def _set_from_mouse(self, mx):
        frac = (mx - self.x) / self.w
        frac = max(0.0, min(1.0, frac))
        self.value = self.min_val + frac * (self.max_val - self.min_val)

    def draw(self, screen, font, label_font):
        label_surf = label_font.render(self.label, True, BLACK)
        screen.blit(label_surf, (self.x - label_surf.get_width() - 14, self.y - label_surf.get_height() // 2))

        track_rect = pygame.Rect(self.x, self.y - self.h // 2, self.w, self.h)
        pygame.draw.rect(screen, SLIDER_TRACK, track_rect)

        fill_w = int(self.w * self._frac(self.value))
        fill_rect = pygame.Rect(self.x, self.y - self.h // 2, max(fill_w, 2), self.h)
        pygame.draw.rect(screen, SLIDER_FILL, fill_rect)

        pygame.draw.rect(screen, BOX_BORDER, track_rect, 1)

        init_x = self.x + self.w * self._frac(self.init_value)
        pygame.draw.line(screen, SLIDER_MARK, (init_x, self.y - self.h // 2 - 2),
                          (init_x, self.y + self.h // 2 + 2), 2)

        val_surf = font.render(self.fmt.format(self.value), True, BLACK)
        screen.blit(val_surf, (self.x + self.w + 12, self.y - val_surf.get_height() // 2))


class RadioGroup:
    def __init__(self, x, y, options, selected, spacing=24):
        self.x, self.y = x, y
        self.options = options
        self.selected = selected
        self.spacing = spacing

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for i, opt in enumerate(self.options):
                oy = self.y + i * self.spacing
                if self.x - 8 <= mx <= self.x + 200 and oy - 10 <= my <= oy + 10:
                    self.selected = opt

    def draw(self, screen, font):
        for i, opt in enumerate(self.options):
            oy = self.y + i * self.spacing
            is_sel = opt == self.selected
            pygame.draw.circle(screen, BLACK, (self.x, oy), 6, 0 if is_sel else 1)
            label_color = BLACK if is_sel else LABEL_GRAY
            screen.blit(font.render(opt, True, label_color), (self.x + 16, oy - 8))


class Button:
    """A simple black-bordered, white-filled button like a matplotlib
    Button widget."""

    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.hovered = False

    def handle_event(self, event):
        clicked = False
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                clicked = True
        return clicked

    def draw(self, screen, font):
        fill = (230, 230, 230) if self.hovered else WHITE
        pygame.draw.rect(screen, fill, self.rect)
        pygame.draw.rect(screen, BOX_BORDER, self.rect, 1)
        txt = font.render(self.text, True, BLACK)
        screen.blit(txt, txt.get_rect(center=self.rect.center))


class App:
    def __init__(self):
        pygame.init()
        self.fullscreen = False
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H), pygame.RESIZABLE)
        pygame.display.set_caption("Photoelectric Effect Simulation")
        self.canvas = pygame.Surface((WINDOW_W, WINDOW_H))
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("dejavusans", 14)
        self.font_small = pygame.font.SysFont("dejavusans", 12)
        self.font_bold = pygame.font.SysFont("dejavusans", 14, bold=True)
        self.font_title = pygame.font.SysFont("dejavusans", 18, bold=True)

        self.axes_rect = pygame.Rect(40, 55, 700, 480)

        self.plate_x = self.axes_rect.x + 110
        self.collector_x = self.axes_rect.x + 560
        self.plate_top = self.axes_rect.y + 40
        self.plate_bottom = self.axes_rect.y + 400

        self.electrons = []
        self.spawn_accumulator = 0.0
        self.current_indicator = 0.0
        self.paused = False

        right_x = self.axes_rect.right + 30
        self.metal_label_pos = (right_x, 60)
        self.radio = RadioGroup(right_x, 90, METAL_NAMES, METAL_NAMES[0])

        readout_y = 90 + len(METAL_NAMES) * 24 + 20
        self.readout_boxes_y = readout_y
        self.readout_box = pygame.Rect(right_x, readout_y, WINDOW_W - right_x - 30, 150)

        self.pause_btn = Button(right_x, readout_y + 165, 130, 34, "Pause")
        self.reset_btn = Button(right_x + 145, readout_y + 165, 130, 34, "Reset")
        self.fullscreen_btn = Button(right_x, readout_y + 209, 275, 34, "Fullscreen (F11)")

        slider_x = 170
        slider_w = 650
        self.wl_slider = Slider(slider_x, WINDOW_H - 60, slider_w, WAVELENGTH_MIN, WAVELENGTH_MAX,
                                 250, "Wavelength (nm)", fmt="{:.0f}")
        self.v_slider = Slider(slider_x, WINDOW_H - 25, slider_w, VOLTAGE_MIN, VOLTAGE_MAX,
                                0.0, "Voltage (V)", fmt="{:+.1f}")

    def step(self, dt):
        if self.paused:
            return

        wavelength = self.wl_slider.value
        voltage = self.v_slider.value
        metal = self.radio.selected
        ke = max_KE_eV(wavelength, metal)

        collected_this_frame = 0

        if ke > 0:
            self.spawn_accumulator += 55 * dt
            while self.spawn_accumulator >= 1.0:
                self.spawn_accumulator -= 1.0
                y0 = random.uniform(self.plate_top + 15, self.plate_bottom - 15)
                speed = 40 + 260 * min(ke / 4.0, 1.0)
                self.electrons.append(Electron(self.plate_x + 10, y0, speed))

        accel = voltage * 55.0

        for e in self.electrons:
            if not e.alive:
                continue
            e.vx += accel * dt
            e.x += e.vx * dt
            e.y += e.vy * dt

            if e.vx <= 0 and e.x <= self.plate_x + 18 and not e.turned_around:
                e.alive = False
                continue
            if e.vx < -2:
                e.turned_around = True

            if e.x >= self.collector_x - 12:
                e.alive = False
                collected_this_frame += 1
            if e.y < self.plate_top or e.y > self.plate_bottom:
                e.alive = False

        self.electrons = [e for e in self.electrons if e.alive]
        if len(self.electrons) > 400:
            self.electrons = self.electrons[-400:]

        self.current_indicator = 0.85 * self.current_indicator + 0.15 * (collected_this_frame * 12)

    def draw_scene(self):
        screen = self.canvas
        wavelength = self.wl_slider.value
        voltage = self.v_slider.value
        metal = self.radio.selected
        ke = max_KE_eV(wavelength, metal)
        beam_color = wavelength_to_rgb(wavelength)

        pygame.draw.rect(screen, WHITE, self.axes_rect)
        pygame.draw.rect(screen, AXES_BORDER, self.axes_rect, 1)

        title = self.font_title.render("Photoelectric Effect Simulation", True, BLACK)
        screen.blit(title, (self.axes_rect.x, self.axes_rect.y - 32))

        for gx in range(self.axes_rect.left + 70, self.axes_rect.right, 70):
            pygame.draw.line(screen, GRID_GRAY, (gx, self.axes_rect.top + 1), (gx, self.axes_rect.bottom - 1), 1)

        mid_y = (self.plate_top + self.plate_bottom) // 2
        for dy in (-90, -30, 30, 90):
            start = (self.axes_rect.x + 10, mid_y + dy)
            end = (self.plate_x, mid_y + int(dy * 0.5))
            pygame.draw.line(screen, beam_color, start, end, 2)
        pygame.draw.rect(screen, (235, 235, 235), (self.axes_rect.x + 5, mid_y - 25, 20, 50))
        pygame.draw.rect(screen, AXES_BORDER, (self.axes_rect.x + 5, mid_y - 25, 20, 50), 1)

        plate_fill = (255, 221, 87) if ke > 0 else (180, 180, 180)
        pygame.draw.rect(screen, plate_fill, (self.plate_x, self.plate_top, 12, self.plate_bottom - self.plate_top))
        pygame.draw.rect(screen, AXES_BORDER, (self.plate_x, self.plate_top, 12, self.plate_bottom - self.plate_top), 1)
        screen.blit(self.font_small.render("TARGET", True, LABEL_GRAY), (self.plate_x - 18, self.plate_top - 18))

        pygame.draw.rect(screen, (190, 190, 190), (self.collector_x, self.plate_top, 12, self.plate_bottom - self.plate_top))
        pygame.draw.rect(screen, AXES_BORDER, (self.collector_x, self.plate_top, 12, self.plate_bottom - self.plate_top), 1)
        screen.blit(self.font_small.render("COLLECTOR", True, LABEL_GRAY), (self.collector_x - 20, self.plate_top - 18))

        wy = self.plate_bottom + 25
        pygame.draw.line(screen, LABEL_GRAY, (self.plate_x + 6, self.plate_bottom), (self.plate_x + 6, wy), 1)
        pygame.draw.line(screen, LABEL_GRAY, (self.plate_x + 6, wy), (self.collector_x + 6, wy), 1)
        pygame.draw.line(screen, LABEL_GRAY, (self.collector_x + 6, wy), (self.collector_x + 6, self.plate_bottom), 1)
        vtxt = self.font_bold.render(f"V = {voltage:+.1f} V", True, BLACK)
        screen.blit(vtxt, ((self.plate_x + self.collector_x) // 2 - 35, wy + 8))

        for e in self.electrons:
            pygame.draw.circle(screen, ELECTRON_BLUE, (int(e.x), int(e.y)), 3)

        if self.paused:
            screen.blit(self.font_bold.render("PAUSED", True, STATUS_RED), (self.axes_rect.right - 90, self.axes_rect.top + 8))

    def draw_panel(self):
        screen = self.canvas

        legend_x = self.axes_rect.right - 130
        legend_y = self.axes_rect.top + 10
        pygame.draw.circle(screen, RED_DOT, (legend_x, legend_y), 4)
        screen.blit(self.font_small.render("Emitted e-", True, BLACK), (legend_x + 10, legend_y - 7))

        screen.blit(self.font_bold.render("Target Metal", True, BLACK), self.metal_label_pos)
        self.radio.draw(screen, self.font)

        rb = self.readout_box
        pygame.draw.rect(screen, WHITE, rb)
        pygame.draw.rect(screen, BOX_BORDER, rb, 1)

        wavelength = self.wl_slider.value
        voltage = self.v_slider.value
        metal = self.radio.selected
        E = photon_energy_eV(wavelength)
        W = METALS[metal]
        ke = E - W
        vstop = ke if ke > 0 else 0.0

        rows = [
            (f"Photon Energy: {E:.2f} eV", BLACK),
            (f"Work Function: {W:.2f} eV", BLACK),
            (f"Max Electron KE: {ke:.2f} eV" if ke > 0 else "Max Electron KE: 0.00 eV", BLACK),
            (f"Stopping Voltage: {vstop:.2f} V", BLACK),
        ]
        if ke <= 0:
            status, scolor = "Status: No emission", STATUS_RED
        elif voltage <= -vstop:
            status, scolor = "Status: Electrons repelled", STATUS_ORANGE
        else:
            status, scolor = "Status: Photocurrent flowing", STATUS_GREEN
        rows.append((status, scolor))
        rows.append((f"Relative Current: {max(self.current_indicator, 0):.2f}", BLACK))

        yy = rb.y + 10
        for text, color in rows:
            screen.blit(self.font.render(text, True, color), (rb.x + 10, yy))
            yy += 24

        self.pause_btn.draw(screen, self.font)
        self.reset_btn.draw(screen, self.font)
        self.fullscreen_btn.draw(screen, self.font)

    def draw_sliders(self):
        self.wl_slider.draw(self.canvas, self.font, self.font_bold)
        self.v_slider.draw(self.canvas, self.font, self.font_bold)

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H), pygame.RESIZABLE)

    def _update_transform(self):
        sw, sh = self.screen.get_size()
        self.scale = min(sw / WINDOW_W, sh / WINDOW_H)
        scaled_w, scaled_h = WINDOW_W * self.scale, WINDOW_H * self.scale
        self.offset_x = (sw - scaled_w) / 2
        self.offset_y = (sh - scaled_h) / 2

    def _translate_event(self, event):
        """Return a version of `event` whose .pos (if any) is converted from
        real window coordinates into fixed canvas coordinates, so widgets
        keep working the same regardless of window size or fullscreen."""
        if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            mx, my = event.pos
            cx = (mx - self.offset_x) / self.scale
            cy = (my - self.offset_y) / self.scale
            ns = pygame.event.Event(event.type, pos=(cx, cy),
                                     button=getattr(event, "button", None))
            return ns
        return event

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0
            self._update_transform()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE and not self.fullscreen:
                    self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        self.toggle_fullscreen()
                    elif event.key == pygame.K_ESCAPE and self.fullscreen:
                        self.toggle_fullscreen()

                te = self._translate_event(event)
                self.wl_slider.handle_event(te)
                self.v_slider.handle_event(te)
                self.radio.handle_event(te)
                if self.pause_btn.handle_event(te):
                    self.paused = not self.paused
                    self.pause_btn.text = "Play" if self.paused else "Pause"
                if self.reset_btn.handle_event(te):
                    self.electrons.clear()
                    self.spawn_accumulator = 0.0
                    self.current_indicator = 0.0
                if self.fullscreen_btn.handle_event(te):
                    self.toggle_fullscreen()

            self.step(dt)

            self.canvas.fill(WHITE)
            self.draw_scene()
            self.draw_panel()
            self.draw_sliders()

            self.screen.fill((30, 30, 30))
            scaled_w, scaled_h = int(WINDOW_W * self.scale), int(WINDOW_H * self.scale)
            scaled = pygame.transform.smoothscale(self.canvas, (scaled_w, scaled_h))
            self.screen.blit(scaled, (self.offset_x, self.offset_y))
            pygame.display.flip()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    App().run()