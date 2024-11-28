import time
import network
import socket
import re
import json
import machine
import os
from machine import Pin, PWM, UART

led = Pin("LED", Pin.OUT)

servo1 = PWM(Pin(15))
servo1.freq(50)

servo2 = PWM(Pin(17))
servo2.freq(50)

# Para mover el servomotor se tiene desde 500000 hasta 2500000 con 180 grados, siendo 500000 = 0° y 2500000 = 180°
# 1° = 11111

# Para cada interruptor habría que desplazarse en un rango de 83333 (esto es teniendo en cuenta que la posicion inicial es en el interruptor 1)

# Para el movimiento total entre interruptores va desde 500000 hasta 1750000

pos01 = 500000
pos02 = 620000
pos03 = 710000
pos04 = 780000
pos05 = 850000
pos06 = 916675
pos07 = 1000010
pos08 = 1090000
pos09 = 1160000
pos10 = 1240000
pos11 = 1320000
pos12 = 1410000
pos13 = 1500000
pos14 = 1560000
pos15 = 1666690
pos16 = 1740000

posiciones = [pos01, pos02, pos03, pos04, pos05, pos06, pos07, pos08, pos09, pos10, pos11, pos12, pos13, pos14, pos15, pos16]

ssid = ""
password = ""
# Conexión

uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))
uart.init(9600, bits = 8, parity=None, stop=1, tx=Pin(0), rx=Pin(1))

def mostrarMenu():
    uart.write('Bienvenido\n')
    uart.write('1. Conectar a la ultima red usada\n')
    uart.write('2. Listar redes disponibles\n')

def escanearRedes(wlan):
    redes = wlan.scan()
    if redes:
        uart.write('Redes wifi disponibles:\n')
        for red in redes:
            ssid = red[0].decode('utf-8')
            uart.write(f'SSID: {ssid} \n')
        return True        
    else:
        uart.write('No se encontraron redes WiFi disponibles. \n')
        return False





def On():
    # Pasar de posicion neutra a ON
    led.on()
    for pulso in range(1300000, 2000000, 10000):
        servo2.duty_ns(pulso)
        time.sleep_ms(10)
    led.off()
    time.sleep_ms(100)

    # Pasar de ON a posicion neutra
    led.on()
    for pulso in range(2000000, 1300000, -10000):
        servo2.duty_ns(pulso)
        time.sleep_ms(10)
    led.off()
    time.sleep_ms(100)

def Off():
    # Pasar de posicion neutra a OFF
    led.on()
    for pulso in range(1300000, 500000, -10000):
        servo2.duty_ns(pulso)
        time.sleep_ms(10)
    led.off()
    time.sleep_ms(100)

    #  Pasar de OFF a posicion neutra
    led.on()
    for pulso in range(500000, 1300000, 10000):
        servo2.duty_ns(pulso)
        time.sleep_ms(10)
    led.off()
    time.sleep_ms(100)

def Movimiento(pos, accion):
    pos = posiciones[pos-1]
    
    #if pos == pos01 or pos == pos02 or pos == pos03 or pos == pos04 or pos == pos05:
    led.on()
    for pulso in range(pos01, pos, 10000):
        servo1.duty_ns(pulso)
        time.sleep_ms(20)
    led.off()
    time.sleep_ms(500)

    if accion == "ON" or accion == "on":
        On()
    elif accion == "OFF" or accion == "off":
        Off()

    led.on()
    for pulso in range(pos, pos01, -10000):
        servo1.duty_ns(pulso)
        time.sleep_ms(20)
    led.off()
    time.sleep_ms(500)
    
    
def funcionamientoHTTP():
    cl, addr = s.accept()
    print('cliente conectado desde', addr)
    request = cl.recv(1024)
    request = str(request)
    
    instruccion = re.search(r'\?(.*?)\ HTTP',request)
    
    instruccion_str = instruccion.group(1)
    numeros = []
    instrucciones = []
    
    for par in instruccion_str.split('&'):
        if '=' in par:
            numero, inst = par.split('=')
            numeros.append(int(numero))
            instrucciones.append(inst)
    
    for i in range(0,len(numeros),1):
        if str(instrucciones[i]) == "ON" or str(instrucciones[i]) == "on":
            print('Activando interruptor ' + str(int(numeros[i])))
            uart.write('Activando interruptor ' + str(int(numeros[i])) + '\n')
        elif str(instrucciones[i]) == "OFF" or str(instrucciones[i]) == "off":
            print('Desactivando interruptor ' + str(int(numeros[i])))
            uart.write('Desactivando interruptor ' + str(int(numeros[i])) + '\n')
        Movimiento(numeros[i], instrucciones[i])
     
    cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
    cl.close()
    print("Petición HTTP terminada")
    uart.write('Petición HTTP terminada\n')
    return 0

def funcionamientoRS232():
    if uart.any():
        instr = uart.readline()
        print(instr)
        instr = str(instr.decode('utf-8')).strip()
        numeros = []
        instrucciones = []
        
        for par in instr.split('&'):
            if '=' in par:
                numero, inst = par.split('=')
                numeros.append(int(numero))
                instrucciones.append(inst)
        
        for i in range(0,len(numeros),1):
            if str(instrucciones[i]) == "ON" or str(instrucciones[i]) == "on":
                print('Activando interruptor ' + str(int(numeros[i])))
                uart.write('Activando interruptor ' + str(int(numeros[i])) + '\n')
            elif str(instrucciones[i]) == "OFF" or str(instrucciones[i]) == "off":
                print('Desactivando interruptor ' + str(int(numeros[i])))
                uart.write('Desactivando interruptor ' + str(int(numeros[i])) + '\n')
            Movimiento(numeros[i], instrucciones[i])
        
        print("Petición RS232 terminada")
        uart.write('Petición RS232 terminada\n')
        return 0

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if wlan.isconnected():
    wlan.disconnect()



mostrarMenu()
while uart.any():
    uart.read()
while not uart.any():
    time.sleep(0.1)
opcion = uart.read(1).decode('utf-8').strip()
uart.write(f'Opción seleccionada: {opcion}\n')
uart.read()
if opcion == '1':
    
    with open("datos.json", "r") as f:
        datos = json.load(f)
        ssid = datos.get('ssid')
        password = datos.get('password')
        
    wlan.active(True)
    wlan.connect(ssid, password)

elif opcion == '2':
    if escanearRedes(wlan):
        uart.write('Ingrese el SSID: ')
        while not uart.any():
            time.sleep(0.1)
        ssid = uart.readline()
        uart.read()
            
            
            
        uart.write('Ingrese la contraseña: ')
        while not uart.any():
            time.sleep(0.1)
        password = uart.readline()
        uart.read()
        
        ssid = ssid.strip()
        password = password.strip()
        
        ssid = str(ssid.decode('utf-8'))
        password = str(password.decode('utf-8'))
        wlan.active(True)
        wlan.connect(ssid, password)
        datos = {"ssid": ssid, "password": password}
        with open("datos.json", "w") as f:
            json.dump(datos, f)
    else:
        machine.reset()


#Tiempo de espera para conexión

max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    uart.write('Conectando a ' + ssid + '\n')
    print('Conectando a ' + ssid)
    time.sleep_ms(1000)
    
#Manejo de error de conexión

if wlan.status() != 3:
    uart.write('Error al conectar a ' + ssid + '\n')
    print('Error al conectar a ' + ssid)
    machine.reset()
else:
    uart.write('Conectado a ' + ssid + '\n')
    print('Conectado a ' + ssid + '\n')
    led.on()
    status = wlan.ifconfig()
    uart.write('ip = ' + status[0] + '\n')
    print( 'ip = ' + status[0] )
    time.sleep_ms(1000)
    led.off()
    
#Open socket
    
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)
s.settimeout(5)
print('escuchando en', addr)

vez = 0
while True:
    if vez == 0:
        uart.write('Esperando petición...\n')
        while uart.any():
            uart.read()
        vez = 1
    try:
        vez = funcionamientoHTTP()
    except:
        vez = funcionamientoRS232()