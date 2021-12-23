"""
Qui è contenuta la funzione load che permette di creare un grafo
da file presenti in una cartella
"""
from graphs import *

import os, shutil
from pickle import *
from scipy import *


def load_graph(percorso):
    """
    Questa funzione , ricevuto il percorso file di una cartella contenente dei file adjacency.npz, id list.pkl,
    attributes.pkl, edge labels.pkl, crea un grafo G come oggetto della classe
    DirectedGraph e caratterizzato dai file sopra indicati.

    :param percorso: percorso file della cartella contenente i file per costruire il grafo
    :return: grafo
    """
    cartella_programma=os.getcwd()
    os.chdir(percorso)
    file_attributi=open("attributes.pkl","rb")
    attributi=load(file_attributi,allow_pickle=True)
    file_attributi.close()
    os.chdir(cartella_programma)
    grafo=DirectedGraph(attributi["name"],attributi["default_weight"])
    grafo.add_from_files(percorso)
    return grafo
