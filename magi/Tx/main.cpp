#include <Arduino.h>
#include <XBee.h>

XBee xbee = XBee();

uint8_t payload[] = {0, 0};

//SH and SL Address of receiving Zigbee (Find using XCTU)
XBeeAddress64 addr64 = XBeeAddress64(0x0013a200, 0x403e0f30);
ZBTxRequest zbTx = ZBTxRequest(addr64, payload, sizeof(payload));
ZBTxStatusResponse txStatus = ZBTxStatusResponse();

int pinLED = 51;
int pinComms = 0;


void setup(){
    pinMode(pinLED, OUTPUT);

    Serial.begin(9600);
    xbee.setSerial(Serial);

}

void loop(){
    pinComms = analogRead(5);
    payload[0] = pinComms >> 8 & 0xff;
    payload[1] = pinComms & 0xff;

    xbee.send(zbTx);

    digitalWrite(pinLED, HIGH);
    
    //Should get a status response after a TX request
    //wait up to half a second for response
    if (xbee.readPacket(500)){
    
    }
    else if(xbee.getResponse().isError()){
    
    }
    else{
        //XBee did not provide a timely TX status response
        //This is rare and shouldn't really happen

    }

    delay(1000);
    digitalWrite(pinLED, LOW);
    delay(1000);

}
