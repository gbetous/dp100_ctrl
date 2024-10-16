import hid
import crcmod
import time

class Dp100:
    VID = 0x00
    PID = 0x00

    DR_H2D          = 0xFB
    DR_D2H          = 0xFA

    OP_NONE         = 0x00
    OP_DEVICEINFO   = 0x10
    OP_BASICINFO    = 0x30
    OP_BASICSET     = 0x35
    OP_SYSTEMINFO   = 0x40
    OP_SCANOUT      = 0x50
    OP_SERIALOUT    = 0x55

    vin     = 0 # unit: mV
    vout    = 0 # unit: mV
    iout    = 0 # unit: mA
    vo_max  = 0 # unit: mV
    temp1   = 0 # unit: 0.1 dgree
    temp2   = 0 # unit: 0.1 dgree
    dc_5v   = 0 # unit: mV
    out_mode= 0 # 0x00 : constant current / 0x01 : constant voltage / 0x02 : disabled
    work_st = 0 # unknown

    dev_type= ""
    hdw_ver = 0
    app_ver = 0
    boot_ver= 0
    run_area= 0
    dev_sn  = bytes([])
    year    = 0
    month   = 0
    day     = 0

    blk_lev = 0
    opp     = 0 # unit: mV
    opt     = 0 # unit: 0.1 dgree
    vol_lev = 0 

    index   = 0
    state   = 0 # 0:off; 1:on
    vo_set  = 0 # unit: mV
    io_set  = 0 # unit: mA
    ovp_set = 0 # unit: mV
    ocp_set = 0 # unit: mA

    SET_MODIFY = 0x20
    SET_ACT    = 0x80

    def __init__(self, vid=0x2e3c, pid=0xaf01):
        self.VID = vid
        self.PID = pid
        self.device = hid.Device(self.VID, self.PID)
        self.crc16 = crcmod.mkCrcFun(0x18005, rev=True, initCrc=0xFFFF, xorOut=0x0000)

    def out_mode_str(self):
        if self.out_mode == 0x00:
            return "Constant Current"
        if self.out_mode == 0x01:
            return "Constant Voltage"
        if self.out_mode == 0x02:
            return "Disabled"

    def gen_frame(self, op_code, data=bytes([])): 
        frame = bytes([self.DR_H2D, op_code&0xFF, 0x0, len(data)&0xFF])+data
        #print(frame)
        crc = self.crc16(frame)
        return (frame+bytes([crc&0xFF,(crc>>8)&0xFF]))

    def check_frame(self, data): 

        #print(data)
        if(data[0] == self.DR_D2H):
            op = data[1]
            data_len = data[3]
            if (self.crc16(data[0:4+data_len+2])==0): # correct if return 0
                raw_data = data[4:4+data_len]
                # print(raw_data)
                if(op == self.OP_BASICINFO):
                    self.vin     = (raw_data[1]<<8) |raw_data[0]
                    self.vout    = (raw_data[3]<<8) |raw_data[2]
                    self.iout    = (raw_data[5]<<8) |raw_data[4]
                    self.vo_max  = (raw_data[7]<<8) |raw_data[6]
                    self.temp1   = (raw_data[9]<<8) |raw_data[8]
                    self.temp2   = (raw_data[11]<<8)|raw_data[10]
                    self.dc_5v   = (raw_data[13]<<8)|raw_data[12]
                    self.out_mode= raw_data[14]
                    self.work_st = raw_data[15]
                    print("BASICINFO:")
                    print(f"       Vin : {self.vin/1000}V")
                    print(f"      Vout : {self.vout/1000}V")
                    print(f"      Iout : {self.iout}mA")
                    print(f"   VoutMax : {self.vo_max/1000}V")
                    print(f"     Temp1 : {self.temp1/10}°C")
                    print(f"     Temp2 : {self.temp2/10}°C")
                    print(f"     DC 5V : {self.dc_5v/1000}V")
                    print(f"  Out Mode : {self.out_mode_str()}")
                    return 1
                elif(op == self.OP_DEVICEINFO):
                    self.dev_type = raw_data[0:15].split(b'\x00')[0].decode("utf-8")
                    self.hdw_ver  = (raw_data[17]<<8) |raw_data[16] # origin:11 means 1.1
                    self.app_ver  = (raw_data[19]<<8) |raw_data[18] # origin:11 means 1.1
                    self.boot_ver = (raw_data[21]<<8) |raw_data[20]
                    self.run_area = (raw_data[23]<<8) |raw_data[22]
                    self.dev_sn   = raw_data[24:24+11]
                    self.year     = (raw_data[37]<<8) |raw_data[36]
                    self.month    = raw_data[38]
                    self.day      = raw_data[39]
                    print("DEVICEINFO:")
                    print(f"          Device Type : {self.dev_type}")
                    print(f"     Hardware Version : {self.hdw_ver/10}")
                    print(f"  Application Version : {self.app_ver/10}")
                    print(f"         Boot Version : {self.boot_ver/10}")
                    #print(f"Run Area : {self.run_area}")
                    #print(f"Serial Number : {self.dev_sn.decode('utf-8')}")
                    #print(f"Serial Number : {self.dev_sn}")
                    print(f"                 Year : {self.year}")
                    print(f"                Month : {self.month}")
                    print(f"                  Day : {self.day}")
                    return 1
                elif(op == self.OP_SYSTEMINFO):
                    self.blk_lev  = raw_data[0]      # backlight
                    self.opp      = (raw_data[2]<<8) |raw_data[1] # over power
                    self.opt      = (raw_data[4]<<8) |raw_data[3] # over temperature
                    self.vol_lev  = raw_data[5]      # beep volumn
                    print("SYSTEMINFO:")
                    print(f"   Backlight Level : {self.blk_lev}")
                    print(f"        Over Power : {self.opp}mA")
                    print(f"  Over Temperature : {self.opt/10}°C")
                    print(f"        Beep Volum : {self.vol_lev}")
                    return 1
                elif(op == self.OP_BASICSET):
                    if(data_len==1):
                        return -2
                    else:
                        self.index    = raw_data[0] 
                        self.state    = raw_data[1] 
                        self.vo_set   = (raw_data[3]<<8) |raw_data[2]
                        self.io_set   = (raw_data[5]<<8) |raw_data[4]
                        self.ovp_set  = (raw_data[7]<<8) |raw_data[6]
                        self.ocp_set  = (raw_data[9]<<8) |raw_data[8]
                        #print("BASICSET", self.index, self.state, self.vo_set, self.io_set, self.ovp_set, self.ocp_set)
                        print("BASICSET:")
                        print(f"         Index : {self.index}")
                        print(f"         State : {self.state}")
                        print(f"          Vout : {self.vo_set/1000}V")
                        print(f"          Iout : {self.vo_set}mA")
                        print(f"  Over Voltage : {self.ovp_set/1000}V")
                        print(f"  Over Current : {self.ocp_set}mA")
                        return 1
                else:
                    return -1
            else:
                print("CRC ERROR")
                return 0

    def gen_set(self, output, vset, iset, ovp, ocp):
        if(output):
            output=1
        else:
            output=0
        return bytes([self.SET_MODIFY, output, vset&0xFF, (vset>>8)&0xFF, iset&0xFF, (iset>>8)&0xFF,
            ovp&0xFF, (ovp>>8)&0xFF, ocp&0xFF, (ocp>>8)&0xFF])

    def status(self):
        self.device.write(self.gen_frame(self.OP_BASICINFO))
        time.sleep(0.05)
        self.check_frame(self.device.read(64))

    def device_info(self):
        self.device.write(self.gen_frame(self.OP_DEVICEINFO))
        time.sleep(0.05)
        self.check_frame(self.device.read(64))

    def system_info(self):
        self.device.write(self.gen_frame(self.OP_SYSTEMINFO))
        time.sleep(0.05)
        self.check_frame(self.device.read(64))

    def basic_set(self):
        self.device.write(self.gen_frame(self.OP_BASICSET, bytes([0x80])))
        time.sleep(0.05)
        self.check_frame(self.device.read(64))

    def set(self, output = -1, vset = -1, iset = -1, ovp = -1, ocp = -1):
        self.basic_set()
        time.sleep(0.1)
        if output == -1:
            output = self.state
        if vset == -1:
            vset = self.vo_set
        if iset == -1:
            iset = self.io_set
        if ovp == -1:
            ovp = self.ovp_set
        if ocp == -1:
            ocp = self.ocp_set
        self.device.write(self.gen_frame(self.OP_BASICSET, self.gen_set(output, vset, iset, ovp, ocp)))
        time.sleep(0.05)
        self.check_frame(self.device.read(64))
