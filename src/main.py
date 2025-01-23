from mqtt import Mqtt
from openmower import Openmower
import json
from display import Display
from pimoroni import Button, RGBLED
import utime

class App:

    def __init__(self):
        self.buttonA = Button(12)
        self.buttonB = Button(13)
        self.buttonX = Button(14)
        self.buttonY = Button(15)
        self.led = RGBLED(6,7,8)
        self.led.set_rgb(0,0,0)
        self.display = Display()        
        self.mqtt = Mqtt(self.mqtt_message_received, Openmower.topics.get_all(), self.display.draw_print_message)
        self.init_display()

    def init_display(self):
        self.display.clear()
        self.display.draw_background()
        self.display.draw_splash()
        self.mqtt.connect()
        self.display.draw_header()

    def mqtt_message_received(self, topic, message):
        if topic == Openmower.topics.actions.b_name:
            Openmower.set_actions(json.loads(message))
            self.display.draw_icons(Openmower.actions)
        elif topic == Openmower.topics.robot_state.b_name:
            self.display.draw_mower_state(json.loads(message))
        elif topic == Openmower.topics.v_battery.b_name:
            self.display.draw_battery_voltage(message)

    def mqtt_publish_message(self, topic, message):
        self.mqtt.publish_message(topic, message)
        
    def sleep(self):
        if not self.display.isAsleep:
            self.display.sleep()
    
    def wake(self):
        self.display.wake()

app = App()
last_use = utime.ticks_ms()
last_connection_check = utime.ticks_ms()

while True:    
    now = utime.ticks_ms()
    if utime.ticks_diff(now, last_use) >= 60000:
        app.sleep()
        if app.buttonA.read() or app.buttonB.read() or app.buttonX.read() or app.buttonY.read():
            last_use = utime.ticks_ms()
            app.wake()
    else:
        if app.buttonA.read():
            if Openmower.actions.start_mowing.enabled:
                app.mqtt_publish_message("action", Openmower.actions.start_mowing.id)
            elif Openmower.actions.pause_mowing.enabled:
                app.mqtt_publish_message("action", Openmower.actions.pause_mowing.id)
            elif Openmower.actions.continue_mowing.enabled:
                app.mqtt_publish_message("action", Openmower.actions.continue_mowing.id)

            last_use = utime.ticks_ms()
        if app.buttonB.read():           
            if Openmower.actions.skip_area.enabled:
                app.mqtt_publish_message("action", Openmower.actions.skip_area.id)
            
            last_use = utime.ticks_ms()
        if app.buttonX.read():                
            if Openmower.actions.abort_mowing.enabled:
                app.mqtt_publish_message("action", Openmower.actions.abort_mowing.id)

            last_use = utime.ticks_ms()
        if app.buttonY.read():                
            if Openmower.actions.reset_emergency.enabled:
                app.mqtt_publish_message("action", Openmower.actions.reset_emergency.id)

            last_use = utime.ticks_ms()
    
    if utime.ticks_diff(now, last_connection_check) >= 2000:
        if not app.mqtt.is_connected():
            app.init_display()
        last_connection_check = utime.ticks_ms()

    try:
        app.mqtt.check_message()
    except:
        utime.sleep(2)

    utime.sleep(0.1)
