import sys
import time

from dp100_ctrl import Dp100

if __name__ == '__main__':

    try:
        dp100 = Dp100()
    except:
        print("Could not communicate to device")
        sys.exit(1)

    print(f"Device Manufacturer: {dp100.device.manufacturer}")
    print(f"Device Serial: {dp100.device.serial}")

    dp100.status()
    dp100.set(output=True, vset=12000, iset=500)
    time.sleep(.5)
    dp100.set(output=False)
