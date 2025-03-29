import re
import unicodedata

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

# Modelado de red de Petri para extraer "aprobado" (VERSIÓN CORREGIDA)
def red_petri_aprobado(cadena):
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
        
        def transicion_disponible(self, nombre_transicion):
            """Verifica si una transición puede dispararse"""
            trans = self.transiciones[nombre_transicion]
            return all(self.lugares[lugar] >= peso for lugar, peso in trans['inputs'])
        
        def disparar_transicion(self, nombre_transicion):
            """Ejecuta una transición si es posible"""
            if not self.transicion_disponible(nombre_transicion):
                return False
            
            trans = self.transiciones[nombre_transicion]
            
            # Consumir tokens de inputs
            for lugar, peso in trans['inputs']:
                self.lugares[lugar] -= peso
            
            # Producir tokens en outputs
            for lugar, peso in trans['outputs']:
                self.lugares[lugar] += peso
            
            self.historial.append(nombre_transicion)
            return True
    
    # Filtramos solo letras y las convertimos a mayúsculas
    letras = [c.upper() for c in cadena if c.isalpha()]
    
    # Creamos la red
    red = RedPetri()
    
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
    for letra in letras:
        if indice_secuencia < len(secuencia):
            letra_esperada, transicion = secuencia[indice_secuencia]
            if letra == letra_esperada:
                if red.disparar_transicion(transicion):
                    indice_secuencia += 1
    
    # Disparamos la transición final si se completó la secuencia
    if indice_secuencia == len(secuencia):
        red.disparar_transicion('completado')
    
    # Verificamos si llegamos al estado final
    return "aprobado" if red.lugares['aprobado'] > 0 else None

# Variable para mantener en búcle el código o romperlo más tarde:
variable_para_parar_el_codigo = True

while variable_para_parar_el_codigo:
    entrada = input("Ingresa un valor alfanumérico: ").strip()
    if es_alfanumerico(entrada):
        print("Entrada válida:", entrada)
        
        # Inicia el procesamiento de la red petri
        resultado = red_petri_aprobado(entrada)

        if resultado:
            print("La salida es: " + resultado)
            menu()
        else:
            print("Error: No se pudo encontrar la palabra 'aprobado' en la cadena.")
            menu()
    else:
        print("Error: Solo se permiten letras y números (sin espacios ni símbolos o que falten números o letras).")
        menu()