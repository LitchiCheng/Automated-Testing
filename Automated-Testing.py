import os 
import serial
import serial.tools.list_ports
import binascii
import time

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

pc_to_stm32_uart_test()
#transition_card_to_stm32_uart_test('com6')
use_com_transfer_what_and_print('com6', 115200, 'aa')
os.system('pause')