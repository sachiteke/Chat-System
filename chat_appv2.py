import threading
import socket
import pyttsx3
import speech_recognition as sr
import datetime
import pytz
import getpass


#Adjusts timezone to IST
timez = pytz.timezone("Asia/Kolkata")
curr = datetime.datetime.now(tz=timez)
curr = curr.strftime("%d/%m/%Y %H:%M:%S")
print(curr)

#lists for keywords
disconnect = ["exit", "quit", "disconnect"]
tts = ["text to speech", "tts"]

#file to store the chat history
f1 = open("history.txt", "a")
f1.write("\n["+curr+"]\n")


#make a http request to google to find out current IP
def getClientIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    print("connected")
    IP = s.getsockname()[0]
    s.close()
    return IP


#ask for the recipient's IP
def getReciever(ReceiverIP):
    inp = input("Enter reciever IP: ")
    recIP = ReceiverIP
    if len(inp) < 13:
        return
    recIP.append(inp)
    return recIP


#this function toggle the status of the text-to-speech flag
def tts_toggle():
    global tts_flag
    if tts_flag == 1:
        tts_flag = 0
    else:
        tts_flag = 1
    return tts_flag

#checking the value to text-to-speech flag
def ttscheck():
    global tts_flag
    return tts_flag


#this is where the actual text-to-speech happens
def textts(input):
    eng = pyttsx3.init()
    eng.say(input)
    eng.runAndWait()
    return


#this function uses Google's voice recognition api to detect voice
#and change it to a string
def speechToText():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Callibrating....")
        r.adjust_for_ambient_noise(source, duration=3)
        print("Speak now....")
        audio = r.listen(source)
        msg = r.recognize_google(audio)
        msg = msg.lower()
        return msg



#this function sends the message to all the IP addresses in RecieverIP
def send(ReceiverIP, flag):
    while 1:
        r = ReceiverIP
        global tts_flag
        if flag == 1:     #this flag is used to tell if the execution has to be stopped
            s.close()
            return
        msg = input()
        if msg in tts:
            tts_flag = tts_toggle()
            if tts_flag == 0:
                print("Text to speech off")
            else:
                print("Text to speech on")
            continue
        if msg == "speak":
            msg = speechToText()
        if "add address " in msg:  #adds another address in the RecieverIP list
            r.append(msg[12:])
            print(r)
            ReceiverIP = r
        print("You: "+msg)
        f1.write("You: "+msg+"\n")
        msgnew = HostIP+": "+msg
        for recIP in ReceiverIP:
            s.sendto(msgnew.encode(), (recIP, 9999))
        if msg.lower() in disconnect:
            flag = 1
            s.close()
            return


#revieves messages from various senders
def recieve(flag):
    while 1:
        t = ttscheck()
        rec = s.recvfrom(1024)
        print(rec[0].decode("utf-8"))
        f1.write(rec[0].decode("utf-8")+"\n")
        t = ttscheck()
        if t == 1:
            textts(rec[0][14:].decode("utf-8"))
            continue
        if rec[0].decode("utf-8").lower() in disconnect:
            break


counter = 0. #to count number of login attempts
try:
    while(counter < 3):
        file = open("psswrd.dat", "rb")
        inp = getpass.getpass()
        i = file.read(len(inp))
        if i.decode("utf-8") == inp:
            print("Logged in!\n")
            file.close()
            break
        else:
            print("Wrong password")
            counter += 1
            if counter >= 3:
                print("Too many attempts, exiting....")
                quit()
except FileNotFoundError:
    print("New user, please set a password")
    paswd = input("Enter the password: ")
    file = open("psswrd.dat", "wb")
    file.write(paswd.encode())
    file.close()

HostIP = getClientIP()
flag = 0
print("Your IP address is: "+HostIP)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((HostIP, 9999))
ReceiverIP = []
tts_flag = 0
ReceiverIP = getReciever(ReceiverIP)
t2 = threading.Thread(target=recieve, args=(flag,), daemon=True)
t2.start()
send(ReceiverIP, flag)
f1.close()
quit()
quit()
