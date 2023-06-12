import socketio
import requests
import os
from colored import fg, attr
import json
import time
from bs4 import BeautifulSoup

# Créez une instance du client socket.io
sio = socketio.Client()

# Définissez la fonction de connexion
@sio.event
def connect():
    print('Connecté au serveur')

# Définissez la fonction de déconnexion
@sio.event
def disconnect():
    print('Déconnecté du serveur')

# Connectez-vous au serveur socket.io
sio.connect('https://room.vpla.net')

# Fonction pour envoyer les données au serveur
def envoyer_message(donnees):
    sio.emit('chat.message', donnees)

def envoyer_music(donnees):
    sio.emit('sound.play', donnees)

def envoyer_stop():
    sio.emit('sound.stop')

def getLocalSounds():
    with open('localSounds.json', "r") as json_file:
        return json.load(json_file)

def getOnlineSounds():
    soundsOnline = requests.get('https://room.vpla.net/sounds.json')
    return soundsOnline.json()

def ajouter_son(id_, url):
    nouveau_son = {
        "id": id_,
        "url": url
    }
    soundsLocal.append(nouveau_son)
    with open('localSounds.json', 'w') as fichier:
        json.dump(soundsLocal, fichier)
    
def soundAlreadyExists(id_, url):
    for sound in soundsLocal:
        if id_ == sound['id'] or url == sound['url']:
            return True
    return False

def getMP3WithLink(link):
    try:
        page = requests.get(link)
        page = page.text
        soup = BeautifulSoup(page, 'html.parser')
        element_a = soup.find('a', href=lambda href: href and href.startswith('/media/sounds'))
        href_value = element_a['href']
        url = 'https://www.myinstants.com' + href_value
        return url
    except:
        return False

def showIds(data):
    colors = [fg(1), fg(2), fg(3), fg(4), fg(5), fg(6), fg(7)]  # Liste de codes de couleurs
    reset_color = attr('reset')  # Code de réinitialisation de la couleur
    
    for index, sound in enumerate(data):
        title = sound['id']
        color = colors[index % len(colors)]  # Sélectionne une couleur à partir de la liste en boucle
        colored_title = color + title + reset_color  # Applique la couleur au titre
        print(colored_title, end=', ' if index < len(data) - 1 else '.\n')

def start():
    os.system('clear')
    print('Disponible sur room.vpla.net :')
    showIds(soundsOnline)
    print('Disponible en local :')
    showIds(soundsLocal)

def prompt_user():
    start()
    print()
    prompt = input('Texte : ')
    if prompt.startswith("mp3 "):
        name = prompt[4:]
        url = input('URL : ')
        ajouter_son(name, url)
        print(f'Votre son {name} a été ajouté avec succès.')

    elif prompt.startswith("add "):
        name = prompt[4:]
        url = input('URL : ')
        alreadyExists = soundAlreadyExists(name, url)
        if alreadyExists:
            print(f'Votre son {name} n\'a pas été ajouté car il existe déjà.')
        else:
            mp3 = getMP3WithLink(url)
            if mp3:
                ajouter_son(name, mp3)
            else:
                print(f'Votre son {name} n\'a pas été ajouté.')
        time.sleep(2)

    elif prompt[-4:] == ".mp3":
        envoyer_music(prompt)
    elif prompt == 'stop':
        envoyer_stop()
    else:
        for sound in soundsOnline + soundsLocal:
            if sound['id'] == prompt:
                return envoyer_music(sound['url'])
        data = {"message":prompt, "lang":"it"}
        envoyer_message(data)

soundsOnline = getOnlineSounds()
soundsLocal = getLocalSounds()

while True:
    prompt_user()            
