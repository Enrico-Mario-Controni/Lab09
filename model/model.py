from database.regione_DAO import RegioneDAO
from database.tour_DAO import TourDAO
from database.attrazione_DAO import AttrazioneDAO

class Model:
    def __init__(self):
        self.tour_map = {} # Mappa ID tour -> oggetti Tour
        self.attrazioni_map = {} # Mappa ID attrazione -> oggetti Attrazione

        self._pacchetto_ottimo = []
        self._valore_ottimo: int = -1
        self._costo = 0

        # TODO: Aggiungere eventuali altri attributi

        # Caricamento
        self.load_tour()
        self.load_attrazioni()
        self.load_relazioni()

    @staticmethod
    def load_regioni():
        """ Restituisce tutte le regioni disponibili """
        return RegioneDAO.get_regioni()

    def load_tour(self):
        """ Carica tutti i tour in un dizionario [id, Tour]"""
        self.tour_map = TourDAO.get_tour()

    def load_attrazioni(self):
        """ Carica tutte le attrazioni in un dizionario [id, Attrazione]"""
        self.attrazioni_map = AttrazioneDAO.get_attrazioni()

    def load_relazioni(self):
        """
            Interroga il database per ottenere tutte le relazioni fra tour e attrazioni e salvarle nelle strutture dati
            Collega tour <-> attrazioni.
            --> Ogni Tour ha un set di Attrazione.
            --> Ogni Attrazione ha un set di Tour.
        """

        # TODO
        relazioni= TourDAO.get_tour_attrazioni()

        for el in relazioni:
            id_tour= el["id_tour"]
            id_attrazioni= el["id_attrazione"]

            tour= self.tour_map[id_tour]
            attrazioni= self.attrazioni_map[id_attrazioni]

            tour.attrazioni.add(attrazioni)
            attrazioni.tour.add(tour)



    def genera_pacchetto(self, id_regione: str, max_giorni: int = None, max_budget: float = None):
        """
        Calcola il pacchetto turistico ottimale per una regione rispettando i vincoli di durata, budget e attrazioni uniche.
        :param id_regione: id della regione
        :param max_giorni: numero massimo di giorni (può essere None --> nessun limite)
        :param max_budget: costo massimo del pacchetto (può essere None --> nessun limite)

        :return: self._pacchetto_ottimo (una lista di oggetti Tour)
        :return: self._costo (il costo del pacchetto)
        :return: self._valore_ottimo (il valore culturale del pacchetto)
        """
        self._pacchetto_ottimo = []
        self._costo = 0
        self._valore_ottimo = -1

        # TODO
        lista_tour=[]
        for el in self.tour_map.values():
            if el.id_regione == id_regione:
                lista_tour.append(el)

        self._ricorsione(0,[],0,0,0,set(),lista_tour,
                         max_giorni, max_budget)


        return self._pacchetto_ottimo, self._costo, self._valore_ottimo

    def _ricorsione(self, start_index: int, pacchetto_parziale: list, durata_corrente: int, costo_corrente: float,
                    valore_corrente: int, attrazioni_usate: set, lista_tour, max_giorni, max_budget):
        """ Algoritmo di ricorsione che deve trovare il pacchetto che massimizza il valore culturale"""

        # TODO: è possibile cambiare i parametri formali della funzione se ritenuto opportuno
        if valore_corrente > self._valore_ottimo:
            self._valore_ottimo = valore_corrente
            self._pacchetto_ottimo = pacchetto_parziale.copy()
            self._costo = costo_corrente

        for i in range(start_index, len(lista_tour)):
            tour = lista_tour[i]


            nuove_attrazioni=set()
            for attr in tour.attrazioni:
                if attr not in attrazioni_usate:
                    nuove_attrazioni.add(attr)

            nuova_durata = durata_corrente+ tour.durata_giorni
            nuovo_costo = costo_corrente + tour.costo

            nuovo_valore = valore_corrente + sum(attr.valore_culturale for attr in nuove_attrazioni)

            if (max_giorni is not None and max_giorni < nuova_durata) or (max_budget is not None and max_budget < nuovo_costo):
                continue


            pacchetto_parziale.append(tour)
            for attr in nuove_attrazioni:
                attrazioni_usate.add(attr)

            self._ricorsione(i+1, pacchetto_parziale=pacchetto_parziale, durata_corrente=nuova_durata,
                costo_corrente=nuovo_costo,valore_corrente=nuovo_valore, attrazioni_usate=attrazioni_usate,
                lista_tour=lista_tour, max_giorni=max_giorni, max_budget=max_budget)

            pacchetto_parziale.pop()
            for attr in nuove_attrazioni:
                attrazioni_usate.remove(attr)

