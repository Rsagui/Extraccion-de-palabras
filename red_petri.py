import re
import unicodedata
from graphviz import Digraph
import time
import os

# Función para eliminar las tíldes que alguien pone pro consola, porque siento que será más fácil :0
def es_alfanumerico(texto):
    texto_normalizado = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    return bool(re.fullmatch(r'^(?=.*[A-Za-z])(?=.*[0-9])[A-Za-z0-9]+$', texto_normalizado))

# Función menú para salir del juego o seguir jugando:
def menu():
    global variable_para_parar_el_codigo  # Añadido para modificar la variable global
    variable_para_parar_romper_bucles = True  
    while variable_para_parar_romper_bucles:
        seguir_jugando = input("Presiona 1 si quieres seguir jugando o 0 para salir: ").strip()
        
        if seguir_jugando not in ('0', '1'):
            print("¡Solo puedes ingresar 1 o 0!")
        elif seguir_jugando == '1':
            variable_para_parar_romper_bucles = False
            print("¡Sigamos jugando pues!")
        elif seguir_jugando == '0':
            variable_para_parar_romper_bucles = False
            variable_para_parar_el_codigo = False
            print("¡Hasta pronto!")

# Función para visualizar la red de Petri
def visualizar_red(red, paso_actual=None, letra_actual=None, paso_descripcion=""):
    try:
        dot = Digraph(comment='Red de Petri para "aprobado"')
        
        # Configuración general del gráfico
        dot.attr(rankdir='TB', size='12,12', dpi='300', nodesep='0.5', ranksep='1.0')
        dot.attr('graph', fontsize='14', fontname='Arial')
        
        # Configuración de nodos (lugares)
        dot.attr('node', 
                shape='circle', 
                width='1', 
                height='1',
                fixedsize='true',
                style='filled',
                fillcolor='lightblue',
                fontname='Arial',
                fontsize='12')
        
        # Configuración de transiciones
        dot.attr('node', 
                shape='rectangle', 
                width='0.8', 
                height='0.3',
                style='filled',
                fillcolor='lightgray',
                fontname='Arial',
                fontsize='10')
        
        # Dibujar lugares con tokens
        for lugar, tokens in red.lugares.items():
            # Color diferente para lugares con tokens
            fill = 'lightblue' if tokens > 0 else 'white'
            border = 'blue' if tokens > 0 else 'black'
            dot.node(lugar, 
                    f"{lugar}\n({tokens} token{'s' if tokens != 1 else ''})",
                    fillcolor=fill,
                    color=border,
                    penwidth='2' if tokens > 0 else '1')
        
        # Dibujar transiciones
        for transicion in red.transiciones:
            label = transicion.split('_')[-1] if '_' in transicion else transicion
            dot.node(transicion, label)
        
        # Dibujar arcos con flechas más claras
        for transicion, datos in red.transiciones.items():
            for lugar, peso in datos['inputs']:
                dot.edge(lugar, transicion, 
                        label=str(peso),
                        arrowsize='0.8',
                        penwidth='1.5')
            for lugar, peso in datos['outputs']:
                dot.edge(transicion, lugar, 
                        label=str(peso),
                        arrowsize='0.8',
                        penwidth='1.5')
        
        # Organización jerárquica para mejor visualización
        with dot.subgraph() as s:
            s.attr(rank='same')
            for lugar in ['inicio', 'A', 'P', 'R', 'O', 'B', 'A2', 'D', 'O2', 'aprobado']:
                s.node(lugar)
        
        # Título y metadatos del gráfico
        titulo = f"Red de Petri - Paso: {paso_actual}" if paso_actual else "Red de Petri"
        if letra_actual:
            titulo += f"\nLetra actual: '{letra_actual}'"
        if paso_descripcion:
            titulo += f"\n{paso_descripcion}"
        
        dot.attr(label=f"{titulo}\n\n", 
                labelloc='t', 
                fontsize='16',
                fontname='Arial Bold')
        
        # Crear directorio si no existe
        os.makedirs('red_petri_graphs', exist_ok=True)
        
        # Ruta del archivo con mejor formato
        filepath = os.path.join('red_petri_graphs', f'paso_{paso_actual:02d}_red_petri')
        
        # Renderizar con formato SVG (mejor calidad) y PNG
        dot.render(filepath, 
                  view=True, 
                  format='png',
                  cleanup=True)
        
        print(f"\n✅ Gráfico generado: {filepath}.png")
        time.sleep(0.5)  # Pausa más corta
        
    except Exception as e:
        print(f"\n❌ Error al generar el gráfico: {str(e)}")

        

# Modelado de red de Petri para extraer "aprobado" (VERSIÓN CORREGIDA)
def red_petri_aprobado(cadena, visualizar=False):
    # Definición formal de la Red de Petri (CORREGIDA)
    class RedPetri:
        def __init__(self):
            # Lugares (con capacidad para múltiples tokens) - CORREGIDO
            self.lugares = {
                'inicio': 1,  # Token inicial
                'A': 0, 'P': 0, 'R': 0, 'O': 0, 'B': 0, 
                'A2': 0, 'D': 0, 'O2': 0,  # Lugares renombrados para evitar conflictos
                'aprobado': 0
            }
            
            # Transiciones con múltiples arcos de entrada/salida - CORREGIDO
            self.transiciones = {
                'encontrar_A': {'inputs': [('inicio', 1)], 'outputs': [('A', 1)]},
                'encontrar_P': {'inputs': [('A', 1)], 'outputs': [('P', 1)]},
                'encontrar_R': {'inputs': [('P', 1)], 'outputs': [('R', 1)]},
                'encontrar_O': {'inputs': [('R', 1)], 'outputs': [('O', 1)]},
                'encontrar_B': {'inputs': [('O', 1)], 'outputs': [('B', 1)]},
                'encontrar_A2': {'inputs': [('B', 1)], 'outputs': [('A2', 1)]},
                'encontrar_D': {'inputs': [('A2', 1)], 'outputs': [('D', 1)]},
                'encontrar_O2': {'inputs': [('D', 1)], 'outputs': [('O2', 1)]},
                'completado': {'inputs': [('O2', 1)], 'outputs': [('aprobado', 1)]}
            }
            
            # Historial de disparos para análisis
            self.historial = []
            self.paso_actual = 0
        
        def transicion_disponible(self, nombre_transicion):
            """Verifica si una transición puede dispararse"""
            trans = self.transiciones[nombre_transicion]
            return all(self.lugares[lugar] >= peso for lugar, peso in trans['inputs'])
        
        def disparar_transicion(self, nombre_transicion, letra_actual=None, visualizar=False):
            """Ejecuta una transición si es posible"""
            if not self.transicion_disponible(nombre_transicion):
                return False
            
            trans = self.transiciones[nombre_transicion]
            
            # Antes de disparar
            if visualizar:
                print(f"\n[Paso {self.paso_actual}] Antes de disparar '{nombre_transicion}':")
                for lugar, peso in trans['inputs']:
                    print(f"  - Lugar '{lugar}': {self.lugares[lugar]} token(s)")
            
            # Consumir tokens de inputs
            for lugar, peso in trans['inputs']:
                self.lugares[lugar] -= peso
            
            # Producir tokens en outputs
            for lugar, peso in trans['outputs']:
                self.lugares[lugar] += peso
            
            self.historial.append(nombre_transicion)
            
            # Después de disparar
            if visualizar:
                print(f"[Paso {self.paso_actual}] Después de disparar '{nombre_transicion}':")
                for lugar, peso in trans['outputs']:
                    print(f"  - Lugar '{lugar}': {self.lugares[lugar]} token(s)")
                
                paso_descripcion = f"Transición '{nombre_transicion}' disparada"
                if letra_actual:
                    paso_descripcion += f" por la letra '{letra_actual}'"
                
                visualizar_red(self, self.paso_actual, letra_actual, paso_descripcion)
            
            self.paso_actual += 1
            return True
    
    # Filtramos solo letras y las convertimos a mayúsculas
    letras = [c.upper() for c in cadena if c.isalpha()]
    print(f"\nProcesando cadena: {cadena}")
    print(f"Letras extraídas: {', '.join(letras)}")
    
    # Creamos la red
    red = RedPetri()
    
    # Mostrar estado inicial
    if visualizar:
        print("\n[Estado inicial de la red de Petri]")
        visualizar_red(red, 0, None, "Estado inicial")
    
    # Mapeo de letras a transiciones - CORREGIDO (ahora usa un sistema de estados)
    secuencia = [
        ('A', 'encontrar_A'),
        ('P', 'encontrar_P'),
        ('R', 'encontrar_R'),
        ('O', 'encontrar_O'),
        ('B', 'encontrar_B'),
        ('A', 'encontrar_A2'),
        ('D', 'encontrar_D'),
        ('O', 'encontrar_O2')
    ]
    
    indice_secuencia = 0
    
    # Procesamos cada letra - CORREGIDO (sigue el orden estricto de la secuencia)
    for i, letra in enumerate(letras):
        if visualizar:
            print(f"\n--- Procesando letra {i+1}: '{letra}' ---")
        
        if indice_secuencia < len(secuencia):
            letra_esperada, transicion = secuencia[indice_secuencia]
            
            if visualizar:
                print(f"Buscando: '{letra_esperada}' (transición: '{transicion}')")
                print(f"Letra actual: '{letra}'")
            
            if letra == letra_esperada:
                if visualizar:
                    print(f"¡Coincidencia! Disparando transición '{transicion}'")
                
                if red.disparar_transicion(transicion, letra, visualizar):
                    indice_secuencia += 1
                    if visualizar:
                        print(f"Avanzando a siguiente estado en la secuencia (índice: {indice_secuencia})")
            else:
                if visualizar:
                    print(f"Letra '{letra}' no coincide con '{letra_esperada}'. No se dispara transición.")
        else:
            if visualizar:
                print("Secuencia completa. Letras adicionales serán ignoradas.")
    
    # Disparamos la transición final si se completó la secuencia
    if indice_secuencia == len(secuencia):
        if visualizar:
            print("\n¡Secuencia completa! Disparando transición final 'completado'")
        red.disparar_transicion('completado', None, visualizar)
    
    # Verificamos si llegamos al estado final
    if visualizar:
        print("\n[Estado final de la red de Petri]")
        for lugar, tokens in red.lugares.items():
            print(f"  - Lugar '{lugar}': {tokens} token(s)")
        
        if red.lugares['aprobado'] > 0:
            print("\n¡ÉXITO! Se encontró la palabra 'aprobado' en la cadena.")
        else:
            print("\nNo se encontró la secuencia completa para 'aprobado'.")
    
    return "aprobado" if red.lugares['aprobado'] > 0 else None

# Variable para mantener en búcle el código o romperlo más tarde:
variable_para_parar_el_codigo = True

while variable_para_parar_el_codigo:
    entrada = input("Ingresa un valor alfanumérico: ").strip()
    if es_alfanumerico(entrada):
        print("Entrada válida:", entrada)
        
        # Preguntar si desea visualización paso a paso
        visualizar = input("¿Deseas ver el proceso paso a paso? (s/n): ").strip().lower() == 's'
        
        # Inicia el procesamiento de la red petri
        resultado = red_petri_aprobado(entrada, visualizar)

        if resultado:
            print("\nLa salida es: " + resultado)
            menu()
        else:
            print("\nError: No se pudo encontrar la palabra 'aprobado' en la cadena.")
            menu()
    else:
        print("Error: Solo se permiten letras y números (sin espacios ni símbolos o que falten números o letras).")
        menu()