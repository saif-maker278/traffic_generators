#!/bin/python
import requests
import re
import sys
import random
from threading import Thread
from time import sleep

# Les pages que le programme va surfer
pages_initiales = []

def usage():
	print("Usage: ./http_gen.sh <liste de sites web> <frequence moyenne en s> <profondeur max> <duree>")
if len(sys.argv) != 5:
	usage()
	exit(1)

pages_initiales = str(sys.argv[1]).split(',')
try:
	frequence = int(sys.argv[2])
	limit1 = int(frequence/2)
	limit2 = int(frequence/2 + frequence)
	PROFONDEUR_MAX = int(sys.argv[3])
	duree = int(sys.argv[4])
except:
	print("Arguments invalides")
	usage()
	exit(1)

# Tirer au sort une page
def page_aleatoire():
	nbr_pages = len(pages_initiales)
	return pages_initiales[random.randint(0, nbr_pages - 1)]

# Tirer au sort un lien parmi une liste de liens
def lien_aleatoire(liste):
	nbr_liens = len(liste)
	ale = liste[random.randint(0, nbr_liens - 1)]
	print("Lien choisi: " + ale)
	return ale

# Se diriger à un lien, et définir la profondeur de ce lien
def aller(lien, profondeur):
	print("Profondeur actuelle: " + str(profondeur))
	if profondeur == PROFONDEUR_MAX:
		print("PROFONDEUR_MAX atteinte!")
		sleep(random.randint(limit1, limit2))
		return
	else:
		print("[-->] Se diriger a " + lien)
		contenu = requests.get(lien,verify=False).text
		listeLiens = chercherLiens(contenu)
		if len(listeLiens) == 0:
			print("Pas de liens dans cette page, on va sur une autre ... ")
			return
		sleep(random.randint(limit1, limit2))
		aller(lien_aleatoire(listeLiens), profondeur + 1)

# Retourner une liste de liens dans une page
def chercherLiens(page):
	liens = []
	print("Les liens trouves sur cette page:")
	# On cherche tous les tags <a> dans le document HTML
	# Le flag re.DOTALL est mis pour que le . soit compatible a "a la ligne \n"
	for tag in re.findall("<a.*?>", page, re.DOTALL):
		# encode utf8 pour les lettres non ASCII
		if re.search('\"http', tag.encode('utf8'), re.DOTALL):
			lien = re.findall("http(?:.*?)[\"]", tag.encode('utf8'), re.DOTALL)[0]
			lien = lien.split("\"")[0]
			print("     - " + lien)
			liens.append(lien)
	return liens

def http_gen():
	while True:
		aller(page_aleatoire(), 0)

# Une horloge qui arrete le programme quand la durée est ecoulée
def horloge(duree):
	print("L'horloge commence!")
	sleep(duree)
	print("Temps ecoule, programme termine!")

th1 = Thread(target = horloge, args = [duree])
th2 = Thread(target = http_gen)
th2.daemon = True
th1.start()
th2.start()
