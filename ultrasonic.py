import time
import board
import neopixel
import adafruit_hcsr04
import random

pixel_pin = board.GP5
num_pixels = 216
sonar = adafruit_hcsr04.HCSR04(trigger_pin=board.GP0, echo_pin=board.GP1)

MAX_BRIGHTNESS = 0.95
MIN_BRIGHTNESS = 0.1
GESTURE_ZONE = 10  # cm, maximum distance for gesture detection
BRIGHTNESS_MIN = 10  # cm, minimum distance for brightness control
BRIGHTNESS_MAX = 40  # cm, maximum distance for brightness control
EASING_FACTOR = 0.75

# Adjusted constants for gesture detection
GESTURE_THRESHOLD = 5  # cm, decreased for more sensitive gestures in the smaller zone
GESTURE_TIME = 0.3  # seconds, decreased for quicker response
GESTURE_COOLDOWN = 1.0  # seconds, prevent rapid successive gestures
MAX_MODES = 8  # Increased for our new fabulous modes

# Initialize with minimum brightness
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=MIN_BRIGHTNESS, auto_write=False)

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)

def color_chase(color, wait):
    start_time = time.monotonic()
    for i in range(num_pixels):
        pixels[i] = color
        while time.monotonic() - start_time < wait:
            pass
        start_time = time.monotonic()
        pixels.show()

def rainbow_cycle(j):
    for i in range(num_pixels):
        rc_index = (i * 256 // num_pixels) + j
        pixels[i] = wheel(rc_index & 255)
    pixels.show()

def set_all(color):
    for i in range(num_pixels):
        pixels[i] = color
    pixels.show()

def set_gradient(color):
    mid_point = num_pixels // 2
    for i in range(mid_point):
        # Gradually decrease the brightness towards the edges
        factor = i / mid_point
        darker_color = tuple([int(c * (1 - factor)) for c in color])
        lighter_color = tuple([min(int(c * (1 + factor)), 255) for c in color])
        pixels[mid_point - i - 1] = darker_color
        pixels[mid_point + i] = lighter_color
    # If there are an odd number of pixels, set the middle one to the base color
    if num_pixels % 2 == 1:
        pixels[mid_point] = color
    pixels.show()

def update_brightness(distance, current_brightness, last_set_brightness):
    if BRIGHTNESS_MIN <= distance <= BRIGHTNESS_MAX:
        range_percentage = (distance - BRIGHTNESS_MIN) / (BRIGHTNESS_MAX - BRIGHTNESS_MIN)
        target_brightness = MIN_BRIGHTNESS + (MAX_BRIGHTNESS - MIN_BRIGHTNESS) * (1 - range_percentage)
        new_brightness = current_brightness + (target_brightness - current_brightness) * EASING_FACTOR
        return new_brightness, new_brightness
    elif distance > BRIGHTNESS_MAX:
        return current_brightness, last_set_brightness
    else:
        new_brightness = current_brightness + (last_set_brightness - current_brightness) * EASING_FACTOR
        return new_brightness, last_set_brightness

def detect_gesture(distance, last_distance, last_gesture_time):
    current_time = time.monotonic()
    if (distance <= GESTURE_ZONE and
        abs(distance - last_distance) > GESTURE_THRESHOLD and 
        current_time - last_gesture_time > GESTURE_COOLDOWN):
        return True, current_time
    return False, last_gesture_time

def update_mode(current_mode):
    return (current_mode + 1) % MAX_MODES

def cyberpunk_pulse(speed=0.05):
    colors = [(0, 255, 255), (255, 0, 255), (255, 255, 0)]  # Cyan, Magenta, Yellow
    for color in colors:
        for i in range(100):
            brightness = abs((i - 50) / 50)  # Creates a pulse effect
            adjusted_color = tuple(int(c * brightness) for c in color)
            set_all(adjusted_color)
            time.sleep(speed)

def matrix_rain(speed=0.1):
    for i in range(num_pixels):
        if random.random() < 0.1:  # 10% chance for each pixel to start a drop
            pixels[i] = (0, 255, 0)  # Bright green
        elif pixels[i][1] > 0:  # If the pixel is part of a drop
            pixels[i] = (0, max(pixels[i][1] - 10, 0), 0)  # Fade out
    pixels.show()
    time.sleep(speed)

def ai_heartbeat(speed=0.5):
    for _ in range(2):  # Double pulse
        for i in range(0, 255, 15):
            set_all((i, 0, i))  # Purple pulse
            time.sleep(speed/30)
        for i in range(255, 0, -15):
            set_all((i, 0, i))
            time.sleep(speed/30)
    time.sleep(speed)

def quantum_fluctuation(speed=0.05):
    for _ in range(50):
        for i in range(num_pixels):
            if random.random() < 0.2:  # 20% chance to change each pixel
                pixels[i] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        pixels.show()
        time.sleep(speed)

def claude_approved(speed=0.1):
    colors = [(128, 0, 128), (75, 0, 130), (0, 0, 255)]  # Purple, Indigo, Blue
    for color in colors:
        set_gradient(color)
        time.sleep(speed * 10)

last_sensor_check = time.monotonic()
rainbow_index = 0
current_brightness = MIN_BRIGHTNESS
last_set_brightness = MAX_BRIGHTNESS
current_mode = 0
last_distance = 0
last_gesture_time = 0

while True:
    current_time = time.monotonic()
    if current_time - last_sensor_check >= 0.05:
        try:
            distance = sonar.distance
            
            # Gesture detection (only in the gesture zone)
            if distance <= GESTURE_ZONE:
                gesture_detected, last_gesture_time = detect_gesture(distance, last_distance, last_gesture_time)
                if gesture_detected:
                    current_mode = update_mode(current_mode)
                    print(f"Gesture detected! Switching to mode {current_mode}")
            
            # Brightness control (only in the brightness control zone)
            elif BRIGHTNESS_MIN <= distance <= BRIGHTNESS_MAX:
                current_brightness, last_set_brightness = update_brightness(distance, current_brightness, last_set_brightness)
                pixels.brightness = current_brightness
            
            print(f"Mode: {current_mode}, Distance: {distance:.2f} cm, Brightness: {current_brightness:.2f}")
            
            last_distance = distance
        except RuntimeError:
            print("Sensor reading failed. Retrying!")
        last_sensor_check = current_time

    # Different behaviors based on the current mode
    if current_mode == 0:
        rainbow_cycle(rainbow_index)
        rainbow_index = (rainbow_index + 1) % 256
    elif current_mode == 1:
        set_all((125, 100, 0))  # Nice Sun Orange
    elif current_mode == 2:
        set_all((0, 20, 255))  # Cyberdeck Blue
    elif current_mode == 3:
        cyberpunk_pulse()
    elif current_mode == 4:
        matrix_rain()
    elif current_mode == 5:
        ai_heartbeat()
    elif current_mode == 6:
        quantum_fluctuation()
    elif current_mode == 7:
        claude_approved()

    time.sleep(0.001)
