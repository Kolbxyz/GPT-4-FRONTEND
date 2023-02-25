import openai
from gtts import gTTS
import os
import wikipedia
import pyaudio
import wave
import speech_recognition as sr
from translate import Translator
import datetime
import webbrowser

#language = input("Enter language: \n") or 'fr' 
print("-------- START --------")
### Settings (inputs)
TTS = input("Activate Text To Speech? y/n: ") == "y" and True or False
isFile = input("Convert prompt to a file path? y/n: ") == "y" and True or False
isVoice = input("Record your voice as prompt? y/n: ") == "y" and True or False
RPCharacter = input("What character do I like act like? [enter] for none: ")
languageInput = input("What language? (fr/en...): ") or "fr"
temperature = int(input("Temperature: (0 - 1): ") or 0.5)
contextMemory = input("keep context in memory? y/n: ") == "y" and True or False
isText = input("Text completion? text/image: ") == "text" and True or False

### Setup
wikipedia.set_lang(languageInput)
translator= Translator(to_lang="fr")
previousResult = ""
os.environ["api_key"] = "sk-YOURAPIKEYRIGHTTHERE"

### Functions
def log(content):
   with open("log.txt", "a") as f: f.write(str(datetime.datetime.now()) + " | " + content + "\n\n")

### Loop
chunk = 1024
sample_format = pyaudio.paInt16
channels = 2
fs = 44100
seconds = 5
filename = "voiceRecording.wav"
p = pyaudio.PyAudio()
os.system('clear')
while True:
 #   os.system('clear')
    Input = ""
    if isVoice != True: Input = input()
    if isFile: Input = "Explique moi ce que fait ce fichier: " + open(Input, "r").read()
#    print(Input)
#   print("Sending API request to wikipedia with query = " + Input)
#   query = wikipedia.summary(wikipedia.search(Input, results = 1)[0], auto_suggest=False)

    if isVoice:
        print('Recording...')
        stream = p.open(format=sample_format,
        channels=channels,
        rate=fs,
        frames_per_buffer=chunk,
        input=True)
        frames = []

        for i in range(0, int(fs / chunk * seconds)):
                data = stream.read(chunk)
                frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        print('Creating audio file...')

        wf = wave.open(filename, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(sample_format))
        wf.setframerate(fs)
        wf.writeframes(b''.join(frames))
        wf.close()

        print('Interpreting audio file...')
        r = sr.Recognizer()
        r.energy_threshold = 50
        r.dynamic_energy_threshold = False
        with sr.AudioFile(filename) as source:
            audio = r.record(source)
        try:
            print(languageInput.lower()+"-"+languageInput.upper())
            Input = r.recognize_google(audio, language=languageInput.lower()+"-"+languageInput.upper())
        except:
            print("Please try again")
  #  print(Input)
    if RPCharacter != "": RPCharacter = "Répond à cette question comme si tu étais {name}: {query}".format(name = RPCharacter, query = Input)
#    print("Translating text.")
    try:
        Input = translator.translate(Input)
    except:
        Input = Input
        
    log(Input)

#    print("...")

    openai.api_key = os.environ["api_key"]
    if isText:
    	completion = openai.Completion.create(
        	engine="text-davinci-003",
        	prompt=previousResult+RPCharacter+Input,
        	max_tokens=3000,
        	temperature=temperature,
        	top_p=1,
        	frequency_penalty=0,
        	presence_penalty=0
    	)
    	result = completion.choices[0].text
    else:
    	print("Generating image ({prompt})".format(prompt=Input))
    	completion = openai.Image.create(
    		prompt=Input,
    		n=1,
    		size="256x256",
	)
    	result = completion["data"][0]["url"]
    	webbrowser.open(result)
    
    print("----------------------------------"+"\n"+result+"\n"+"----------------------------------\n")
    log(result)
    if not isFile and contextMemory and isText: previousResult = "Afin que tu te rappelles de notre conversation précédente, j'ai demandé: {input} et tu as répondu {result}.\n".format(input=Input, result=result)
    
    if TTS:
    	print("Creating audio file...")
    	myobj = gTTS(text=result, lang=languageInput, slow=False)
    	myobj.save("file" + ".mp3")
    	os.system("mpg321 " + "file" + ".mp3")# + " tempo 1.9")'''

#    input("")#[Enter to continue]")
