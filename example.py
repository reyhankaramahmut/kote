from machine import UART, Pin
import binascii
import time

CRC32POLY = 0x04C11DB7  # CRC-32 Polynom

data_examples = ["ABCD", "EFGH", "IJKL", "MNOP", "QRST", "UVWX", "YZ"]
start_time = 0
timeout_sec = 20
current_sequence_number = 0
last_data = None

def char_to_bits(char):
    bits = []
    for i in range(8):
        bits.append((ord(char) >> (7 - i)) & 1)
    return bits

def calculate_crc8(data: str) -> int:
    byte_data = data.encode('utf-8')    
    crc = 0xFF
    for byte in byte_data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = (crc << 1) ^ 0x07
            else:
                crc <<= 1
            crc &= 0xFF
    return crc

def calculate_crc32(chars):
    crc32 = 0
    for char in chars:
        bits = char_to_bits(char)
        for bit in bits:
            if ((crc32 >> 31) & 1) != bit:
                crc32 = (crc32 << 1) ^ CRC32POLY
            else:
                crc32 = crc32 << 1
            crc32 &= 0xFFFFFFFF  # Sicherstellen, dass crc32 innerhalb von 32 Bits bleibt
    return crc32

# Initialisiere UART für Kommunikation mit dem Arduino Mega
uart = UART(0, baudrate=9600)  # Passe die Pins entsprechend an
uart.init(9600, bits=8, parity=None, stop=1) # init with given parameters

def send_data(data):
    crc_data = calculate_crc8(data)
    crc8_hex = '{:X}'.format(crc_data)
    full_message = str(current_sequence_number) + ";" + str(crc8_hex) + ";" + data
    print('\nData sent: ' + full_message)
    uart.write(full_message)

def receive_data(current_sequence_nr):
  start_time = time.time()
  while True:
    if (time.time() - start_time) > timeout_sec:
      start_time = time.time()
      print("NoACK " + str(current_sequence_nr))
      send_data(last_data)
    if uart.any():
      try:  
        received_message = uart.read().decode('utf-8')
        received_message_list = received_message.split(";")
        #print(received_message_list)
        ack = received_message_list[1]
        sequence_number = received_message_list[0]
        #print(ack)
        #print(sequence_number)
        if str(ack) == "ACK" and str(sequence_number) == str(current_sequence_nr):
          start_time = time.time()
          print("ACK " + str(current_sequence_nr))
          return True
      except UnicodeError:
        print("Received undecodable data")
        return False

while True:
  if len(data_examples) == 0:
    break
  data = data_examples.pop()
  last_data = data
  send_data(data)
  receive_data(current_sequence_number)  
  current_sequence_number += 1