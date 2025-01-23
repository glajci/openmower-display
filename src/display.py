import gc
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY_2
from pngdec import PNG
from openmower import Actions

class Display:

    def __init__(self):
        gc.enable()
        self.display = PicoGraphics(display=DISPLAY_PICO_DISPLAY_2, rotate=0)
        self.width, self.height = self.display.get_bounds()    
        self.eraser_pen = self.background_Pen = self.display.create_pen(250, 250, 250)
        self.font_pen = self.display.create_pen(33, 33, 33)
        self.header_pen = self.display.create_pen(3, 169, 244)
        self.display.set_backlight(0.7)
        self.png = PNG(self.display)
        self.png.open_file("icons.png")
        self.emergency = False
        self.actions: Actions

    def clear(self):
        self.isAsleep = True
        self.display.set_pen(self.eraser_pen)
        self.display.clear()
        self.display.update()
    
    def draw_background(self):
        self.isAsleep = False
        self.display.set_pen(self.header_pen)
        self.display.rectangle(0, 0, self.width, self.height)
        self.display.set_pen(self.background_Pen)
        self.display.rectangle(0, 40, self.width, self.height - 2 * 40)
        self.display.update()

    def draw_splash(self):
        self.png.decode(int((self.width - 236) / 2), 95, source = (400, 0, 236, 40))
        self.display.update()
        gc.collect()

    def draw_header(self):
        self.png.decode(0, 0, source = (400, 40, 164, 32))
        self.display.update()
        gc.collect()

    def draw_icons(self, actions: Actions):
        self.actions = actions

        if actions.start_mowing.enabled or actions.continue_mowing.enabled:
            self.draw_icon_a(0, 0)
        elif actions.pause_mowing.enabled:
            self.draw_icon_a(40, 0)
        else:
            self.draw_icon_a(0, 40)

        self.draw_icon_b(120, 0 if actions.skip_area.enabled else 40)
        self.draw_icon_x(80, 0 if actions.abort_mowing.enabled else 40)
        self.draw_icon_y(160, 0 if actions.skip_path.enabled else 40)

    def draw_icon_a(self, png_x, png_y):
        self.draw_icon(0, 40, png_x, png_y)

    def draw_icon_b(self, png_x, png_y):
        self.draw_icon(0, self.height - 2 * 40, png_x, png_y)

    def draw_icon_x(self, png_x, png_y):
        self.draw_icon(self.width - 40, 40, png_x, png_y)

    def draw_icon_y(self, png_x, png_y):
        self.draw_icon(self.width - 40, self.height - 2 * 40, png_x, png_y)

    def draw_icon(self, x, y, png_x, png_y):
        self.display.set_pen(self.eraser_pen)
        self.display.rectangle(x, y, 40, 40)
        self.png.decode(x, y, source = (png_x, png_y, 40, 40))
        gc.collect()     

    def draw_mower_state(self, state):
        self.draw_mower_status(state['current_state'])
        self.draw_emergency(state['emergency'])
        self.draw_gps(state['pose']['pos_accuracy'], state['gps_percentage'])
        self.draw_battery(state['battery_percentage'], state['is_charging'])
        self.display.update()

    def draw_mower_status(self, status):
        scale = 4
        state_text_width = self.display.measure_text(status, scale)
        self.display.set_pen(self.eraser_pen)
        self.display.rectangle(0, int(self.height / 2 - scale*6 / 2) - 10, self.width, scale*6 + 10)
        self.display.set_pen(self.font_pen)
        self.display.text(status, int(self.width / 2 - state_text_width / 2), int(self.height / 2 - scale*6 / 2), self.width, scale)

    def draw_emergency(self, emergency: bool):
        if emergency == self.emergency: return
        self.emergency = emergency
        if emergency:
            self.draw_icon_y(200, 0)
        else:
            self.draw_icon_y(160, 0 if self.actions.skip_path.enabled else 40)

    def draw_gps(self, accuracy, percentage):
        if accuracy <= 0.05:
            self.draw_icon(50, 40, 200, 40)
        elif accuracy <= 0.2:
            self.draw_icon(50, 40, 240, 40)
        else:
            self.draw_icon(50, 40, 240, 0)

        scale = 2
        self.display.set_pen(self.eraser_pen)
        self.display.rectangle(100, 44, 60, scale*6)
        self.display.rectangle(100, 44 + 20, 60, scale*6)
        self.display.set_pen(self.font_pen)
        self.display.text(f'{str(round(percentage, 2) * 100)}%', 100, 44, 60, scale)
        self.display.text(f'{str((int(accuracy) + round(accuracy - int(accuracy), 3)) * 100)}cm', 100, 44 + 20, 60, scale)

    def draw_battery(self, percentage, is_charging):
        if percentage < 0.25:
            self.draw_icon(164, 40, 280, 40)
        elif percentage < 0.5:
            self.draw_icon(164, 40, 320, 0)
        elif percentage < 0.75:
            self.draw_icon(164, 40, 320, 40)
        elif percentage < 1:
            self.draw_icon(164, 40, 360, 0)
        else:
            self.draw_icon(164, 40, 360, 40)

        if is_charging:
            self.png.decode(164, 40, source = (280, 0, 40, 40))

        scale = 2
        self.display.set_pen(self.eraser_pen)
        self.display.rectangle(214, 44, 60, scale*6)
        self.display.set_pen(self.font_pen)
        self.display.text(f'{str(round(percentage, 2) * 100)}%', 214, 44, 60, scale)

    def draw_battery_voltage(self, voltage):
        scale = 2
        self.display.set_pen(self.eraser_pen)
        self.display.rectangle(214, 44 + 20, 60, scale*6)
        self.display.set_pen(self.font_pen)
        self.display.text(f'{round(float(voltage.decode()), 1)}V', 214, 44 + 20, 60, scale)
        self.display.update()

    def draw_print_message(self, message):
        scale = 2
        message_width = self.display.measure_text(message, scale)
        self.display.set_pen(self.background_Pen)
        self.display.rectangle(0, int(self.height / 2 + 30 / 2 + 4), self.width, scale*6 + 2)
        self.display.set_pen(self.font_pen)
        self.display.text(message, int(self.width / 2 - message_width / 2), int(self.height / 2 + 30 / 2 + 4), self.width, scale)
        self.display.update()
                
    def sleep(self):
        self.display.set_backlight(0)      
        
    def wake(self):
        self.display.set_backlight(0.7)
