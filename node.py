class Node:
    def __init__(self, id: str, nombre: str):
        self.id = id
        self.nombre = nombre
        self.esta_activo = True
        self.es_proponente = False

        # Aceptante
        self.id_prepare_mas_alta: int | None = None
        self.id_aceptada: int | None = None
        self.comando_aceptado: str | None = None

        # Proponente
        self.id_propuesta_activa: int | None = None
        self.comando_propuesta: str | None = None
        self.cant_nodos_prepare: int = 0

        self.id_aceptado_viejo: int | None = None
        self.comando_aceptado_viejo: str | None = None

    def set_proponente(self, status: bool):
        estado_viejo, self.es_proponente = self.es_proponente, status
        if estado_viejo != status:
            self.resetear_estado()

    def resetear_estado(self):
        # Proponente
        self.id_propuesta_activa = None
        self.comando_propuesta = None
        self.cant_nodos_prepare = 0
        self.id_aceptado_viejo = None
        self.comando_aceptado_viejo = None
        # Aceptante
        self.id_prepare_mas_alta = None
        self.id_aceptada = None
        self.comando_aceptado = None

    # Proponente
    def empezar_prepare(self, id_propuesta: int):
        if not self.es_proponente:
            raise Exception(f"Node {self.nombre} no es proponente.")
        self.id_propuesta_activa = id_propuesta
        self.comando_propuesta = None
        self.cant_nodos_prepare = 0

    def aceptar_prepare(self, id_aceptado_old: int | None, comando_aceptado_old: str | None):
            self.cant_nodos_prepare += 1
            if id_aceptado_old is not None:
                # Si no teníamos ningún valor viejo o si el nuevo es mayor
                if self.id_aceptado_viejo is None or id_aceptado_old > self.id_aceptado_viejo:
                    self.id_aceptado_viejo = id_aceptado_old
                    self.comando_aceptado_viejo = comando_aceptado_old

    # Aceptante
    def responder_prepare(self, id_propuesta: int):
        if not self.esta_activo:
            return False, None, None

        if self.id_prepare_mas_alta is None or id_propuesta > self.id_prepare_mas_alta:
            self.id_prepare_mas_alta = id_propuesta
            return True, self.id_aceptada, self.comando_aceptado

        return False, None, None

    def responder_accept(self, id_propuesta: int, comando: str):
        if not self.esta_activo:
            return False

        if self.id_prepare_mas_alta is None or id_propuesta >= self.id_prepare_mas_alta:
            self.id_prepare_mas_alta = id_propuesta
            self.id_aceptada = id_propuesta
            self.comando_aceptado = comando
            return True

        return False
