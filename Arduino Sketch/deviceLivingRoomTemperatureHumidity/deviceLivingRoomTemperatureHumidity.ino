#include "DHT.h"

#include <SPI.h>
#include "nRF24L01.h"
#include "RF24.h"
#include <printf.h>  // Printf is used for debug 

#define BAUDRATE 9600

#define MASTERID 1  // number of the master device
#define MYID 2  // number of the device
#define MASTERPIPE 0
#define MYPIPE 1

// Uncomment whatever type you're using!
//#define DHTTYPE DHT11   // DHT 11 
#define DHTTYPE DHT22   // DHT 22  (AM2302)
//#define DHTTYPE DHT21   // DHT 21 (AM2301)
#define DHTPIN 6     // what pin the DHT is connected to
#define UNIT 1      // 0 for Fahrenheit and 1 for Celsius

DHT dht(DHTPIN, DHTTYPE); // set dht

RF24 radio(9,10);

// Radio pipe addresses for the 2 nodes to communicate.
const uint64_t pipes[6] = { 0xE1F0F0F0E1LL, 0xD2F0F0F0D2LL, 0xF0B2F0F0B2LL, 0xF0C3F0F0C3LL, 0xF0F0E4F0E4LL, 0xF0F0D5F0D5LL };

// declare actions
#define ACTIONTEMP 1 // send temperature
#define ACTIONHUM 2 // send humidity
#define ACTIONTEMPHUM 3 // send temperature and humidity

// declare variables
char receive_payload[32]; // max is 32 bytes even with enableDynamicPayloads

//int task; // can not send task it gets to big
int from;
int to;
int action;

char message[24]; // hold return ms

char payload[26]; // max is 32 bytes even with enableDynamicPayloads

void setup(void)
{
  Serial.begin(BAUDRATE);
  Serial.println("Serial begin.");
  
  Serial.println("Printf begin.");
  printf_begin(); //Printf is used for debug
    
  Serial.println("Radio begin.");
  radio.begin();
  
  // enable dynamic payloads
  radio.enableDynamicPayloads();

  // optionally, increase the delay between retries & # of retries
  radio.setRetries(5,15);
  
  radio.setPALevel(RF24_PA_MAX);
  radio.setDataRate(RF24_250KBPS);
  radio.setChannel(114);

  radio.openWritingPipe(pipes[MYPIPE]);
  radio.openReadingPipe(1,pipes[MASTERPIPE]);

  radio.startListening();
  
  radio.printDetails();
}

int ftoa(char *a, float f){  //translates floating point readings into strings to send over the air
  int left=int(f);
  float decimal = f-left;
  int right = decimal *100; //2 decimal points
  if (right > 10) {  //if the decimal has two places already. Otherwise
    sprintf(a, "%d.%d",left,right);
  } else { 
    sprintf(a, "%d.0%d",left,right); //pad with a leading 0
  }
}

char *getTempHum(int action, char* message){
  char temp[6]; //2 int, 2 dec, 1 point, and \0
  char hum[6];
  
  // Reading temperature or humidity takes about 250 milliseconds!
  // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  float tf = t * 1.8 +32;  //Convert from C to F 
  
  Serial.println("");
  
  // check if returns are valid, if they are NaN (not a number) then something went wrong!
  if (isnan(t) || isnan(h)) {
    Serial.println("Failed read DHT");
    // if its failt to read set everything to zero so it returns something back and the program can 
    // see at the 0.00 that it has failt
    h = 0.00;
    t = 0.00;
    tf = 0.00;
    
    sprintf(message, "error:%s", "failed read dht");
    
  }else {
    Serial.print("Humidity: "); 
    Serial.print(h);
    Serial.print(" %\t");
    ftoa(hum,h);
    
    Serial.print("Temperature: "); 
    if (UNIT == 0 ){  //choose the right unit F or C
      Serial.print(tf);
      Serial.println(" *F");
      ftoa(temp,tf);
    }
    else {
      Serial.print(t);
      Serial.println(" *C");
      ftoa(temp,t);
    }
    
    // build message
    if(ACTIONTEMP == action){ // temperature
      sprintf(message, "temp:%s", temp);
    }
    if(ACTIONHUM == action){ // humidity
      sprintf(message, "hum:%s", hum);
    } 
    if(ACTIONTEMPHUM == action){ // temperature and humidity
      sprintf(message, "temp:%s,hum:%s", temp, hum);
    }  
    
    Serial.println("");
    Serial.print("Return: ");
    Serial.println(message);
  }
}

void loop(void)
{
  // if there is data ready
  while ( radio.available() )
  {
    // Fetch the payload, and see if this was the last one.
    uint8_t len = radio.getDynamicPayloadSize();
    
    // If a corrupt dynamic payload is received, it will be flushed
    if(!len){
      continue; 
    }
    
    memset(receive_payload, 0, len); // clear it    
    radio.read( receive_payload, len );
    
    Serial.println("");
    Serial.print("Received: ");
    Serial.println(receive_payload);
    
    from = 0;
    to = 0;
    action = 0;
    sscanf((char *)receive_payload, "fr:%d,to:%d,ac:%d", &from, &to, &action);
    
    Serial.print("From: ");
    Serial.print(from);
    Serial.print("To: ");
    Serial.print(to);
    Serial.print("Action: ");
    Serial.print(action);
    
    if(from == MASTERID && to == MYID){
      
      if(ACTIONTEMP == action || ACTIONHUM == action || ACTIONTEMPHUM == action){ // temperature humidity
        Serial.println("");
        Serial.print("Action #: ");
        Serial.println(action);
        getTempHum(action, message);
        
      }else {
        sprintf(message, "error:action not exists");
      }
      
      Serial.println("");
      Serial.print("Message: ");
      Serial.println(message);
      
      memset(payload, 0, sizeof(payload)); // clear it
      sprintf(payload, "%s\0", message);
      
      // First, stop listening so we can talk
      radio.stopListening();
      
      Serial.println("");
      Serial.print("Send: ");
      Serial.println(payload);
      
      Serial.print("Send size: ");
      Serial.println(sizeof(payload));
      
      // Send the final one back.
      radio.write( payload, sizeof(payload) );
      
      // Now, resume listening so we catch the next packets.
      radio.startListening();
    }
  }
}
