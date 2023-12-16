import requests
import sys
import os
import time
import argparse
import threading
from queue import Queue

# Définition des arguments
parser = argparse.ArgumentParser(description='Dirbuster')
parser.add_argument('-u', '--url', type=str, help='URL à scanner', required=True)
parser.add_argument('-w', '--wordlist', type=str, help='Wordlist à utiliser', required=True)
parser.add_argument('-t', '--threads', type=int, help='Nombre de threads', required=True)
parser.add_argument('-o', '--output', type=str, help='Fichier de sortie', required=True)
args = parser.parse_args()

# Définition des variables
url = args.url
wordlist = args.wordlist
threads = args.threads
output = args.output
q = Queue()

# Fonction pour écrire dans le fichier de sortie
def write_file(result):
    with open(output, 'a') as f:
        f.write(result + '\n')

# Fonction pour scanner les répertoires
def scan_dir(url, wordlist):
    while not q.empty():
        try:
            path = q.get()
            r = requests.get(url + path, timeout=10)
            if r.status_code == 200:
                print('[+] ' + url + path)
                write_file(url + path)
            elif r.status_code == 403:
                print('[!] ' + url + path + ' (403 - Forbidden)')
            elif r.status_code == 404:
                print('[-] ' + url + path)
            else:
                print('[?] ' + url + path + ' (' + str(r.status_code) + ')')
        except Exception as e:
            print('[-] Erreur lors du scan de ' + url + path + ': ' + str(e))
        finally:
            q.task_done()

# Fonction pour créer les threads
def create_threads():
    for _ in range(threads):
        t = threading.Thread(target=scan_dir, args=(url, wordlist))
        t.daemon = True
        t.start()

# Fonction pour créer la file d'attente
def create_queue():
    with open(wordlist, 'r') as f:
        for line in f:
            q.put(line.strip())

# Fonction pour lancer le scan
def start_scan():
    create_queue()
    create_threads()

# Fonction pour afficher les informations
def print_info():
    print('URL: ' + url)
    print('Wordlist: ' + wordlist)
    print('Threads: ' + str(threads))
    print('Output: ' + output)
    print('')

# Fonction pour vérifier les arguments
def check_args():
    if not os.path.isfile(wordlist):
        print('[-] Le fichier ' + wordlist + ' n\'existe pas')
        sys.exit(1)
    if not os.path.exists(output):
        open(output, 'w').close()

# Fonction principale
def main():
    check_args()
    print_info()
    start_scan()
    q.join()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('[-] Interruption du scan')
        sys.exit(1)
