#!/usr/bin/python
import ftplib
import random
import sys
import re
import os
import time
import threading

transaction = False
NBR_OPERATIONS = int(5)

def usage():
	print("Usage: ftp_gen.py <serveur FTP> <fichier de logins> <repertoire de travail en local> <duree> <frequence en moyenne>")
if len(sys.argv) != 6:
	usage()
	exit(1)

serveur = sys.argv[1]
creds = sys.argv[2]
repertoire = sys.argv[3]
try:
	duree = int(sys.argv[4])
	frequence = int(sys.argv[5])
	limite1 = int(frequence/2)
	limite2 = int(frequence*3/2)
except:
	print("La duree saisie est invalide.")
	exit(1)

if not os.path.isfile(creds):
	print("Le fichier des credentiels est invalide.")
	exit(1)
if not os.path.isdir(repertoire):
	print("Le repertoire des fichiers a up/downloader est invalide.")
	exit(1)

# Connexion au serveur
try:
	ftp = ftplib.FTP(serveur)
except:
	print("Erreur de connexion")
	exit(1)

# Fonction qui prend aléatoirement un jeu d'identifiant:mot de passe pour l'authentification
def creds_aleatoire():
	ident = "user"
	mdp = "mdp"
	idents = open(creds).read().split(';')
	cred = random.choice(idents)
	if re.search(':', cred):
		ident = cred.split(':')[0]
		mdp = cred.split(':')[1]
	return ident, mdp

# S'authentifier au serveur avec un identifiant et mot de passe
def authentification(ident, mdp):
	print("Authentification avec {}:{}".format(ident, mdp))
	ftp.login(ident,mdp)

# Téléchargement d'un fichier aléatoire sur le serveur
def telecharger():
	# ftplib.FTP.nlst() retourne les fichiers sur le serveur FTP
	liste_fichiers = ftp.nlst()
	if len(liste_fichiers) != 0:
		print("Liste des fichiers sur le serveur:")
		for fichier in liste_fichiers:
			print("   - {}".format(fichier))
		# On en choisit un, aléatoirement
		a_telecharger = random.choice(liste_fichiers)
		print("Telechargement de {}".format(a_telecharger))
		# La commande RETR pour télécharger le fichier
		# Il sera mis dans le meme répertoire des fichiers à uploader
		transaction = True
		try:
			with open(os.path.join(repertoire, a_telecharger), "wb") as file:
				ftp.retrbinary("RETR {}".format(a_telecharger), file.write)
		except:
			print("Telechargement de {} echoue".format(a_telecharger))
	else:
		print("Pas de fichiers sur le serveurs.")
	transaction = False
	time.sleep(random.randint(limite1, limite2))

# Upload d'un fichier aléatoire sur la machine locale au serveur
def uploader():
	# Ici on ne prend en compte que les fichiers. Les dossiers sont ignorés
	liste_fichiers = [fichier for fichier in os.listdir(repertoire) if os.path.isfile(os.path.join(repertoire, fichier))]
	if len(liste_fichiers) != 0:
		print("Liste des fichiers en local:")
		for fichier in liste_fichiers:
			print("   + {}".format(fichier))
		# On en choisit un, aléatoirement
		a_uploader = random.choice(liste_fichiers)
		print("Chargement de {}".format(a_uploader))
		# La commande STOR pour uploader le fichier
		# Il sera mis dans le répertoire / sur le serveur
		transaction = True
		try:
			with open(os.path.join(repertoire, a_uploader), "rb") as file:
				ftp.storbinary("STOR {}".format(a_uploader), file)
		except:
			print("Chargement de {} echoue".format(a_uploader))
	else:
		print("Pas de fichiers en local.")
	transaction = False
	time.sleep(random.randint(limite1, limite2))

def ftp_gen():
	while True:
		cred = creds_aleatoire()
		ftp = ftplib.FTP(serveur)
		try:
			authentification(cred[0], cred[1])
			print("Authentification reussie")
			for i in range(NBR_OPERATIONS):
				j = random.randint(0,1)
				if j == 0:
					telecharger()
				else:
					uploader()
		except EOFError:
			print("EOFError")
			ftp.quit()
		except ftplib.error_perm:
			# Si l'authentification est echouee
			# Attendre quelques secondes et reessayer
			print("Authentification echouee")
			time.sleep(random.randint(limite1, limite2))
		except Exception:
			print("Autre exception")
		ftp.quit()

# Une horloge qui arrete le programme une fois la durée est écoulée
def horloge(duree):
	print("L'horloge commence!!!")
	time.sleep(duree)
	print("Temps ecoule")
	while transaction:
		print("Une transaction encore en cours")
	ftp.quit()
	print("Programme termine")

th1 = threading.Thread(target = ftp_gen)
th2 = threading.Thread(target = horloge, args = [duree])
th1.daemon = True
th1.start()
th2.start()
