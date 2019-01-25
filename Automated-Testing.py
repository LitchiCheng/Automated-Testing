import os 
import serial
import serial.tools.list_ports
import binascii
import time
import socket
import struct
import signal
import threading
from datetime import datetime
import sys
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import WordCompleter
import logging
import shutil
from logging.handlers import RotatingFileHandler

global is_log_param_set
is_log_param_set = False

input_mutex = threading.Lock()

#十六进制显示
def hexShow(argv):        
    try:
        result = ''  
        hLen = len(argv)  
        for i in range(hLen):  
            hvol = argv[i]
            hhex = '%02x'%hvol  
            result += hhex+' '  
        print('hexShow:',result)
    except:
        pass

#pc到stm32的测试
def pc_to_stm32_232_test(argv):
    print('pc_to_stm32_232_test start')
    pc_com1 = serial.Serial(argv,115200)  
    strInput = 'CC' 
    try:    
        n =pc_com1.write(bytes.fromhex(strInput))
    except: 
        n =pc_com1.write(bytes(strInput,encoding='utf-8'))
    print('232 transfer data to stm32')  
    time.sleep(1)    
    num=pc_com1.inWaiting()
    if num:
        print('232 recieve data from stm32') 
        try:   
            data= str(binascii.b2a_hex(pc_com1.read(num)))[2:-1] 
            print(data)
            if data != '6920616d2073746d333200':
                print('232 test failed')
            else:
                print('232 test successful')
        except: 
            str = pc_com1.read(num)
            if str != b'i am stm32\x00':
                print('232 test failed')
            else:
                print('232 test successful')   
            hexShow(str)
    else:
        print('232 nothing recieve...') 
    serial.Serial.close(pc_com1)

#485卡到stm32的测试
def transition_card_to_stm32_485_test(argv):
    print('transition_card_to_stm32_485_test start')
    card_com = serial.Serial(argv,115200)  
    strInput = 'AA' 
    try:   
        n =card_com.write(bytes.fromhex(strInput))
    except: 
        n =card_com.write(bytes(strInput,encoding='utf-8'))
    print('485 transfer data to stm32')
    time.sleep(1)   
    num=card_com.inWaiting()
    if num:
        print('485 recieve data from stm32') 
        try:   
            data= str(binascii.b2a_hex(card_com.read(num)))[2:-1] 
            print(data)
            if data != '0504030201':
                print('485 test failed')
            else:
                print('485 test successful')
        except:
            str = card_com.read(num)
            if str != b'\x05\x04\x03\x02\x01':
                print('485 test failed')
            else:
                print('485 test successful')   
            hexShow(str)
            print(str)
    else:
        print('485 nothing recieve...') 
    serial.Serial.close(card_com)

#232卡到stm32的测试
def transition_card_to_stm32_232_test(argv):
    print('transition_card_to_stm32_232_test start')
    card_com = serial.Serial(argv,115200)   
    strInput = 'BB'
    try:   
        n =card_com.write(bytes.fromhex(strInput))
    except: 
        n =card_com.write(bytes(strInput,encoding='utf-8'))
    print('232 transfer data to stm32')
    time.sleep(1)   
    num=card_com.inWaiting()
    if num:
        print('232 recieve data from stm32') 
        try:   
            data= str(binascii.b2a_hex(card_com.read(num)))[2:-1] 
            print(data)
            if data != '0102030405':
                print('232 test failed')
            else:
                print('232 test successful')
        except:
            str = card_com.read(num)
            if str != b'\x01\x02\x03\x04\x05':
                print('232 test failed')
            else:
                print('232 test successful')   
            hexShow(str)
            print(str)
    else:
        print('232 nothing recieve...') 
    serial.Serial.close(card_com)

#通用串口测试
def use_com_transfer_what_and_print(com, baudrate, what):
    use_com = serial.Serial(com,baudrate)  
    print(use_com.portstr) 
    try:   
        n =use_com.write(bytes.fromhex(what))
    except: 
        n =use_com.write(bytes(what,encoding='utf-8'))  
    time.sleep(1) 
    num=use_com.inWaiting()
    if num:
        try:  
            data= str(binascii.b2a_hex(use_com.read(num)))[2:-1]
            print(data)
            #在这里判断
        except:
            str = use_com.read(num)
            #在这里判断   
            hexShow(str)
    else:
        print('nothing recieve...') 
    serial.Serial.close(use_com)

#创建文件夹
def make_folder(path):
    path=path.strip()
    path=path.rstrip("\\")
    isExists=os.path.exists(path)
    if not isExists:
        os.makedirs(path) 
        return True
    else:
        return False

#删除文件夹
def del_file(path):
    path=path.strip()
    path=path.rstrip("\\")
    isExists=os.path.exists(path)
    if not isExists:
        return True
    else:
        shutil.rmtree(path)
        return False

#udp监听
def listenThreadFunc():
    global is_log_param_set
    local_addr = ('', 4999)
    so = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    so.settimeout(0.05)
    try:
        so.bind(local_addr)
    except OSError:
        print('There is already an app blind the port, press enter to exit...')
        sys.exit()
    print('Local> Listening to local port %d' % local_addr[1])

    mkpath="\\Automated-Testing-Log\\"
    pwd = os.getcwd()
    pwd = pwd.replace('\\','\\\\')
    out_address = pwd + mkpath
    del_file(out_address)

    while True:
        try:
            (stmlog, addr) = so.recvfrom(1000)
        except socket.timeout:
            continue
        except NameError:
            quit()
        
        if is_log_param_set is False:
            make_folder(out_address)
            logger = logging.getLogger(__name__)
            logger.setLevel(level = logging.INFO)
            rHandler = RotatingFileHandler((out_address+"log.txt"), maxBytes = 20*1024*1024,backupCount = 10)
            rHandler.setLevel(logging.INFO)
            formatter = logging.Formatter('[%(asctime)s] - %(message)s')
            rHandler.setFormatter(formatter)
            logger.addHandler(rHandler)
            is_log_param_set = True         
        try:
            str_to_log = stmlog.decode()
        except UnicodeDecodeError:
            print(stmlog)
        logger.info(str_to_log)

#modbus_tcp_io板模拟操作
import modbus_tk
import modbus_tk.defines as modbus_define
import modbus_tk.modbus_tcp as modbus_tcp
class modbus_tcp_toolkit():
    def __init__(self, slave_ip_str, slave_id_int = 1):
        self.master = modbus_tcp.TcpMaster(host=slave_ip_str)
        self.master.set_timeout(5.0)
    def readHoldRegister(self, slave_id_int = 1, first_register_id_int = 0, register_num_int = 0):
        self.master.execute(slave_id_int, modbus_define.READ_HOLDING_REGISTERS, first_register_id_int, register_num_int)
    def readInputRegister(self, slave_id_int = 1, first_register_id_int = 0, register_num_int = 0):
        self.master.execute(slave_id_int, modbus_define.READ_INPUT_REGISTERS, first_register_id_int, register_num_int)
    def readCoilsRegister(self, slave_id_int = 1, first_register_id_int = 0, register_num_int = 0):
        self.master.execute(slave_id_int, modbus_define.READ_COILS, first_register_id_int, register_num_int)
    def readDiscreteRegister(self, slave_id_int = 1, first_register_id_int = 0, register_num_int = 0):
        self.master.execute(slave_id_int, modbus_define.READ_DISCRETE_INPUTS, first_register_id_int, register_num_int)
    def writeSingleHoldRegister(self, slave_id_int = 1, first_register_id_int = 0, register_value_int = 0):
        self.master.execute(slave_id_int, modbus_define.WRITE_SINGLE_REGISTER, first_register_id_int, output_value = regiter_value_int)
    def writeSingleCoilRegister(self, slave_id_int = 1, first_register_id_int = 0, register_value_int = 0):
        self.master.execute(slave_id_int, modbus_define.WRITE_SINGLE_COIL, first_register_id_int, output_value = register_value_int)
    def writeMultipleHoldRegister(self, slave_id_int = 1, first_register_id_int = 0, register_value_int_arrary = [0,0,0,0,0,0,0,0]):
        self.master.execute(slave_id_int, modbus_define.WRITE_MULTIPLE_REGISTERS, first_register_id_int, output_value = register_value_int_arrary)
    def writeMultipleCoilRegister(self, slave_id_int = 1, first_register_id_int = 0, register_value_int_arrary = [0,0,0,0,0,0,0,0]):
        self.master.execute(slave_id_int, modbus_define.WRITE_MULTIPLE_COILS, first_register_id_int, output_value = register_value_int_arrary)

#主程序
listenThread = threading.Thread(target=listenThreadFunc)
listenThread.setDaemon(True)
listenThread.start()

modbus_master = modbus_tcp_toolkit('192.168.192.111')

while (1):
    pc_to_stm32_232_test('com1')
    transition_card_to_stm32_485_test('com6')
    transition_card_to_stm32_232_test('com6')
    modbus_master.writeSingleCoilRegister(1,0,1)
    time.sleep(1)
    modbus_master.writeSingleCoilRegister()
os.system('pause')