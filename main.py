import re
import sys
import time

from dp100_ctrl import Dp100

def main(argv):

    if len(argv) == 0:
        dp100.status()
        sys.exit(0)

    for param in argv:
        if re.search('off', param, re.IGNORECASE):
            dp100.set(output=False)
        if re.search('on', param, re.IGNORECASE):
            dp100.set(output=True)
        if re.search('[0-9]+V', param, re.IGNORECASE):
            dp100.set(vset=int(param[:-1])*1000)
        if re.search('[0-9]+mV', param, re.IGNORECASE):
            dp100.set(vset=int(param[:-2]))
        if re.search('[0-9]+A', param, re.IGNORECASE):
            dp100.set(iset=int(param[:-1])*1000)
        if re.search('[0-9]+mA', param, re.IGNORECASE):
            dp100.set(iset=int(param[:-2]))

    dp100.basic_set()

if __name__ == '__main__':
    try:
        dp100 = Dp100()
    except:
        print("Could not communicate to device")
        sys.exit(1)

    print(f"Device Manufacturer: {dp100.device.manufacturer}")
    print(f"Device Serial: {dp100.device.serial}")
    main(sys.argv[1:])
