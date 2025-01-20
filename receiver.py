from machine import UART, Pin
import binascii
import time


text = """There is coffee all over the world. Increasingly, in a world in which
   computing is ubiquitous, the computists want to make coffee."""

text = text.replace(" ","")

# Initialisiere UART für Kommunikation mit dem Arduino Mega
uart = UART(0, baudrate=9600)  # Passe die Pins entsprechend an
uart.init(9600, bits=8, parity=None, stop=1) # init with given parameters

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

def send_data(m):
    uart.write(m)

def receive_data():
    if uart.any():
      try:
        received_message = uart.read().decode('utf-8')
        received_message_list = received_message.split(";")
        print(received_message_list)
        message = received_message_list[2]
        crc = received_message_list[1]
        sequence_number = received_message_list[0]   
        calculated_crc8 = '{:X}'.format(calculate_crc8(message))
        print("calculate_crc8: " + str(calculated_crc8) + " crc: " + str(crc))
        global index
        global length_substring
        global errors
        global text
        test_text = text[index:index+length_substring]
        if (crc) == str(calculated_crc8):
          print("CORRECT")
          print(test_text)
          print(message)
          if str(test_text) != str(message):
            global lost_errors
            lost_errors += 1
            print("str(test_text): " + str(test_text) + "str(message)" + str(message))
            print("lost errors:" + str(lost_errors))
          ack_message = sequence_number + ";" + "ACK"
          send_data(ack_message)
          print("Sent: " + str(ack_message))
          if index < len(text):
            index += length_substring
        else:
          print("WRONG")
          errors += 1
          print("errors:" + str(errors))
      except UnicodeError:
        global sequence
        ack_message = str(0) + ";" + "ACK"
        send_data(ack_message)
        print("UniCodeError")
        
index = 0
length_substring = 10
lost_errors = 0
errors = 0
end = False
while True:
    receive_data()
