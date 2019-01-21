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

global printFlag
global logFlag
global is_log_param_set

printFlag = True
logFlag = False
is_log_param_set = False

input_mutex = threading.Lock()

def hexShow(argv):        #十六进制显示方法1
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

def pc_to_stm32_uart_test():
    print('pc_to_stm32_uart_test start')
    pc_com1 = serial.Serial('com1',115200)  
    #print(pc_com1.portstr) 
    strInput = input('enter some words:') 
    try:    #如果输入不是十六进制数据-- 
        n =pc_com1.write(bytes.fromhex(strInput))
    except: #--则将其作为字符串输出
        n =pc_com1.write(bytes(strInput,encoding='utf-8'))
    print('transfer data to stm32')
    #print(n)  
    time.sleep(1)     #sleep() 与 inWaiting() 最好配对使用
    num=pc_com1.inWaiting()
    if num:
        print('recieve data from stm32') 
        try:   #如果读取的不是十六进制数据--
            data= str(binascii.b2a_hex(pc_com1.read(num)))[2:-1] #十六进制显示方法2
            print(data)
            if data != '6920616d2073746d333200':
                print('test failed')
            else:
                print('test successful')
        except: #--则将其作为字符串读取
            str = pc_com1.read(num)
            if str != b'i am stm32\x00':
                print('test failed')
            else:
                print('test successful')   
            hexShow(str)
    else:
        print('nothing recieve...') 
    serial.Serial.close(pc_com1)

def transition_card_to_stm32_uart_test(argv):
    print('pc_to_stm32_uart_test start')
    card_com = serial.Serial(argv,115200)  
    print(card_com.portstr) 
    strInput = input('enter some words:') 
    try:    #如果输入不是十六进制数据-- 
        n =card_com.write(bytes.fromhex(strInput))
    except: #--则将其作为字符串输出
        n =card_com.write(bytes(strInput,encoding='utf-8'))
    print('transfer data to stm32')
    print(n)  
    time.sleep(1)     #sleep() 与 inWaiting() 最好配对使用
    num=card_com.inWaiting()
    print(num)
    if num:
        print('recieve data from stm32') 
        try:   #如果读取的不是十六进制数据--
            data= str(binascii.b2a_hex(card_com.read(num)))[2:-1] #十六进制显示方法2
            print(data)
            if data != '0504030201':
                print('test failed')
            else:
                print('test successful')
        except: #--则将其作为字符串读取
            str = card_com.read(num)
            if str != b'\x05\x04\x03\x02\x01':
                print('test failed')
            else:
                print('test successful')   
            hexShow(str)
            print(str)
    else:
        print('nothing recieve...') 
    serial.Serial.close(card_com)

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

def make_folder(path):
    path=path.strip()
    path=path.rstrip("\\")
    isExists=os.path.exists(path)
    if not isExists:
        os.makedirs(path) 
        return True
    else:
        return False

def del_file(path):
    path=path.strip()
    path=path.rstrip("\\")
    isExists=os.path.exists(path)
    if not isExists:
        return True
    else:
        shutil.rmtree(path)
        return False

def listenThreadFunc():
    global is_log_param_set
    timestampflag = True
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

        if printFlag is True:
            if timestampflag is True:
                #sys.stdout.write('[' + datetime.strftime(datetime.now(), '%H:%M:%S.%f')[0:-3] + '] ')
                timestampflag = False
            try:
                logstr = stmlog.decode()
            except UnicodeDecodeError:
                print(stmlog)
            else:
                if logstr.find('\r\n') >= 0:
                    timestampflag = True
                #sys.stdout.write(logstr)
                sys.stdout.flush()

#主程序
listenThread = threading.Thread(target=listenThreadFunc)
listenThread.setDaemon(True)
listenThread.start()

while (1):
    pc_to_stm32_uart_test()
    #transition_card_to_stm32_uart_test('com6')
    use_com_transfer_what_and_print('com6', 115200, 'aa')
os.system('pause')