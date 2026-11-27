#!/usr/bin/env python3
import os
import time

LED_PATH = "/sys/class/leds/platform::micmute/brightness"

def find_battery():
    ps_path = "/sys/class/power_supply"
    if not os.path.exists(ps_path):
        return None
    for name in os.listdir(ps_path):
        if name.startswith("BAT"):
            return os.path.join(ps_path, name)
    return None

def find_ac():
    ps_path = "/sys/class/power_supply"
    if not os.path.exists(ps_path):
        return None
    for name in os.listdir(ps_path):
        type_file = os.path.join(ps_path, name, "type")
        if os.path.exists(type_file):
            try:
                with open(type_file, "r") as f:
                    if f.read().strip() == "Mains":
                        return os.path.join(ps_path, name, "online")
            except Exception:
                pass
    return None

def get_status():
    bat_dir = find_battery()
    capacity = 50
    is_charging = False

    if bat_dir:
        try:
            with open(os.path.join(bat_dir, "capacity"), "r") as f:
                capacity = int(f.read().strip())
        except Exception:
            pass

        try:
            with open(os.path.join(bat_dir, "status"), "r") as f:
                status = f.read().strip().lower()
                is_charging = (status == "charging")
        except Exception:
            pass

    return capacity, is_charging

def set_led(state):
    try:
        with open(LED_PATH, "w") as f:
            f.write(str(int(state)))
    except Exception:
        pass

def main():
    if not find_battery():
        print("No battery found on this device")
        return

    while True:
        capacity, is_charging = get_status()

        if is_charging:
            # Solid on
            set_led(1)
            time.sleep(2)  # check status every 2 seconds
        elif capacity < 30:
            # Low battery warning: 1s on, 1s off
            set_led(1)
            time.sleep(1.0)
            set_led(0)
            time.sleep(1.0)
        else:
            # Normal state: 0.2s on, 5s off
            set_led(1)
            time.sleep(0.2)
            set_led(0)
            time.sleep(5.0)

if __name__ == "__main__":
    main()