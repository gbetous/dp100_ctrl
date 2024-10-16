# dp100_ctrl

### Dependencies

`pip install -r requitements.txt`

### udev rules

- Check the USB values with `lsusb | grep "ALIENTEK ATK-MDP100"`
- Copy file under /etc/udev/rules.d/
- Restart udev with `sudo udevadm control --reload-rules && sudo udevadm trigger`
- You should now be able to control DP100 without being `root`

# Thanks !

Inspired by zhj@ihep.ac.cn (https://github.com/palzhj/pydp100)
Also thanks to Denis Bodor (Hackable Magazine n°56)
