#define CRC32POLY 0x04C11DB7  // CRC-32 Polynom

float bitErrorProbability = 0.015; // Beispiel: 10% Bitfehlerwahrscheinlichkeit
bool dataReceived = false;
String receivedData = "";
String receivedCRC = "";

void setup() {
  Serial.begin(9600);   // USB serial monitor
  Serial1.begin(9600);  // UART1
  Serial2.begin(9600);  // UART2
  Serial.println("Start receiving");
  // Initialisiere den Zufallsgenerator mit einem Seed
  randomSeed(analogRead(0));
}

void loop() {
  String messageFromNano1;
  String messageToNano2;
  if (Serial1.available()) {
    //Serial.println("Serial1.available()");
    messageFromNano1 = Serial1.readString();
    Serial.print("\nNano1Message (Original): ");
    Serial.println(messageFromNano1);

    int firstDelim = messageFromNano1.indexOf(';');
    int secondDelim = messageFromNano1.indexOf(';', firstDelim + 1);

    String message;
    String crc;
    String seqeunceNumber;
    String errorMessage = "";
    if (firstDelim != -1 && secondDelim != -1) {
      seqeunceNumber = messageFromNano1.substring(0, firstDelim);
      crc = messageFromNano1.substring(firstDelim + 1, secondDelim);
      message = messageFromNano1.substring(secondDelim + 1);

      for (int i = 0; i < message.length(); i++) {
        bool currentCharInMessageBits[8];
        bool errorCharInMessageBits[8];

        char currentCharInMessage = message.charAt(i);        
        charToBits(currentCharInMessage, currentCharInMessageBits);
        Serial.print("currentCharInMessage: ");
        Serial.println(currentCharInMessage);
        Serial.print("currentCharInMessage in Bit: ");
        Serial.println(bitsToString(currentCharInMessageBits,8));

        char errorCharInMessage = introduceBitErrors(currentCharInMessage, bitErrorProbability);
        charToBits(errorCharInMessage, errorCharInMessageBits);
        Serial.print("errorCharInMessage: ");
        Serial.println(errorCharInMessage);
        Serial.print("errorCharInMessage in Bit: ");
        Serial.println(bitsToString(errorCharInMessageBits,8));
        errorMessage += errorCharInMessage;
      }
    } 
    else {
      Serial.println("Trennzeichen nicht gefunden.");
    }
    String messageToNano2 = seqeunceNumber + ";" + crc  + ";" + errorMessage;
    Serial.println(messageToNano2);
    //Serial1.write(nanoMessage.c_str());
    //Serial.println("Serial2.available()");
    //String nano2Message = Serial2.readString();
    //Serial.print("\nNano2Message (Original): ");
    //Serial.println(nano2Message);  
    Serial2.write(messageToNano2.c_str(), messageToNano2.length());
    String messageFromNano2 = Serial2.readString();
    Serial.println("messageFromNano2 " + messageFromNano2);
    Serial1.write(messageFromNano2.c_str(), messageFromNano2.length());
    
  }
}

// Funktion zur Einführung von Bitfehlern
char introduceBitErrors(char byte, float probability) {
  char byteCopy = byte;
  for (int i = 0; i < 8; i++) {
    if (random(1000) < probability * 1000) {
      byteCopy ^= (1 << i);
    }
  }
  return byteCopy; 
}

String bitsToString(bool* bits, int length) {
  String result = "";
  for (int i = 0; i < length; i++) {
    result += bits[i] ? "1" : "0";
  }
  return result;
}

void charToBits(char chr, bool* bits) {
  for (int i = 0; i < 8; i++) {
    bits[i] = (chr >> (7 - i)) & 1;
  }
}

uint32_t calculateCRC32(String chars) {
  uint32_t crc32 = 0;
  
  for (int i = 0; i < chars.length(); i++) {
    char currentChar = chars.charAt(i);
    bool bits[8];
    charToBits(currentChar, bits);
    
    for (int j = 0; j < 8; j++) {
      bool bit = bits[j];
      bool crc32MSB = (crc32 >> 31) & 1;
      
      if (crc32MSB != bit) {
        crc32 = (crc32 << 1) ^ CRC32POLY;
      } else {
        crc32 = crc32 << 1;
      }
      crc32 &= 0xFFFFFFFF;
    }
  }
  
  return crc32;
}
