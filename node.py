class Node:
    def __init__(self, id: str, nombre: str):
        self.id = id
        self.nombre = nombre
        self.esta_activo = True
        self.es_proponente = False

    def set_proponente(self, status: bool):
        self.es_proponente = status
        self.clear_status()  # TODO: el estado solo se resetea si hay un cambio de proponente a no proponente o viceversa, no cada vez que se llama a set_proponente

    def clear_status(self):
        self.esta_activo = True
        self.es_proponente = False
