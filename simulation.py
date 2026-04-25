from node import Node


class Simulacion:
    def __init__(self, cant_proponentes: int, nodes: list[Node]):
        self.cant_proponentes = cant_proponentes
        self.nodos = nodes
        self.bd: dict[str, str | int] = {}
        self.logs: list[str] = []

    def clonar(self):
        nueva_simulacion = Simulacion(
            self.cant_proponentes,
            [nodo.clonar() for nodo in self.nodos]
        )
        nueva_simulacion.bd = self.bd.copy()
        nueva_simulacion.logs = self.logs.copy()
        return nueva_simulacion

    def ejecutar_bully(self):
        cant_proponentes_activos = len(self.get_proponentes_activos())
        for node in self.nodos:
            if cant_proponentes_activos >= self.cant_proponentes:
                break
            if node.esta_activo and not node.es_proponente:
                node.set_proponente(True)
                cant_proponentes_activos += 1

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
            self.procesar_learn()

    def procesar_prepare(self, args: list[str]):
        """
        El proponente se comunica con los aceptantes activos y evalúa sus respuestas: aceptación,
        rechazo, ausencia de respuesta por nodo caído (equivale a rechazo) o aceptación condicionada
        según Paxos.
        """
        nombre_nodo, id_propuesta = args
        nodo = self.get_nodo_by_name(nombre_nodo)
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
        if not nodo.es_proponente:
            print(f"Nodo {nombre_nodo} no es proponente. Ignorando evento Accept.")
            return
        id_propuesta = int(id_propuesta)
        if nodo.id_propuesta_activa != id_propuesta:
            print(f"Nodo {nombre_nodo} no tiene una propuesta activa con id {id_propuesta}. Ignorando evento Accept.")
            return

        if not self.has_quorum(nodo.cant_nodos_prepare):
            print(f"Nodo {nombre_nodo} no alcanzó quorum para propuesta {id_propuesta}. Ignorando evento Accept.")
            return

        comando_final = comando_que_quiere
        if nodo.comando_aceptado_viejo is not None:
            comando_final = nodo.comando_aceptado_viejo

        print("Proponente", nodo.nombre, "emite Accept con comando final:", comando_final)
        for otro_nodo in self.nodos:
            if otro_nodo.es_proponente:
                continue
            otro_nodo.responder_accept(id_propuesta, comando_final)

    def procesar_stop(self, args: list[str]):
        nodos = args
        for nodo in self.nodos:
            if nodo.nombre in nodos:
                nodo.esta_activo = False
        self.ejecutar_bully()

    def procesar_start(self, args: list[str]):
        nodos = args

        proponentes_activos = len(self.get_proponentes_activos())
        for nodo in self.nodos:
            if nodo.nombre in nodos:
                nodo.esta_activo = True

                if nodo.es_proponente:
                    if proponentes_activos >= self.cant_proponentes:
                        nodo.set_proponente(False)
                    else:
                        proponentes_activos += 1
        self.ejecutar_bully()

    def procesar_learn(self):
        aceptantes_activos = self.get_aceptantes_activos()

        votos_por_comando = {}
        for nodo in aceptantes_activos:
            if nodo.comando_aceptado is not None:
                cmd = nodo.comando_aceptado
                votos_por_comando[cmd] = votos_por_comando.get(cmd, 0) + 1

        print(f"Votos por comando: {votos_por_comando}")

        for cmd, votos in votos_por_comando.items():
            if votos > (len(aceptantes_activos) / 2):
                self.ejecutar_comando(cmd)
            else:
                print(f"Comando {cmd} no alcanzó quorum con {votos} votos")

        for nodo in self.nodos:
            if nodo.esta_activo:
                nodo.resetear_estado()

    def has_quorum(self, cantidad: int):
        cantidad_aceptantes_activos = len(self.get_aceptantes_activos())
        return cantidad > cantidad_aceptantes_activos / 2

    def get_aceptantes_activos(self):
        return [nodo for nodo in self.nodos if not nodo.es_proponente and nodo.esta_activo]

    def get_proponentes_activos(self):
        return [nodo for nodo in self.nodos if nodo.es_proponente and nodo.esta_activo]

    def get_nodo_by_name(self, name: str):
        for node in self.nodos:
            if node.nombre == name:
                return node
        raise Exception(f"Nodo con nombre {name} no encontrado.")

    def ejecutar_comando(self, cmd: str):
        comando, variable, *valor = cmd.split("-")
        valor = "-".join(valor)
        if comando == "SET":
            if valor.isdigit():
                valor = int(valor)
            self.bd[variable] = valor
        elif comando == "ADD":
            valor_actual = self.bd.get(variable, None)
            if valor_actual is None:
                return self.ejecutar_comando(f"SET-{variable}-{valor}")
            elif isinstance(valor_actual, int) and valor.isdigit():
                self.bd[variable] = valor_actual + int(valor)
            else:
                self.bd[variable] = str(valor_actual) + valor
        elif comando == "DEL":
            if variable in self.bd:
                del self.bd[variable]

# TODO: Adicionalmente, una vez que el proponente emite un Accept, re-cuerda el identificador de propuesta utilizado, pudiendo reenviar mensajes Accept con ese mismo identificador. En estos reenvíos, la operación se mantiene invariante.