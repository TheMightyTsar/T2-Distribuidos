from node import Node


class Simulacion:
    def __init__(self, cant_proponentes: int, nodes: list[str], ids: list[str]):
        self.cant_proponentes = cant_proponentes
        self.nodos = [Node(id=id, nombre=node) for node, id in zip(nodes, ids)]
        self.nodos.sort(key=lambda node: node.id, reverse=True)
        self.bd: dict[str, str | int] = {}
        self.logs: list[str] = []

    def clonar(self):  # TODO: nodos se resetean o se copian?
        nueva_simulacion = Simulacion(
            self.cant_proponentes,
            [node.nombre for node in self.nodos],
            [node.id for node in self.nodos],
        )
        nueva_simulacion.bd = self.bd.copy()
        nueva_simulacion.logs = self.logs.copy()
        return nueva_simulacion

    def ejecutar_bully(self):
        # TODO: handle case where there are not enough active nodes to be proponents
        # TODO: if a node is already a proponente, it should keep its status unless it becomes inactive
        # Encontrar los cant_proponentes nodos con mayor ID activos y marcarlos como proponentes
        proponentes = sum(
            1 for node in self.nodos if node.es_proponente and node.esta_activo
        )
        for node in self.nodos:
            if proponentes >= self.cant_proponentes:
                break
            if node.esta_activo and not node.es_proponente:
                node.set_proponente(True)
                proponentes += 1

    def procesar_evento(self, evento: str, args: list[str]):
        if evento == "Prepare":
            self.procesar_prepare(args)
        elif evento == "Accept":
            self.procesar_accept(args)
        elif evento == "Stop":
            self.procesar_stop(args)
        elif evento == "Start":
            self.procesar_start(args)
        elif evento == "Learn":
            self.procesar_learn(args)
        elif evento == "Log":
            self.procesar_log(args)

    def procesar_prepare(self, args: list[str]):
        """
        El proponente se comunica con los aceptantes activos y evalúa sus respuestas: aceptación,
        rechazo, ausencia de respuesta por nodo caído (equivale a rechazo) o aceptación condicionada
        según Paxos.
        """
        nombre_nodo, id_propuesta = args
        nodo = self.get_nodo_by_name(nombre_nodo)
        if not nodo:
            return
        if not nodo.es_proponente:
            return
        id_propuesta = int(id_propuesta)
        nodo.empezar_prepare(id_propuesta)

        # Envia el mensaje a los aceptantes
        for otro_nodo in self.nodos:
            if otro_nodo.es_proponente:
                continue
            acepta, id_aceptada, comando_aceptado = otro_nodo.responder_prepare(id_propuesta)
            if acepta:
                nodo.aceptar_prepare(id_aceptada, comando_aceptado)

    def procesar_accept(self, args: list[str]):
        """
        Envía una operación a los aceptantes activos. Solo es válido si el proponente
        ejecutó previamente un Prepare con el mismo identificador y obtuvo las aceptaciones
        necesarias según el consenso. La operación debe cumplir las reglas de Paxos: puede ser la
        indicada en el mismo evento o una previamente aceptada por algún aceptante.
        """
        nombre_nodo, id_propuesta, comando_que_quiere = args
        nodo = self.get_nodo_by_name(nombre_nodo)
        if not nodo:
            return
        if not nodo.es_proponente:
            return
        id_propuesta = int(id_propuesta)
        if nodo.id_propuesta_activa != id_propuesta:
            return

        # No cumple quorum
        cantidad_nodos_activos = sum(1 for node in self.nodos if node.esta_activo)
        cantidad_aceptantes = cantidad_nodos_activos - self.cant_proponentes
        if nodo.cant_nodos_prepare <= cantidad_aceptantes / 2:
            return

        for otro_nodo in self.nodos:
            if otro_nodo.es_proponente:
                continue
            comando = comando_que_quiere
            if nodo.comando_aceptado_viejo is not None:
                comando = nodo.comando_aceptado_viejo
            otro_nodo.responder_accept(id_propuesta, comando)

    def procesar_stop(self, args: list[str]):
        nodos = args
        if not self.are_all_nodes_valid(nodos):
            return

    def procesar_start(self, args: list[str]):
        nodos = args
        if not self.are_all_nodes_valid(nodos):
            return

    def procesar_learn(self, args: list[str]):
        pass

    def procesar_log(self, args: list[str]):
        pass

    def get_nodo_by_name(self, name: str) -> Node | None:
        for node in self.nodos:
            if node.nombre == name:
                return node
        return None

    def are_all_nodes_valid(self, nodes: list[str]) -> bool:
        node_names = (node.nombre for node in self.nodos)
        return all(node in node_names for node in nodes)
