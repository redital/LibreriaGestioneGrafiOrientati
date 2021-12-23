"""
abbiamo scritto questo file per mostrare il corretto funzionamento del modulo e della funzione implementati
"""

from graphs import *
from functions import *
import os, shutil

g=DirectedGraph("Grafo_1")#creazione di un grafo vuoto di nome "Grafo_1" 
g.auto_add_nodes(12) #aggiunta di 12 nodi
g.add_edges([(2,4),(7,4),(11,4),(4,8),(8,9),(9,11)])#creazione di archi con peso predefinito 
g.add_edges([(1,5),(7,8),(8,9)],weight=4.0)#creazione di archi con peso dato
g.add_edges([(1,11),(8,1)],weight=0.5)#creazione di archi con peso dato
g.nodes[0].labels={"nome":"Giovanni","altezza":182} #assegnazione etichette ad un nodo del grafo
g.add_edges([(11,1)],lunghezza="20",colore="arancione") #assegnazione etichette ad un arco del grafo
print("\n\nStampa degli id dei nodi")
print(list(g.nodes.keys()))#stampa degli id
print("\n\nStampa degli archi e relative etichette")
for i in range (len(g.get_edges())):
    print(g.get_edges_labels([g.get_edges()[i]]))#stampa archi e relative etichette


gigi=g.copy()#creazione di un grafo come copia del grafo già presente
gigi.name="Grafo_copia"#assegnazione del nome al nuovo grafo


grafo=DirectedGraph("Grafo_2")#creazione di un nuovo grafo vuoto di nome "Grafo_2" 
grafo.auto_add_nodes(4)#aggiunta di 4 nodi
grafo.add_edges([(2,1),(1,3)],weight=2.0) #creazione archi
grafo.nodes[0].labels={"nome":"Alessia","altezza":164} #assegnazione etichette ad un nodo del grafo
grafo.add_edges([(0,1)],lunghezza="10",colore="blu") #assegnazione etichette ad un arco del grafo


grafo.save() #salvataggio del grafo "Grafo_2" su file
percorso=os.getcwd()+"\\"+grafo.name #creazione stringa percorso per la funzione load e per il metodo add_from_files. N.B. facendo partire più volte il programma la
                                     #funzione save creerà più occorrenze della cartella in questione differenziandole con un numero.
                                     #Il programma prenderà quindi sempre quello relativo alla oprima esecuzione.
                                     #Trattandosi solo di un test non ci siamo preoccupati molto di ciò. eventualmente basta eliminare
                                     #le cartella dalla cartella del programma 
g.add_from_files(percorso) #aggiunta al grafo "Grafo_1" di tutti gli elementi di "Grafo_2" tramite file
g.add_edges([(15,7),(12,1)],weight=1.5) #creazione di archi che collegano i nuovi nodi aggiunti con quelli già presenti in precedenza 
grafone=load_graph(percorso) #creazione di un grafo come copia del grafo già presente tramite file


print("\n\nStampa del cammino minimo e del costo di ogni passo")
print(g.minpath_dijkstra(14,5)) #stampa del cammino minimo secondo dijkstra
g.plot(False,True)#plot del grafo "Grafo_1"
