# Solo puedes importar las siguientes librerías y ninguna otra
import sys
# Librerías adicionales por si necesitas ocuparlas. No son esperadas, pero puedes usarlas si quieres.
import typing, os, pathlib, math, re, collections

from simulation import Simulacion

def remove_comments(line: str) -> str:
    return line.split("#")[0].strip()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python3 main.py [PATH_TO_INPUT_FILE]")
        sys.exit(1)

    print(sys.argv)
    
    path = sys.argv[1]
    name_without_extension = os.path.splitext(os.path.basename(path))[0]
    
    with open(os.path.join("logs", f"{name_without_extension}_LOG.txt"), "w") as log_file:
        pass
    
    simulaciones = []
    with open(path, "r") as input_file:
        line1 = input_file.readline().strip()
        cant_proponents = int(remove_comments(line1))
        
        line2 = input_file.readline().strip()
        nodos = remove_comments(line2).split(";")
        
        line3 = input_file.readline().strip()
        ids = remove_comments(line3).split(";")
        
        simulacion_inicial = Simulacion(cant_proponents, nodos, ids)
        simulacion_inicial.ejecutar_bully()
        simulaciones.append(simulacion_inicial)
        
        for line in input_file:
            line = remove_comments(line)
            
            if not line:
                continue
            # if nodo_no_existe(line):
            #     continue
                
            print(f"Processing line: {line}")
            es_bifurcacion = line.startswith("*")
            command, *args = line.lstrip("*").split(";")
            
            print(f"Command: {command}, Args: {args}, Bifurcation: {es_bifurcacion}")
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
        
            
