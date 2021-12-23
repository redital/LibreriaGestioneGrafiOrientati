"""
Modulo per la gestione di grafi orientati.
Contiene due classi, DirGraphNode per gestire i nodi e
DirectedGraph per il grafo nel suo insieme.
Contiene tutte le principali operazioni, come lettura, aggiunta, rimozione, modifica
di nodi e archi, consente di salvare e/o caricare i dati del grafo su file .pkl
e contiene un metodo basato sull'algoritmo di Dijikstra per il
calcolo del cammino minimo tra due nodi. E' inoltre implementato
un metodo che consente la visualizzazione grafica dell'oggetto costruito.
"""


from pickle import *
import os, shutil
from scipy.sparse import *
from scipy import *
import numpy as np
from copy import deepcopy
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook


class DirGraphNode:
    """
    La classe DirGraphNode serve a caratterizzare un generico nodo v di un generico grafo orientato G.

    Al suo interno sono presenti i seguenti attributi:
    - id -> int: contiene l'ID del nodo
    - labels -> dizionario: contiene tutte le etichette del nodo
    - neighbours_out -> lista di tuple: Ogni tupla contiene l'i-esimo vicino ui del nodo v e il dizionario
      contenente le etichette dell'arco (v,ui)
    - neighbours_in -> lista: contiene oggetti DirGraphNode wi tali che wi sia l'i-esimo vicino di v
      considerando i lati (wi,v), ovvero entranti in v

    I metodi contenuti sono utili per la gestione dei nodi.
    """
    def __init__(self, id=None, **labels):
        """
        Questo metodo serve per l'inizializzazione di un elemento di tipo DirGraphNode.
        
        :param id: ID del nodo. DEFAULT = None
        :param labels: (facoltativo) un dizionario contenente le etichette del nodo

        :return:
        """
        self.id = id
        self.labels = labels
        self.neighbours_out = []
        self.neighbours_in = []

    def get_neighbours(self):
        """
        Il metodo restituisce due liste contenenti i vicini del nodo

        :return: neighbours_out, self.neighbours_in
        """
        neighbours_out = []
        for pair in self.neighbours_out:
            neighbours_out.append(pair[0])

        return neighbours_out, self.neighbours_in


    def degrees(self):
        """
        Il metodo restituisce il numero di lati in entrata (degout) e di quelli in uscita (degin) rispetto ad un nodo

        :return: degout, degin
        """
        degout=len(self.neighbours_out)
        degin=len(self.neighbours_in)
        return degout, degin


    def get_edge_labels(self, elenco):
        """
        Dato un elenco di nodi (u0,...,un), il metodo restituisce una lista contenente le etichette dei lati (v,ui)

        :param elenco: lista contenente un elenco di nodi (u0,...,un)
        :return: lista
        """
        lista=[]
        for nodo in elenco:
            if nodo in self.get_neighbours()[0]:
                for pair in self.neighbours_out:
                    if pair[0]==nodo:
                        lista.append(pair[1])
        return lista

    

    def add_neighbours_out(self, *new_neighbours_out, **edge_labels):
        """
        Il metodo aggiunge nuove tuple (nodo, labels) all'attributo neghbours_out.

        :param *new_neighbours_out: elenco di nuovi neighbours_out da aggiungere al nodo
        :param **edge_labels: etichette comuni da applicare ai nuovi lati (nodo, new_neighbours_out)

        :return:
        """
        neighbours_out, _ = self.get_neighbours()
        for u in new_neighbours_out:
            if u not in neighbours_out:
                edge_labels_copy = edge_labels.copy()
                self.neighbours_out.append((u, edge_labels_copy))
            else:
                ind_u = neighbours_out.index(u)
                self.neighbours_out[ind_u][1].update(edge_labels)


    def add_neighbours_in(self, *new_neighbours_in):
        """
        Il metodo aggiunge un elenco di nuovi nodi all'attributo neiughbours_in

        :param new_neighbours_in: elenco di neighbours_in da aggiungere

        :return:
        """
        for w in new_neighbours_in:
            if w not in self.neighbours_in:
                self.neighbours_in.append(w)


    def rmv_neighbours_out (self, elenco):
        """
        Questo metodo rimuove dall'attributo neighbours_out tutte le tuple che contengono i nodi ui dati in elenco

        :param elenco: elenco dei nodi da rimuovere

        :return:
        """
        for nodo in elenco:
            for vicino in self.neighbours_out:
                if nodo.labels in vicino:
                    self.neighbours_out.remove(vicino)

                    
    def rmv_neighbours_in (self, elenco):
        """
        Questo metodo rimuove dall'attributo neighbours_in tutti i nodi wi dati in elenco

        :param elenco: elenco dei nodi da rimuovere

        :return:
        """
        for nodo in elenco:
            for vicino in self.neighbours_in:
                if nodo.labels in vicino:
                    self.neighbours_in.remove(vicino)    


class DirectedGraph:
    """
    La classe DirectedGraph serve a caratterizzare un generico grafo orientato G.

    Al suo interno sono presenti i seguenti attributi:
    - name -> stringa: contiene il nome del grafo.
    - default_weight -> double: contiene il peso di default di tutti gli archi non inizializzati
    - nodes ->  dizionario: contiene la corrispondenza id:nodo per ogni nodo del grafo
    
    """
    def __init__(self, name='noname_graph',
                 default_weight=1.0,
                 nodes=(),
                 edges=(),
                 node_labels={},
                 edge_labels={}):
        """
        Questo metodo serve per l'inizializzazione di un elemento di tipo DirectedGraph.
        
        :param name: nome del grafo. DEFAULT: 'noname_graph'
        :param default_weight: peso assegnato all'attributo default_weight. DEFAULT 1.0
        :param nodes: tupla dei nodi del grafo. DEFAULT: ()
        :param edges: tupla di tuple (ik, il) rappresentanti gli edges del grafo. DEFAULT: ()
        :param node_labels: dizionario contenente le etichette dei nodi. DEFAULT: {}
        :param edge_labels: dizionario contenente le etichette deilati. DEFAULT: {}

        :return:
        """
        self.name = name
        self.default_weight = default_weight
        self.nodes = {}
        self.add_nodes(nodes, **node_labels)
        self.add_edges(edges, **edge_labels)

    def add_nodes(self, id_list, **node_labels):
        """
        Questo metodo aggiunge al grafo una lista di nodi con le stesse etichette assegnando ad ogni nodo uno degli ID specificati in lista.

        :param id_list: lista di nodi da aggiungere
        :param **node_labels: (facoltativo) dizionario contenente le etichette comuni ai nodi da aggiungere

        :return:
        """
        for i in id_list:
            if i not in self.nodes.keys():
                v = DirGraphNode(i, **node_labels)
                self.nodes[i] = v
            else:
                self.nodes[i].labels.update(node_labels)

    def auto_add_nodes(self, num, **node_labels):
        """
        Questo metodo aggiunge al grafo un numero dato di nodi tutti con le stesse etichette.
        
        :param num: int che indica il numero di nodi da aggiungere
        :param **node_labels: (facoltativo) dizionario contenente le etichette comuni ai nodi da aggiungere

        :return:
        """
        idn=0
        lista_id = []
        for i in range(num):
            trovato=False
            while trovato==False:
                if idn in self.nodes.keys():
                    idn = idn +1
                else:
                    trovato=True
                    n=idn
                    idn = idn +1
                    lista_id.append(n)
        self.add_nodes(lista_id, **node_labels)
            

    def add_edges(self, edge_list, **edge_labels):
        """
        Questo metodo aggiunge una lista di archi e assegna a tutti le stesse etichette.
        
        :param edge_list: lista di tuple contenenti gli ID degli archi da aggiungere
        :param **edge_labels: (facoltativo) dizionario contenente le etichette da assegnare agli archi da aggiungere
                            'weight': chiave da utilizzare per specificare il peso

        :return:
        """
        if "weight" not in edge_labels.keys():
            edge_labels["weight"] = self.default_weight
    
        for edge in edge_list:
            i_out = edge[0]
            if i_out not in self.nodes.keys():
                self.add_nodes([i_out])
            i_in = edge[1]
            if i_in not in self.nodes.keys():
                add_nodes([i_in])
            w = self.nodes[i_out]
            u = self.nodes[i_in]
            
            w.add_neighbours_out(u, **edge_labels.copy())
            u.add_neighbours_in(w)

    

    def rmv_edges(self, edge_list):
        """
        Questo metodo rimuove gli archi dati in input dagli archi del grafo.
        
        :param edge_list: lista di tuple contenenti gli ID che identificano gli archi da rimuovere

        :return:
        """
        for edge in edge_list:
            i_out = edge[0]
            i_in = edge[1]
            w = self.nodes[i_out]
            u = self.nodes[i_in]
            if u in w.get_neighbours()[0]:
                w.neighbours_out.pop(w.get_neighbours()[0].index(u))
            if w in u.neighbours_in:
                u.neighbours_in.remove(w)



    def rmv_nodes (self, lista_id):
        """
        Questo metodo rimuove i nodi dati in input dai nodi del grafo.
        
        :param lista_id: lista di ID che identificano i nodi da rimuovere

        :return:
        """
        for idn in lista_id:
            edge_list=[]
            for nodo in self.nodes[idn].get_neighbours()[0]:
                edge_list.append((self.nodes[idn].id,nodo.id))
            for nodo in self.nodes[idn].get_neighbours()[1]:
                edge_list.append((nodo.id,self.nodes[idn].id))
            print (edge_list)
            self.rmv_edges(edge_list)
            del self.nodes[idn]


    def get_edges (self):
        """
        Questo metodo restiruisce una lista contenente tutte le tuple di ID indicanti gli archi del grafo.

        :return: edge_list
        """
        edge_list=[]
        for nodo in self.nodes.values():
            for out in nodo.get_neighbours()[0]:
                edge_list.append((nodo.id,out.id))
        return edge_list


    def get_edges_labels(self,edge_list):
        """
        Questo metodo, data una lista contenente le tuple di ID indicanti degli archi,
        restiruisce una lista contenente tutte le etichette degli archi presenti nella lista.

        :return: lista
        """
        lista=[]
        dizionario={}
        for edge in edge_list:
            if edge not in self.get_edges():
                dizionario[edge]=None
                lista.append(dizionario.copy())
            else :
                for n in self.nodes[edge[0]].neighbours_out:
                    if n[0].id==edge[1]:
                        dizionario[edge]=n[1]
                        if dizionario[edge] not in lista:
                            lista.append(dizionario.copy())
                        dizionario.clear()
        return lista


    def size(self):
        """
        Questo metdo restituisce il numero di nodi e il numero di archi che compongono il grafo.
        
        :return: len(self.nodes), len(self.get_edges())
        """
        return len(self.nodes), len(self.get_edges())


    def copy(self):
        """
        Questo metodo crea un nuovo grafo che è una esatta copia del grafo al quale viene applicato il metodo
        
        :return: deepcopy(self)
        """
        return deepcopy(self)


    def compute_adjacency(self,tipo="D"):
        """
        Questo metodo computa la matrice di adiacenza del grafo e l'utente ha a possibilità
        di specificare se essa deve essere restituita in forma densa o sparsa specificando nel parametro di input
        una D o una S, rispettivamente.

        :param tipo:
                    D: matrice viene computata in forma densa
                    S: matrice viene computata in forma sparsa
        :return: m
        """
        
        id_list=self.nodes.keys()
        massimo=max(id_list) + 1
        
        matrice=[]
        for i in range(massimo):
            riga=[]
            if i not in id_list:
                for j in range (massimo):
                    riga.append(0)
                    print("aggiungo uno 0 alla riga " + str(i) + " in posizione " + str(j))
            else:
                for j in range (massimo):
                    if j in id_list:
                        if (i,j) in self.get_edges():
                            riga.append(self.get_edges_labels([(i,j)])[0][(i,j)]["weight"])
                        else:
                            riga.append(0)
                    else:
                        riga.append(0)
            matrice.append(riga.copy())
            riga.clear()
             
        m=np.asmatrix(np.array(matrice))
        
        if tipo=="S":
            m=dok_matrix(m)
        return m        

    def add_from_adjacency(self, matrice):
        """
        aggiunge al grafo dei nodi e gli archi che li collegano partendo da una matrice di adiacenza

        :param matrice: matrice: la matrice di adiacenza dalla quale copiare i dati
        :return:

        """
        id_list=[]
        for i in range(matrice.shape[0]):
            self.auto_add_nodes(1)
            id_list.append(list(self.nodes.keys())[len(self.nodes.keys())-1])
        
        for i in range(matrice.shape[0]):
            for j in range( matrice.shape[1]):
                if matrice[i,j]!=0:
                    self.add_edges([(id_list[i],id_list[j])],weight=matrice[i,j])

    def add_graph(self, grafo):
        """
        aggiunge al grafo tutti gli elementi di un altro grafo dato in input

        :param grafo:grafo dal quale copiare i dati
        :return:
        """
        #self.add_from_adjacency(grafo.compute_adjacency("S"))
        grafo_tmp=grafo.nodes.copy()
        lista_nuovi_id=[]
        for idn, value in grafo.nodes.items():
            if idn in self.nodes.keys():
                trovato=False
                nuovo_id=0
                while trovato==False:
                    if (nuovo_id in self.nodes.keys()) or (nuovo_id in lista_nuovi_id):
                        nuovo_id = nuovo_id +1
                    else:
                        trovato=True
                        lista_nuovi_id.append(nuovo_id)
                        value.id=nuovo_id
                        grafo_tmp[nuovo_id]=value
                        del grafo_tmp[idn]
        self.nodes.update(grafo_tmp)


    def save(self,**inputo):
        """
        genera una cartella in cui salvare alcuni file contenenti
        i dati relativi al grafo. A discrezione dell’utente si può
        scegliere il nome della cartella e il path in cui crearla.
        se questi dati non vengono forniti, di default la cartella
        verrà creata all'interno della cartella del programma e si
        chiamerà come il grafo. Se dovesse già esistere una o più
        cartelle con quel nome sarà chiamata Nome_grafo(1),Nome_grafo(2)...
        i file saranno salvati con i nomi "adjacency.pkl", "id list.pkl",
        "attributes.pkl", "edge labels.pkl"

        :param: **inputo:
                        percorso: il percorso in cui creare la cartella
                        nome: il nome della cartella
        :return:
        """
        if "nome" not in list(inputo.keys()):
            nome=self.name
        else:
            nome = inputo["nome"]
        if "percorso" not in list(inputo.keys()):
            percorso=os.getcwd()
        else:
            percorso = inputo["percorso"]
        cartella_programma=os.getcwd()
        i=0
        while os.path.exists(percorso+"\\"+nome):
            i = i + 1
            nome = self.name + "(" + str(i) + ")"
        percorso = percorso + "\\" + nome
        os.makedirs(percorso)

        os.chdir(percorso)
        file_id=open("id_list.pkl","wb")
        dump(list(self.nodes.keys()),file_id)
        #file_id.write(str(list(self.nodes.keys())))
        file_id.close()
        file_matrice=open("adjacency.pkl","wb")
        dump(dict(self.compute_adjacency("S")),file_matrice)
        #file_matrice.write(str(dict(self.compute_adjacency("S"))))
        file_matrice.close()
        labels={}
        for idn in self.nodes.keys():
            labels[idn]=self.nodes[idn].labels
        attributi={"name":self.name,"default_weight":self.default_weight,"node_labels":labels}
        file_attributi=open("attributes.pkl","wb")
        dump(attributi,file_attributi)
        #file_attributi.write(str(attributi))
        file_attributi.close()
        archi={}
        for arco in self.get_edges():
            lista=[arco]
            a=list(self.get_edges_labels(lista)[0].values())[0].copy()
            del a["weight"]
            archi[arco]=a.copy()
        file_archi=open("edge_labels.pkl","wb")
        dump(archi,file_archi)
        #file_archi.write(str(archi))
        file_archi.close()
        
        os.chdir(cartella_programma)


    def add_from_files(self,percorso):
        """
        dato il percorso di una cartella, cerca al suo interno dei file
        "adjacency.pkl", "id list.pkl", "attributes.pkl", "edge labels.pkl",
        aggiunge tutti gli elementi di un altro grafo salvato su tali file

        :param: percorso: il percorso della cartella nella quale sono salvati i file
        :return:
        """
        cartella_programma=os.getcwd()
        os.chdir(percorso)
        file_id=open("id_list.pkl","rb")
        lista_id=load(file_id,allow_pickle=True)
        file_id.close()
        file_attributi=open("attributes.pkl","rb")
        attributi=load(file_attributi,allow_pickle=True)
        file_attributi.close()
        file_matrice=open("adjacency.pkl","rb")
        matrice=load(file_matrice,allow_pickle=True)
        file_matrice.close()
        file_archi=open("edge_labels.pkl","rb")
        archi=load(file_archi,allow_pickle=True)
        file_archi.close()
        
        
            
        self.auto_add_nodes(len(list(lista_id)))
        
        #lista=[]
        #for i in list(lettura):
        #    if i not in self.nodes.keys():
        #        lista.append(i)
        #self.add_nodes(lista)
        #self.auto_add_nodes(len(list(lettura))-len(lista))

        #add_nodes([idn],attributi[node_labels][idn])
        i=0
        for idn in lista_id:
            i=i+1
            self.nodes[list(self.nodes.keys())[-len(lista_id)+i-1]].labels.update(attributi["node_labels"][idn])
        for arco in matrice.keys():
            i=0
            trovato=0
            id_out=0
            id_in=0
            while trovato<2:
                for i in range(len(lista_id)):
                    idn=lista_id[i]
                    if idn==arco[0]:
                        id_out=i
                        trovato=trovato+1
                    if idn==arco[1]:
                        id_in=i
                        trovato=trovato+1
                    
            id_out=list(self.nodes.keys())[-len(lista_id)+id_out]
            id_in=list(self.nodes.keys())[-len(lista_id)+id_in]
            
            nuovo_arco=(id_out,id_in)
            self.add_edges([nuovo_arco],**archi[arco])
            self.add_edges([nuovo_arco],weight=matrice[arco])

        os.chdir(cartella_programma)

    def plot(self,etichette_nodi=False,etichette_archi=False):
        """
        il metodo genera un grafico del grafo. A discrezione dell’utente si
        può scegliere di visualizzare anche le etichette degli archi e/o dei nodi.
        il grafo viene visualizzato ponendo tutti i nodi su di una circonferenza.
        gli archi sono dunque visualizzati come corde di tale circonferenza. Gli
        id dei nodi sono sempre visualizzati. eventualmente le etichette relative
        agli archi sono visualizzate in un riquadro a destra del grafico


        :param etichette_nodi: bool dove True = voglio vedere le etichette relative ai nodi
                               mentre False = non voglio vedere le etichette relative ai nodi
                               DEFAULT:False
        :param etichette_archi:bool dove True = voglio vedere le etichette relative ai archi
                               mentre False = non voglio vedere le etichette relative ai archi
                               DEFAULT:False
        :return:
        
        """
        ax = plt.subplot(121, projection='polar')
        spaziatura=np.linspace(0.0, 2*np.pi,len(list(self.nodes.keys()))+1)
        r=[]
        volume = []
        j=-1
        for i in range(len(list(self.nodes.keys()))+1):
            j=j+1
            r.append(2)
            volume.append(300)
        for i in range(len(list(self.nodes.keys()))):
            ax.text(spaziatura[i],2.1,str(list(self.nodes.keys())[i]))
            if etichette_nodi==True:
                ax.text(spaziatura[i],2.3,str(list(self.nodes.values())[i].labels))            
        raggio_costante=np.array(r)
        ax.scatter(spaziatura,raggio_costante,volume)

        testo_archi=""
        for arco in self.get_edges():
            i=-1
            for idn in list(self.nodes.keys()):
                i=i+1
                if idn==arco[0]:
                    x1=spaziatura[i]
                if idn==arco[1]:
                    x2=spaziatura[i]
            #ax.plot(np.array([x1,x2]),np.array([2,2]),linewidth=self.get_edges_labels([arco])[0][arco]["weight"],color='red')
            #ax.arrow(x1,2,x2-x1,-0.2,head_width=0.1)
            ax.annotate("", xy=(x2, 1.9), xytext=(x1, 2),arrowprops=dict(arrowstyle="->"))
            testo_archi=testo_archi + "\n" + str(self.get_edges_labels([arco])[0])
            
        if etichette_archi==True:
            ax.text(0, 4, testo_archi, style='italic',bbox={'facecolor': 'white', 'alpha': 0.5, 'pad': 10})

        #ax.arrow(spaziatura[0],2,spaziatura[1]-spaziatura[0],-0.2,head_width=0.1,length_includes_head=True)


        
        
        
        ax.set_rmax(2)
        ax.set_rticks([])
        ax.set_thetagrids(())
        ax.grid(False)
        
        plt.show()

    def minpath_dijkstra(self,id_start,id_end):
        """
        Dati gli ID di due nodi, il metodo restituisce (se esiste) il cammino
        minimo, calcolato secondo l’algoritmo di Dijkstra. Restituisce una tupla
        con come primo elemento una tupla di id dei nodi per cui passa il percorso
        minimo e il costo di ogni passaggio

        :param id_start: id del nodo di partenza
        :param id_end: id del nodo di arrivo
        :return:(parenti, lista_pesi)

        N.B. il valore infinito utilizzato da Dijkstra è stato devinito inf=99999999999

        Se vengono forniti id inesistenti si riceve un messaggio
        di errore "input invalidi" e il metodo restituisce None,None

        Se vengono forniti il cammino desiderato non esiste si riceve un messaggio
        di errore "I nodi indicati non sono collegabili tra di loro" e il metodo
        restituisce None, None

        """
        if (id_start not in self.nodes.keys()) or (id_end not in self.nodes.keys()):
            print("input invalidi")
            return None, None
        inf=99999999999

        costo_nodi={}
        parents={}
        non_processati=list(self.nodes.keys())

        for nodo in self.nodes.keys():
            costo_nodi[nodo]=inf
            #parents[nodo]=None
        costo_nodi[id_start]=0
        

        while non_processati != []:
            nodo_minimo=id_start
            temp_dict={}
            for nodo in costo_nodi:
                if nodo in non_processati:
                    temp_dict[nodo]=costo_nodi[nodo]
            for nodo in costo_nodi:
                if costo_nodi[nodo] == min(list(temp_dict.values())):
                    nodo_minimo=nodo
            if costo_nodi[nodo_minimo]==inf:
                print("I nodi indicati non sono collegabili tra di loro")
                return None,None
            
            for vicino in self.nodes[nodo_minimo].neighbours_out:
                temp =vicino[1]["weight"] + costo_nodi[nodo_minimo]
                if temp<costo_nodi[vicino[0].id]:
                    costo_nodi[vicino[0].id]=vicino[1]["weight"] + costo_nodi[nodo_minimo]
                    parents[vicino[0].id]=nodo_minimo
            non_processati.append(None)
            for i in range(len(non_processati)-1):
                if non_processati[i]==nodo_minimo:
                    del non_processati[i]
                    #del costo_nodi[nodo_minimo]
            del non_processati[-1]
            if id_end not in non_processati:
                non_processati.clear()
                
        if id_end not in parents.keys():
            parents[id_end]=id_end
        #del parents[list(parents.keys())[0]]
        parenti=list(parents.values())
        for padre in parenti:
            copiaparenti=parenti.copy()
            copiaparenti.remove(padre)
            if padre in copiaparenti:
                parenti.remove(padre)
        lista_pesi=[]
        for i in range(len(parenti)-1):
            nodo1=(parenti)[i]
            nodo2=(parenti)[i+1]
            peso_passo=self.get_edges_labels([(nodo1,nodo2)])[0][(nodo1,nodo2)]["weight"]
            lista_pesi.append(peso_passo)

        return tuple(parenti),tuple(lista_pesi)



    
