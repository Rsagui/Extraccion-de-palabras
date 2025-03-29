import re
import unicodedata
from graphviz import Digraph
import os

# Configuración global
CARPETA_BASE = "grafos_ejecucion"
EJECUCION_ACTUAL = 1

def crear_carpeta_ejecucion():
    global EJECUCION_ACTUAL
    carpeta = f"{CARPETA_BASE}_{EJECUCION_ACTUAL}"
    os.makedirs(carpeta, exist_ok=True)
    EJECUCION_ACTUAL += 1
    return carpeta

def es_alfanumerico(texto):
    texto_normalizado = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    return bool(re.fullmatch(r'^(?=.*[A-Za-z])(?=.*[0-9])[A-Za-z0-9]+$', texto_normalizado))

def obtener_respuesta_visualizacion():
    while True:
        respuesta = input("¿Ver proceso paso a paso? (s/n): ").strip().lower()
        if respuesta in ('s', 'n'):
            return respuesta == 's'
        print("Error: Por favor ingrese solo 's' o 'n'")

def menu():
    global variable_para_parar_el_codigo
    while True:
        seguir_jugando = input("Presiona 1 si quieres seguir jugando o 0 para salir: ").strip()
        if seguir_jugando not in ('0', '1'):
            print("¡Solo puedes ingresar 1 o 0!")
        elif seguir_jugando == '1':
            print("¡Sigamos jugando pues!")
            break
        elif seguir_jugando == '0':
            variable_para_parar_el_codigo = False
            print("¡Hasta pronto!")
            break

def visualizar_red(red, paso_actual, letra_actual, paso_descripcion, carpeta_ejecucion):
    try:
        dot = Digraph(comment='Red de Petri')
        
        # Configuración para maximizar el uso del espacio
        dot.attr(
            rankdir='TB',  # Top to Bottom
            size='8.5,11!',  # Tamaño carta forzado (con ! para ignorar ajustes automáticos)
            margin='0.2',  # Margen mínimo
            dpi='300',
            nodesep='0.5',  # Separación horizontal entre nodos
            ranksep='0.7',  # Separación vertical entre niveles
            fontname='Arial',
            fontsize='16',
            bgcolor='white'
        )
        
        # Estilo de bordes y flechas más gruesos
        dot.attr('edge', 
                fontname='Arial', 
                fontsize='14', 
                arrowsize='1.2', 
                penwidth='2.0',
                color='#333333')
        
        # Lugares (círculos) con mayor tamaño
        for lugar, tokens in red.lugares.items():
            # Colores según estado
            if lugar == 'inicio':
                color_borde = '#1A5276'  # Azul oscuro
                color_relleno = '#D6EAF8' if tokens > 0 else '#EBF5FB'
            elif lugar == 'aprobado':
                color_borde = '#196F3D'  # Verde oscuro
                color_relleno = '#D5F5E3' if tokens > 0 else '#EAFAF1'
            else:
                color_borde = '#2E86C1' if tokens > 0 else '#AED6F1'
                color_relleno = '#AED6F1' if tokens > 0 else '#EBF5FB'
            
            # Tamaño según importancia - MUCHO MÁS GRANDE
            if lugar in ['inicio', 'aprobado']:
                tamano = '1.2'
            else:
                tamano = '1.0'
            
            # Etiqueta con información de tokens
            etiqueta = f"{lugar}\n({tokens} token{'s' if tokens != 1 else ''})"
            
            # Crear nodo
            dot.node(lugar, etiqueta,
                    shape='circle', 
                    width=tamano, 
                    height=tamano,
                    style='filled', 
                    fillcolor=color_relleno,
                    color=color_borde, 
                    penwidth='2.5',
                    fontname='Arial Bold', 
                    fontsize='16')
        
        # Transiciones (rectángulos) con mayor tamaño
        for transicion in red.transiciones:
            # Nombre más legible
            nombre_corto = transicion.split('_')[-1]
            
            # Colores según disponibilidad
            if red.transicion_disponible(transicion):
                color_borde = '#C0392B'  # Rojo oscuro
                color_relleno = '#F5B7B1'  # Rojo claro
                ancho_borde = '3.0'
            else:
                color_borde = '#922B21'  # Rojo más oscuro
                color_relleno = '#FADBD8'  # Rojo muy claro
                ancho_borde = '2.0'
            
            # Crear nodo
            dot.node(transicion, nombre_corto,
                    shape='rectangle', 
                    width='0.8', 
                    height='0.5',
                    style='filled,rounded', 
                    fillcolor=color_relleno,
                    color=color_borde, 
                    penwidth=ancho_borde,
                    fontname='Arial Bold', 
                    fontsize='16')
        
        # Conexiones con estilos mejorados
        for transicion, datos in red.transiciones.items():
            # Arcos de entrada (lugar -> transición)
            for lugar, peso in datos['inputs']:
                dot.edge(lugar, transicion, 
                        label=str(peso) if peso > 1 else "",
                        color='#2471A3', 
                        penwidth='2.0',
                        arrowhead='normal', 
                        arrowsize='1.2')
            
            # Arcos de salida (transición -> lugar)
            for lugar, peso in datos['outputs']:
                dot.edge(transicion, lugar, 
                        label=str(peso) if peso > 1 else "",
                        color='#C0392B', 
                        penwidth='2.0',
                        arrowhead='normal', 
                        arrowsize='1.2')
        
        # Título y leyenda mejorados
        if letra_actual:
            titulo = f"Paso {paso_actual}: {paso_descripcion}\nLetra procesada: '{letra_actual}'"
        else:
            titulo = f"Paso {paso_actual}: {paso_descripcion}"
            
        dot.attr(label=titulo, labelloc='t', fontsize='22', fontname='Arial Bold')
        
        # Añadir leyenda mejorada en la parte superior derecha
        with dot.subgraph(name='cluster_legend') as legend:
            legend.attr(
                label='Leyenda', 
                fontsize='18', 
                fontname='Arial Bold',
                style='filled,rounded', 
                fillcolor='#F8F9F9', 
                color='#5D6D7E',
                margin='10',
                rank='sink'  # Forzar a la parte inferior
            )
            
            # Nodos de leyenda más grandes
            legend.node('legend_token', 'Con token', 
                      shape='circle', 
                      style='filled', 
                      fillcolor='#AED6F1', 
                      color='#2E86C1',
                      width='0.8', 
                      height='0.8', 
                      fontsize='14')
            
            legend.node('legend_no_token', 'Sin token', 
                      shape='circle', 
                      style='filled', 
                      fillcolor='#EBF5FB', 
                      color='#AED6F1',
                      width='0.8', 
                      height='0.8', 
                      fontsize='14')
            
            legend.node('legend_trans_active', 'Transición\ndisponible', 
                      shape='rectangle', 
                      style='filled,rounded', 
                      fillcolor='#F5B7B1', 
                      color='#C0392B',
                      width='1.0', 
                      height='0.6', 
                      fontsize='14')
            
            legend.node('legend_trans_inactive', 'Transición\nno disponible', 
                      shape='rectangle', 
                      style='filled,rounded', 
                      fillcolor='#FADBD8', 
                      color='#922B21',
                      width='1.0', 
                      height='0.6', 
                      fontsize='14')
            
            # Organizar leyenda horizontalmente
            legend.attr(rank='same')
            legend.edge('legend_token', 'legend_no_token')
            legend.edge('legend_no_token', 'legend_trans_active')
            legend.edge('legend_trans_active', 'legend_trans_inactive')
            legend.edge_attr.update(style='invis')
        
        # Guardar imagen con mejor calidad y tamaño forzado
        filepath = os.path.join(carpeta_ejecucion, f"paso_{paso_actual:02d}")
        dot.render(filepath, format='png', cleanup=True)
        
        print(f"✓ Gráfico {paso_actual:02d} guardado en {carpeta_ejecucion}")
        return True
        
    except Exception as e:
        print(f"✗ Error al generar gráfico: {str(e)}")
        return False

class RedPetri:
    def __init__(self):
        self.lugares = {
            'inicio': 1, 'A': 0, 'P': 0, 'R': 0, 'O': 0, 
            'B': 0, 'A2': 0, 'D': 0, 'O2': 0, 'aprobado': 0
        }
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
        self.historial = []
        self.paso_actual = 0
    
    def transicion_disponible(self, nombre_transicion):
        trans = self.transiciones[nombre_transicion]
        return all(self.lugares[l] >= p for l, p in trans['inputs'])
    
    def disparar_transicion(self, nombre_transicion, letra_actual=None, visualizar=False, carpeta_ejecucion=None):
        if not self.transicion_disponible(nombre_transicion):
            return False
        
        trans = self.transiciones[nombre_transicion]
        
        if visualizar:
            print(f"\n[Paso {self.paso_actual}] Antes de disparar '{nombre_transicion}':")
            for lugar, peso in trans['inputs']:
                print(f"  - {lugar}: {self.lugares[lugar]} token(s)")
        
        for lugar, peso in trans['inputs']:
            self.lugares[lugar] -= peso
        for lugar, peso in trans['outputs']:
            self.lugares[lugar] += peso
        
        self.historial.append(nombre_transicion)
        
        if visualizar:
            print(f"[Paso {self.paso_actual}] Después de disparar '{nombre_transicion}':")
            for lugar, peso in trans['outputs']:
                print(f"  - {lugar}: {self.lugares[lugar]} token(s)")
            
            paso_descripcion = f"Transición '{nombre_transicion}' disparada"
            if letra_actual:
                paso_descripcion += f" por '{letra_actual}'"
            
            visualizar_red(self, self.paso_actual, letra_actual, paso_descripcion, carpeta_ejecucion)
        
        self.paso_actual += 1
        return True

def red_petri_aprobado(cadena, visualizar=False):
    carpeta_ejecucion = crear_carpeta_ejecucion() if visualizar else None
    
    letras = [c.upper() for c in cadena if c.isalpha()]
    print(f"\nProcesando: {cadena}")
    print(f"Letras: {', '.join(letras)}")
    
    red = RedPetri()
    
    if visualizar:
        print("\n[Estado inicial]")
        visualizar_red(red, 0, None, "Estado inicial", carpeta_ejecucion)
    
    secuencia = [
        ('A', 'encontrar_A'), ('P', 'encontrar_P'), ('R', 'encontrar_R'),
        ('O', 'encontrar_O'), ('B', 'encontrar_B'), ('A', 'encontrar_A2'),
        ('D', 'encontrar_D'), ('O', 'encontrar_O2')
    ]
    
    indice = 0
    for i, letra in enumerate(letras):
        if visualizar:
            print(f"\n--- Letra {i+1}: '{letra}' ---")
        
        if indice < len(secuencia):
            letra_esperada, trans = secuencia[indice]
            
            if visualizar:
                print(f"Buscando: '{letra_esperada}' (transición: '{trans}')")
            
            if letra == letra_esperada:
                if visualizar:
                    print(f"¡Coincidencia! Disparando '{trans}'")
                
                if red.disparar_transicion(trans, letra, visualizar, carpeta_ejecucion):
                    indice += 1
            else:
                if visualizar:
                    print(f"No coincide. Esperaba '{letra_esperada}'")
        else:
            if visualizar:
                print("Secuencia completa. Ignorando letras adicionales.")
    
    if indice == len(secuencia):
        if visualizar:
            print("\n¡Secuencia completa! Disparando 'completado'")
        red.disparar_transicion('completado', None, visualizar, carpeta_ejecucion)
    
    if visualizar:
        print("\n[Estado final]")
        for lugar, tokens in red.lugares.items():
            print(f"  - {lugar}: {tokens} token(s)")
        
        if red.lugares['aprobado'] > 0:
            print("\n¡ÉXITO! Se encontró 'aprobado'")
        else:
            print("\nNo se completó la secuencia")
    
    return "aprobado" if red.lugares['aprobado'] > 0 else None

# Ejecución principal
if __name__ == "__main__":
    variable_para_parar_el_codigo = True
    
    print("=== Simulador de Red de Petri para 'APROBADO' ===")
    print("Ingrese cadenas alfanuméricas que contengan las letras 'APROBADO' en orden")
    
    while variable_para_parar_el_codigo:
        entrada = input("\nIngresa un valor alfanumérico: ").strip()
        
        if es_alfanumerico(entrada):
            print("Entrada válida:", entrada)
            visualizar = obtener_respuesta_visualizacion()
            resultado = red_petri_aprobado(entrada, visualizar)
            
            if resultado:
                print("\nLa salida es:", resultado)
            else:
                print("\nNo se encontró 'aprobado'")
            
            menu()
        else:
            print("Error: Solo letras y números (sin espacios/símbolos)")
            menu()

