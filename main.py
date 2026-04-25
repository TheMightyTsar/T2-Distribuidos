# Solo puedes importar las siguientes librerías y ninguna otra
import sys

# Librerías adicionales por si necesitas ocuparlas. No son esperadas, pero puedes usarlas si quieres
import typing, os, pathlib, math, re, collections

from simulation import Simulacion
from node import Node


def remove_comments(line: str) -> str:
    return line.split("#")[0].strip()

def log(name_without_extension: str, message: str, clear_previous: bool = False):
    path = os.path.join("logs", f"{name_without_extension}_LOG.txt")
    if clear_previous and os.path.exists(path):
        os.remove(path)
    with open(path, "a", encoding="utf-8") as log_file:
        log_file.write(message + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python3 main.py [PATH_TO_INPUT_FILE]")
        sys.exit(1)

    path = sys.argv[1]
    name_without_extension = os.path.splitext(os.path.basename(path))[0]

    log(name_without_extension, "LOGS", clear_previous=True)

    simulaciones: list[Simulacion] = []
    hizo_log = False
    with open(path, "r", encoding="utf-8") as input_file:
        line1 = input_file.readline().strip()
        cant_proponents = int(remove_comments(line1))

        line2 = input_file.readline().strip()
        nodos = remove_comments(line2).split(";")
        nodos_validos = set(nodos)

        line3 = input_file.readline().strip()
        ids = remove_comments(line3).split(";")

        nodos = [Node(id=int(id), nombre=node) for node, id in zip(nodos, ids)]
        nodos.sort(key=lambda node: node.id, reverse=True)
        simulacion_inicial = Simulacion(cant_proponents, nodos)
        simulacion_inicial.ejecutar_bully()
        simulaciones.append(simulacion_inicial)

        for line in input_file:
            line = remove_comments(line)

            if not line:
                continue

            es_bifurcacion = line.startswith("*")
            command, *args = line.lstrip("*").split(";")

            print(f"\nCommand: {command}, Args: {args}, Bifurcation: {es_bifurcacion}")
            if command == "Log":
                hizo_log = True
                variable = args[0]

                valores = []
                for simulacion in simulaciones:
                    valor = simulacion.bd.get(variable, None)
                    if valor is not None and valor not in valores:
                        valores.append(valor)
                log(name_without_extension, f"{variable}={str(valores)}")
                continue

            # Validar nodos
            nodos_involucrados = []
            if command in ("Prepare", "Accept") and len(args) > 0:
                nodos_involucrados.append(args[0])
            elif command in ("Stop", "Start"):
                nodos_involucrados.extend(args)

            if not all(nodo in nodos_validos for nodo in nodos_involucrados):
                continue

            if es_bifurcacion:
                nuevas_simulaciones = []
                for simulacion in simulaciones:
                    copia_sim = simulacion.clonar()
                    simulacion.procesar_evento(command, args)
                    nuevas_simulaciones.append(copia_sim)
                simulaciones.extend(nuevas_simulaciones)
            else:
                for simulacion in simulaciones:
                    simulacion.procesar_evento(command, args)

    if not hizo_log:
        log(name_without_extension, "No hubo logs")

    log(name_without_extension, "BASE DE DATOS")

    dict_variable_valores: dict[str, set[str | int]] = {}
    for simulacion in simulaciones:
        print("Simulación con BD:", simulacion.bd)
        for variable, valor in simulacion.bd.items():
            if variable not in dict_variable_valores:
                dict_variable_valores[variable] = set()
            dict_variable_valores[variable].add(valor)
    for variable, valores in dict_variable_valores.items():
        log(name_without_extension, f"{variable}={str(list(valores))}")
    if not dict_variable_valores:
        log(name_without_extension, "No hay datos")
