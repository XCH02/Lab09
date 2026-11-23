from database.parco_DAO import ParcoDAO
from database.escursione_DAO import EscursioneDAO
from database.punto_interesse_DAO import PuntoInteresseDAO
from model import escursione


class Model:
    def __init__(self):
        self.escursioni_map = {} # Mappa ID escursione -> oggetti Escursione
        self.punti_interesse_map = {} # Mappa ID punto di interesse -> oggetti PuntoInteresse

        self._pacchetto_ottimo = []
        self._valore_ottimo: int = -1
        self._costo = 0

        # TODO: Aggiungere eventuali altri attributi

        # Caricamento
        self.load_escursioni()
        self.load_punti_interesse()
        self.load_relazioni()

    @staticmethod
    def load_parchi():
        """ Restituisce tutti i parchi disponibili """
        return ParcoDAO.get_parchi()

    def load_escursioni(self):
        """ Carica tutte le escursioni in un dizionario [id, Escursione]"""
        self.escursioni_map = EscursioneDAO.get_escursioni()

    def load_punti_interesse(self):
        """ Carica tutti i punti di interesse in un dizionario [id, PuntoInteresse]"""
        self.punti_interesse_map = PuntoInteresseDAO.get_punti_interesse()

    def load_relazioni(self):
        """
            Interroga il database per ottenere tutte le relazioni fra escursioni e punti di interesse e salvarle nelle strutture dati
            Collega escursione <-> punti di interesse.
            --> Ogni Escursione ha un set di PuntoInteresse.
            --> Ogni PuntoInteresse ha un set di Escursioni.
        """
        # TODO
        #Metto in relazione escursione e punti di interesse
        #prendo le relazioni dal database
        relazioni = EscursioneDAO.get_escursioni_punti_interesse()

        if relazioni is None:
            return
        else:
            for relazione in relazioni:
                #recupero oggetto puntointeresse e escursione
                id_esc = relazione["id_escursione"]
                id_punto= relazione["id_punto_interesse"]
                #per ogni valore del dizionario escursione
                for escursione in self.escursioni_map.values():
                    #per ogni valore del dizionario puntiinteresse
                    for punto in self.punti_interesse_map.values():
                        #quando id escursione è ugaule a quello della relazione e quello del punto uguale a quello della relazione
                        #in questo modo ho trovato la relazione corrispondente poi li collego
                        if escursione.id ==id_esc and punto.id == id_punto:
                            escursione.punti_interesse.add(punto)
                            punto.escursioni.add(escursione)

    def genera_pacchetto(self, id_parco: str, max_giorni: int = None, max_budget: float = None):
        """
        Calcola il pacchetto di escursioni ottimale per un parco rispettando i vincoli di durata, budget e punti di interesse unici.
        :param id_parco: id del parco
        :param max_giorni: numero massimo di giorni (può essere None --> nessun limite)
        :param max_budget: costo massimo del pacchetto (può essere None --> nessun limite)

        :return: self._pacchetto_ottimo (una lista di oggetti Escursione)
        :return: self._costo (il costo del pacchetto)
        :return: self._valore_ottimo (il voto complessivo dei visitatori per il pacchetto)
        """
        self._pacchetto_ottimo = []
        self._costo = 0
        self._valore_ottimo = -1

        # TODO
        self._escursioni_parco = []

        for escursione in self.escursioni_map.values():
            if escursione.id_parco == id_parco:
                self._escursioni_parco.append(escursione)

        self._ricorsione(0,[],0,0,0,set(),max_giorni,max_budget)

        return self._pacchetto_ottimo, self._costo, self._valore_ottimo

    def _ricorsione(self, start_index: int, pacchetto_parziale: list, durata_corrente: int, costo_corrente: float, valore_corrente: int, punti_usati: set,max_giorni, max_budget):
        """ Algoritmo di ricorsione che deve trovare il pacchetto che massimizza il voto complessivo dei visitatori"""

        # TODO: è possibile cambiare i parametri formali della funzione se ritenuto opportuno

        #PUNTO A SEMPRE ESEGUITO Aggiornamento soluzione migliore
        if valore_corrente > self._valore_ottimo:
            self._valore_ottimo = valore_corrente
            self._pacchetto_ottimo = pacchetto_parziale.copy()
            self._costo = costo_corrente
        #Qui genero le possibili scelte
        for i in range(start_index, len(self._escursioni_parco)):
            escursione=self._escursioni_parco[i]

            #PUNTO C Filtri controllo i vincoli
            valida=True
            #controllo budget
            if max_budget is not None:
                if costo_corrente +escursione.costo > max_budget:
                    valida=False

            #controllo giorni

            if max_giorni is not None:
                if durata_corrente +escursione.durata_giorni > max_giorni:
                    valida = False

            #controllo punti di interesse duplicati
            for punto in escursione.punti_interesse:
                if punto in punti_usati:
                    valida = False
                    break
            #PUNTO D COMPUTE PARTIAL
            if valida:
                #aggiungo escursione
                pacchetto_parziale.append(escursione)
                #aggiorno giorni e costo, sommo i voti di punti di interesse
                # e aggiungo i punti al set dei punti già usati
                durata_corrente = durata_corrente + escursione.durata_giorni
                costo_corrente= costo_corrente + escursione.costo
                for punto in escursione.punti_interesse:
                    valore_corrente = valore_corrente + punto.voto_visitatori
                    punti_usati.add(punto)


                #PUNTO E CHIAMO RICORSIONE
                self._ricorsione(i+1,pacchetto_parziale, durata_corrente, costo_corrente, valore_corrente, punti_usati, max_giorni, max_budget)

                #PUNTO F Backtracking
                pacchetto_parziale.pop()
                durata_corrente = durata_corrente-escursione.durata_giorni
                costo_corrente = costo_corrente-escursione.costo
                for punto in escursione.punti_interesse:
                    valore_corrente = valore_corrente-punto.voto_visitatori
                    punti_usati.remove(punto)



