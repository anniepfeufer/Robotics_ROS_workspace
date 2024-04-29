# april 28
import network
from time import sleep
import utime
from wifi import ssid, key
import socket
import struct
import ustruct
import machine
from machine import Pin, Timer, disable_irq, enable_irq, time_pulse_us
import json

# testing high/low with button
buttonPinNo = 15
buttonPin = None
ledPin = None
trigger_pin_number = 2
#trigger_pin = None
echo_pin_number = 3
#echo_pin = None
speed_of_sound = 340

def debounceButton(pin):
    utime.sleep_ms(50)
    return pin.value()

def setup():
    global buttonPin, ledPin
    buttonPin= Pin(buttonPinNo, Pin.IN, Pin.PULL_DOWN)
    #trigger_pin = Pin(trigger_pin_number, Pin.OUT)
    #echo_pin = Pin(echo_pin_number, Pin.IN)
    ledPin= Pin("LED", Pin.OUT)
    
def measure_distance():
    #Trigger the sensor by pulling the trigger pin high for 10 microseconds
    t_pin = Pin(trigger_pin_number, Pin.OUT)
    t_pin.on()
    utime.sleep_us(10)
    t_pin.off()
    
    #Wait for the echo pin to go high and measure the pulse duration
    e_pin = Pin(echo_pin_number, Pin.IN)
    pulse_duration = time_pulse_us(e_pin, 1, 38000) #38ms timeout
    
    if pulse_duration < 0:
        print("Timeout occurred. No object in range.")
        return None
    
    #calculate the distance using the speed of sound and pulse duration
    distance = (pulse_duration / 2) * (speed_of_sound / 1000000)
    return distance

'''
led=None
temperature_pin=4
temperature_sensor=None

def setup_pins():
    global led, temperature_sensor
    temperature_sensor=machine.ADC(temperature_pin)
    led=machine.Pin("LED", machine.Pin.OUT)
    
'''
        
def connect_wifi():
    wlan=network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, key)
    while wlan.isconnected() == False:
        print("waiting for connection")
        sleep(1)
    print("connected")
    print(wlan.ifconfig())
    return wlan

connect_wifi()

def get_addr(url, port):
    addr_info=socket.getaddrinfo(url, port)
    print(addr_info)
    addr=addr_info[-1][-1]
    return addr

'''

def get_temperature():
    analog_reading= temperature_sensor.read_u16()
    voltage=3.3 * analog_reading / 65535
    celsius = 27 - (voltage - 0.706)/0.001721
    return 32 + 1.8*celsius
    
'''

def read_forever(addr):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(addr)
    print("connected")
    while True:
        #print("waiting for data")
        length_prefix= recv_all(s,4)
        message_length= struct.unpack('>I', length_prefix)[0]
        message=recv_all(s,message_length)
        decoded_msg = message.decode()
        handle_msg(decoded_msg)
        
        ultrasonic=measure_distance()#soon to be ultrasonic
        button=debounceButton(buttonPin)
        encoded_data=json.dumps({'us':ultrasonic, 'button':button}).encode()
        message_length=len(encoded_data)
        length_prefix= ustruct.pack('>I', message_length)
        s.sendall(length_prefix + encoded_data)
        #print(f"got {decoded_msg}")
        #data = s.recv(1024)
        #print(str(data, 'utf8'), end='')
    return

def recv_all(sock, length):
    data=b''
    while len(data) < length:
        more=sock.recv(length-len(data))
        if not more:
            print("connection hung up")
            raise OSError("read is too short")
        data+=more
    return data

def handle_msg(msg):
    global led
    if msg=="LED":
        ledPin.toggle()
    else:
        print(msg)

#server= '1.tcp.ngrok.io'
setup()
addr= ("10.143.173.24", 8001)
read_forever(addr)