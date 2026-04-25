# Informe material externo

# Material externo no IA

Nada

## Uso de IA

Para los distintos usos de IA se debe incluir:
1. _Prompt_ o conjunto de _prompt_ utilizados. 
2. Explicar qué uso se le dió a la respuesta de la IA.

### Caso 1: Comprensión de reglas y casos borde mediante NotebookLM

> **Instrucción / Contexto**: Se cargó el enunciado completo de la tarea en NotebookLM como fuente de verdad. Los prompts realizados fueron:
> 1. "¿Podría pasar que haya una variable que no está en la base de datos de una bifurcación? ¿Qué se hace en ese caso al momento de crear los logs?"
> 2. "¿Como se decide el orden de variables?"
> 3. "¿A qué se refiere con esto el enunciado?: 'Adicionalmente, una vez que el proponente emite un Accept, recuerda el identificador de propuesta utilizado, pudiendo reenviar mensajes Accept con ese mismo identificador. En estos reenvíos, la operación se mantiene invariante.'"

**Uso**: La IA se utilizó exclusivamente como herramienta de comprensión de lectura y aclaración de reglas del enunciado. No se utilizó para la generación, corrección o sugerencia de código. Las respuestas ayudaron a entender situaciones especiales (como el manejo de variables inexistentes en los logs) y a interpretar correctamente la lógica de idempotencia en los mensajes Accept con identificadores repetidos.

## Ejecución de código

```bash
python3 main.py tests_publicos/test_01.txt