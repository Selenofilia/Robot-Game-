"""
================================================================================
                        ROBOT RACE QUIZ - VERSION 6.0
                 Juego de carreras de robots con quiz educativo
                    Compatible con Makey Makey + LEGO EV3
================================================================================

DESCRIPCION:
    Este programa implementa un juego educativo de carreras de robots donde 
    dos jugadores compiten respondiendo preguntas. Incluye un interludio de
    cuenta regresiva "3, 2, 1" antes de cada pregunta, seguido de 30 segundos
    donde ambos jugadores pueden intentar responder. El primero en responder
    correctamente gana el punto.

CARACTERISTICAS PRINCIPALES v6.0:
    - INTERLUDIO "3, 2, 1": Cuenta regresiva animada antes de cada pregunta
    - TIEMPO DE 30 SEGUNDOS: Ambos jugadores pueden responder durante este tiempo
    - RESPUESTA RAPIDA: El primer jugador en responder correctamente gana
    - RESPUESTA INCORRECTA: Si alguien responde mal, queda bloqueado esa ronda
    - TIEMPO AGOTADO: Si nadie responde, la pregunta se invalida
    - INTERFAZ UNICA: Una sola pantalla con la pregunta centrada
    - PREGUNTAS DESECHABLES: Cada pregunta solo se usa una vez
    - Barra de progreso visual estilo pista de carreras segmentada
    - Integracion con LEGO EV3 para robots fisicos
    - Compatible con Makey Makey para controles alternativos
    - Logos institucionales (Facultad de Matematicas e Ingeniotics)

FLUJO DEL JUEGO:
    1. INTERLUDIO: Cuenta regresiva "3, 2, 1" animada (3 segundos)
    2. PREGUNTA: Se muestra la pregunta y respuestas (30 segundos)
       - Ambos jugadores pueden intentar responder
       - El primero en responder correctamente gana el punto
       - Si alguien responde incorrectamente, queda bloqueado esa ronda
    3. RESULTADO: Se muestra el resultado y se pasa a la siguiente pregunta

REQUISITOS:
    pip install pygame pandas openpyxl requests

PARA EV3:
    pip install pybricks

CONTROLES:
    - RESPONDER (durante los 30 segundos):
        - Jugador 1: A=opcion1, S=opcion2, D=opcion3
        - Jugador 2: J=opcion1, K=opcion2, L=opcion3
    - Menu: Teclas 1, 2, 3 para seleccionar nivel
    - ESC: Salir al menu
    - ESPACIO: Reiniciar (en pantalla de fin de juego)

ESTRUCTURA DEL ARCHIVO EXCEL (preguntas.xlsx):
    Nivel | Pregunta | Respuesta Correcta | R1 | R2

AUTORES:
    Desarrollado para uso educativo
    Facultad de Matematicas | Ingeniotics

FECHA:
    2024
================================================================================
"""

# ==============================================================================
#                           IMPORTACION DE MODULOS
# ==============================================================================

import pygame                    # Motor de juegos principal para graficos y eventos
import pandas as pd              # Manejo de datos tabulares (lectura de Excel)
import random                    # Generacion de numeros aleatorios para mezclar preguntas
import math                      # Funciones matematicas para animaciones
import os                        # Operaciones del sistema de archivos
import time                      # Manejo de tiempo para el temporizador
import io                        # Manejo de streams de bytes para imagenes
from dataclasses import dataclass, field  # Decoradores para clases de datos
from typing import Optional, List         # Anotaciones de tipos
from enum import Enum                     # Enumeraciones para estados del juego

# Intentar importar requests para cargar imagenes desde URL
# Si no esta disponible, se usara un fallback
try:
    #import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("[AVISO] requests no instalado. Logos desde URL no estaran disponibles.")
    print("        Instalar con: pip install requests")

# ==============================================================================
#                    CONFIGURACION EV3 (LEGO MINDSTORMS)
# ==============================================================================
# Descomentar las siguientes lineas para usar con LEGO EV3 real
# La comunicacion se realiza via Bluetooth

# from pybricks.hubs import EV3Brick
# from pybricks.pupdevices import Motor
# from pybricks.parameters import Port
# 
# # Inicializacion del brick EV3 y motores
# ev3 = EV3Brick()
# motor_player1 = Motor(Port.A)  # Motor del jugador 1 en puerto A
# motor_player2 = Motor(Port.B)  # Motor del jugador 2 en puerto B
# 
# def move_robot(player: int, distance: int):
#     """
#     Mueve el robot EV3 una distancia determinada.
#     
#     Args:
#         player (int): Numero del jugador (1 o 2)
#         distance (int): Distancia a mover (en unidades del juego)
#     
#     El motor gira a 500 grados/segundo, convirtiendo la distancia
#     del juego a grados de rotacion del motor.
#     """
#     motor = motor_player1 if player == 1 else motor_player2
#     motor.run_angle(500, distance * 10)  # Convertir unidades a grados
#
# def celebrate_robot(player: int):
#     """
#     Hace que el robot ganador ejecute una animacion de celebracion.
#     
#     Args:
#         player (int): Numero del jugador ganador (1 o 2)
#     
#     El robot realiza 3 giros completos hacia adelante y atras.
#     """
#     motor = motor_player1 if player == 1 else motor_player2
#     for _ in range(3):
#         motor.run_angle(1000, 360)   # Giro hacia adelante
#         motor.run_angle(1000, -360)  # Giro hacia atras
# ==============================================================================


def move_robot(player: int, distance: int):
    """
    Funcion simulada para mover el robot (cuando no hay EV3 conectado).
    
    Esta funcion sirve como placeholder cuando no se tiene hardware EV3.
    Imprime un mensaje en consola indicando el movimiento que se realizaria.
    
    Args:
        player (int): Numero del jugador (1 o 2)
        distance (int): Distancia que avanzaria el robot
    
    Returns:
        None
    """
    print(f"[EV3 SIMULADO] Robot del Jugador {player} avanza {distance} unidades")


def celebrate_robot(player: int):
    """
    Funcion simulada para celebracion del robot (cuando no hay EV3 conectado).
    
    Esta funcion sirve como placeholder cuando no se tiene hardware EV3.
    Imprime un mensaje en consola indicando la celebracion.
    
    Args:
        player (int): Numero del jugador ganador (1 o 2)
    
    Returns:
        None
    """
    print(f"[EV3 SIMULADO] Robot del Jugador {player} celebra la victoria!")


# ==============================================================================
#                         INICIALIZACION DE PYGAME
# ==============================================================================

# Inicializar todos los modulos de Pygame
pygame.init()

# Inicializar especificamente el modulo de fuentes
pygame.font.init()
info = pygame.display.Info()


# ==============================================================================
#                      CONSTANTES DE CONFIGURACION
# ==============================================================================

# Dimensiones de la ventana del juego
SCREEN_WIDTH = info.current_w  # Ancho de la pantalla en pixeles
SCREEN_HEIGHT = info.current_h

# Velocidad de actualizacion del juego
FPS = 60  # Cuadros por segundo (frames per second)

# ==================== TIEMPOS DE CADA FASE ====================
# Duracion del interludio "3, 2, 1" (segundos por numero)
COUNTDOWN_DURATION = 1.0  # 1 segundo por cada numero (total 3 segundos)

# Tiempo limite para responder la pregunta (segundos)
QUESTION_TIME_LIMIT = 30

# Tiempo de pausa despues de responder para mostrar resultado (milisegundos)
RESULT_PAUSE_DURATION = 2500  # 2.5 segundos

# Nombres de los archivos locales de logos (deben estar en la misma carpeta)
LOGO_FAC_FILE = "LOGO_FAC.png"
LOGO_INGENIOTICS_FILE = "ingenio2.png"

# ==============================================================================
#                         PALETA DE COLORES
# ==============================================================================
# Definicion de colores en formato RGB (rojo, verde, azul)
# Los valores van de 0 a 255 para cada componente

COLORS = {
    # Colores de fondo
    'background': (20, 22, 35),       # Fondo principal oscuro
    'card': (30, 32, 50),             # Fondo de tarjetas/paneles
    'card_hover': (40, 42, 65),       # Fondo de tarjetas al pasar el mouse
    
    # Colores de texto
    'text_white': (248, 250, 252),    # Texto blanco principal
    'text_gray': (148, 163, 184),     # Texto gris secundario
    'text_muted': (100, 116, 139),    # Texto atenuado/sutil
    
    # Colores del Jugador 1 (Verde)
    'player1': (34, 197, 94),         # Verde principal
    'player1_light': (74, 222, 128),  # Verde claro
    'player1_dark': (22, 163, 74),    # Verde oscuro
    
    # Colores del Jugador 2 (Naranja)
    'player2': (249, 115, 22),        # Naranja principal
    'player2_light': (251, 146, 60),  # Naranja claro
    'player2_dark': (234, 88, 12),    # Naranja oscuro
    
    # Colores de acento y estado
    'accent': (250, 204, 21),         # Amarillo de acento
    'success': (34, 197, 94),         # Verde para exito/correcto
    'error': (239, 68, 68),           # Rojo para error/incorrecto
    'countdown': (147, 51, 234),      # Morado para cuenta regresiva
    'question': (59, 130, 246),       # Azul para fase de pregunta
    
    # Colores de interfaz
    'border': (51, 65, 85),           # Bordes de elementos
    'track_bg': (15, 23, 42),         # Fondo de la pista de carreras
    'track_segment': (30, 41, 59),    # Segmentos de la pista
    'finish': (250, 204, 21),         # Linea de meta (amarillo)
}


# ==============================================================================
#                      ENUMERACIONES Y CLASES DE DATOS
# ==============================================================================

class GamePhase(Enum):
    """
    Enumeracion que define las fases/estados posibles del juego.
    
    Attributes:
        MENU: Estado del menu principal donde se selecciona el nivel
        COUNTDOWN: Interludio con cuenta regresiva "3, 2, 1"
        QUESTION: Fase donde se muestra la pregunta (30 segundos para responder)
        RESULT_PAUSE: Pausa para mostrar resultado antes de siguiente pregunta
        FINISHED: Estado de fin de juego mostrando resultados
    """
    MENU = "menu"                     # Pantalla de menu principal
    COUNTDOWN = "countdown"           # Interludio "3, 2, 1"
    QUESTION = "question"             # Fase de pregunta (30 seg, todos pueden responder)
    RESULT_PAUSE = "result_pause"     # Pausa mostrando resultado
    FINISHED = "finished"             # Juego terminado


@dataclass
class Question:
    """
    Clase de datos que representa una pregunta del quiz.
    
    Utiliza el decorador @dataclass para generar automaticamente
    __init__, __repr__ y otros metodos especiales.
    
    Attributes:
        nivel (int): Nivel de dificultad de la pregunta (1, 2 o 3)
        pregunta (str): Texto de la pregunta a mostrar
        respuesta_correcta (str): La respuesta correcta
        r1 (str): Primera respuesta incorrecta
        r2 (str): Segunda respuesta incorrecta
    
    Note:
        Las tres opciones (respuesta_correcta, r1, r2) se mezclaran
        aleatoriamente al presentar la pregunta al jugador.
    """
    nivel: int                    # Nivel de dificultad (1=facil, 2=medio, 3=dificil)
    pregunta: str                 # Texto de la pregunta
    respuesta_correcta: str       # Respuesta correcta
    r1: str                       # Respuesta incorrecta 1
    r2: str                       # Respuesta incorrecta 2


@dataclass 
class PlayerState:
    """
    Clase de datos que mantiene el estado actual de un jugador.
    
    Almacena toda la informacion relevante sobre la posicion,
    puntuacion y estado de respuesta de cada jugador.
    
    Attributes:
        position (float): Posicion actual del robot en la pista (0-100)
        target_position (float): Posicion objetivo para animacion suave
        score (int): Puntuacion actual (numero de respuestas correctas)
        last_answer (Optional[str]): Resultado de ultima respuesta ("correct"/"incorrect")
        message (str): Mensaje a mostrar al jugador
        message_type (str): Tipo de mensaje ("info", "success", "error", "warning")
        animation_offset (float): Desplazamiento para animacion del robot
        blocked_this_round (bool): Si el jugador esta bloqueado esta ronda (respondio mal)
    """
    position: float = 0.0                           # Posicion en pista (0-100%)
    target_position: float = 0.0                    # Posicion destino para animacion
    score: int = 0                                  # Puntos acumulados
    last_answer: Optional[str] = None               # "correct" o "incorrect"
    message: str = ""                               # Mensaje de feedback
    message_type: str = "info"                      # Tipo de mensaje
    animation_offset: float = 0.0                   # Offset para animacion flotante
    blocked_this_round: bool = False                # Bloqueado por respuesta incorrecta


# ==============================================================================
#                      CLASE PRINCIPAL DEL JUEGO
# ==============================================================================

class RobotRaceGame:
    """
    Clase principal que controla toda la logica del juego Robot Race Quiz.
    
    Esta clase maneja:
    - Inicializacion de Pygame y recursos
    - Carga de preguntas desde Excel
    - Interludio "3, 2, 1" antes de cada pregunta
    - Sistema de respuesta rapida (30 segundos)
    - Logica del juego (turnos, puntuacion, tiempo)
    - Renderizado de graficos
    - Manejo de eventos de entrada
    - Integracion con EV3 (simulada o real)
    
    Attributes:
        screen: Superficie principal de Pygame para renderizado
        clock: Reloj de Pygame para control de FPS
        phase: Fase actual del juego (MENU, COUNTDOWN, QUESTION, etc.)
        level: Nivel de dificultad actual
        player1: Estado del jugador 1
        player2: Estado del jugador 2
        winner: Numero del jugador ganador (None si no hay)
        questions: Lista de todas las preguntas cargadas
        available_questions: Preguntas disponibles para la partida actual
        current_question: Pregunta actual
        current_options: Opciones de respuesta mezcladas
    """
    
    def __init__(self):
        """
        Constructor de la clase RobotRaceGame.
        
        Inicializa todos los componentes necesarios:
        - Ventana de Pygame
        - Fuentes tipograficas
        - Estados de jugadores
        - Carga de preguntas
        - Variables de tiempo y animacion
        - Carga de logos institucionales
        """
        # ==================== CONFIGURACION DE PANTALLA ====================
        # Crear ventana del juego con las dimensiones especificadas
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Establecer titulo de la ventana
        pygame.display.set_caption("Robot Race Quiz v6.0 - Interludio 3,2,1 + 30 segundos")
        
        # Crear reloj para controlar la velocidad del juego
        self.clock = pygame.time.Clock()
        
        # ==================== FUENTES TIPOGRAFICAS ====================
        # Diferentes tamanos de fuente para distintos elementos de UI
        self.font_title = pygame.font.Font(None, 56)       # Titulos grandes
        self.font_countdown = pygame.font.Font(None, 200)  # Numeros de cuenta regresiva
        self.font_large = pygame.font.Font(None, 48)       # Subtitulos grandes
        self.font_medium = pygame.font.Font(None, 32)      # Texto medio
        self.font_small = pygame.font.Font(None, 24)       # Texto pequeno
        self.font_tiny = pygame.font.Font(None, 18)        # Texto muy pequeno
        
        # ==================== ESTADO DEL JUEGO ====================
        self.phase = GamePhase.MENU    # Comenzar en el menu
        self.level = 1                 # Nivel por defecto
        self.player1 = PlayerState()   # Estado del jugador 1
        self.player2 = PlayerState()   # Estado del jugador 2
        self.winner = None             # Sin ganador inicialmente
        
        # ==================== PREGUNTAS ====================
        self.questions: List[Question] = []              # Todas las preguntas
        self.available_questions: List[Question] = []    # Preguntas disponibles
        self.current_question: Optional[Question] = None # Pregunta actual
        self.current_options: List[str] = []             # Opciones mezcladas
        self.questions_answered = 0                       # Contador de preguntas
        
        # ==================== SISTEMA DE INTERLUDIO ====================
        self.countdown_number = 3                  # Numero actual de cuenta regresiva
        self.countdown_start_time = 0             # Tiempo de inicio de cuenta regresiva
        
        # ==================== RESULTADO DE RONDA ====================
        self.round_winner: Optional[int] = None   # Quien gano esta ronda (1, 2 o None)
        self.last_answer_correct: Optional[bool] = None  # Si la ultima respuesta fue correcta
        self.result_pause_start = 0               # Tiempo inicio de pausa resultado
        
        # ==================== TEMPORIZADOR DE PREGUNTA ====================
        self.question_time_remaining = QUESTION_TIME_LIMIT
        self.question_start_time = 0
        
        # ==================== CONSTANTES DEL JUEGO ====================
        self.WINNING_POSITION = 100    # Posicion de meta (100%)
        self.POSITION_INCREMENT = 20   # Avance por respuesta correcta
        self.TOTAL_SEGMENTS = 5        # Numero de segmentos en la pista
        
        # ==================== ANIMACION ====================
        self.animation_time = 0        # Contador de tiempo para animaciones
        self.hover_level = None        # Nivel sobre el que esta el cursor
        
        # ==================== LOGOS ====================
        self.logo_fac = None           # Logo Facultad de Matematicas
        self.logo_ingeniotics = None   # Logo Ingeniotics
        
        # ==================== CARGAR RECURSOS ====================
        # Cargar preguntas desde archivo Excel
        self.load_questions_from_excel()
        
        # Cargar logos institucionales
        self.load_logos()
    
    # ==========================================================================
    #                        CARGA DE LOGOS
    # ==========================================================================
    
    def load_logos(self):
        """
        Carga los logos institucionales desde archivos locales en la computadora.
        Busca los archivos en la misma carpeta donde esta el script.
        """
        # Obtener la ruta de la carpeta donde esta este archivo .py
        base_path = os.path.dirname(os.path.abspath(__file__))
        
        # Construir las rutas completas a las imagenes
        path_fac = os.path.join(base_path, LOGO_FAC_FILE)
        path_ing = os.path.join(base_path, LOGO_INGENIOTICS_FILE)
        
        # --- CARGAR LOGO FACULTAD ---
        if os.path.exists(path_fac):
            try:
                print(f"[INFO] Cargando logo Facultad desde: {path_fac}")
                self.logo_fac = pygame.image.load(path_fac)
                # Redimensionar manteniendo aspecto (100x100)
                self.logo_fac = pygame.transform.scale(self.logo_fac, (150, 100))
                print("[OK] Logo Facultad cargado correctamente")
            except Exception as e:
                print(f"[ERROR] No se pudo cargar la imagen {LOGO_FAC_FILE}: {e}")
        else:
            print(f"[AVISO] No se encontro el archivo: {LOGO_FAC_FILE}")
            
        # --- CARGAR LOGO INGENIOTICS ---
        if os.path.exists(path_ing):
            try:
                print(f"[INFO] Cargando logo Ingeniotics desde: {path_ing}")
                self.logo_ingeniotics = pygame.image.load(path_ing)
                # Redimensionar (mas ancho porque es horizontal)
                self.logo_ingeniotics = pygame.transform.scale(self.logo_ingeniotics, (150, 50))
                print("[OK] Logo Ingeniotics cargado correctamente")
            except Exception as e:
                print(f"[ERROR] No se pudo cargar la imagen {LOGO_INGENIOTICS_FILE}: {e}")
        else:
            print(f"[AVISO] No se encontro el archivo: {LOGO_INGENIOTICS_FILE}")
    
    # ==========================================================================
    #                     CARGA DE PREGUNTAS
    # ==========================================================================
    
    def load_questions_from_excel(self):
        """
        Carga las preguntas del quiz desde un archivo Excel.
        
        Busca el archivo 'preguntas.xlsx' en multiples ubicaciones:
        1. Directorio actual
        2. Directorio del script
        3. Directorio de trabajo
        
        El archivo Excel debe tener la estructura:
        Nivel | Pregunta | Respuesta Correcta | R1 | R2
        
        Si no se encuentra el archivo o hay errores, carga preguntas
        por defecto para permitir que el juego funcione.
        
        Returns:
            None
        
        Raises:
            No lanza excepciones - maneja errores internamente
        """
        excel_file = "preguntasCompletasVirgilio.xlsx"
        
        # Lista de posibles ubicaciones del archivo
        possible_paths = [
            excel_file,                                         # Directorio actual
            os.path.join(os.path.dirname(__file__), excel_file), # Directorio del script
            os.path.join(os.getcwd(), excel_file),              # Directorio de trabajo
        ]
        
        # Buscar el archivo en las ubicaciones posibles
        file_found = None
        for path in possible_paths:
            if os.path.exists(path):
                file_found = path
                break
        
        if file_found:
            try:
                # Leer archivo Excel usando pandas
                df = pd.read_excel(file_found)
                
                # Verificar que existan las columnas requeridas
                required_columns = ['Nivel', 'Pregunta', 'Respuesta Correcta', 'R1', 'R2']
                missing = [col for col in required_columns if col not in df.columns]
                
                if missing:
                    print(f"[ERROR] Columnas faltantes en Excel: {missing}")
                    print(f"[INFO] Columnas encontradas: {list(df.columns)}")
                    self.load_default_questions()
                    return
                
                # Procesar cada fila del Excel
                for _, row in df.iterrows():
                    try:
                        # Crear objeto Question y anadirlo a la lista
                        self.questions.append(Question(
                            nivel=int(row['Nivel']),
                            pregunta=str(row['Pregunta']).strip(),
                            respuesta_correcta=str(row['Respuesta Correcta']).strip(),
                            r1=str(row['R1']).strip(),
                            r2=str(row['R2']).strip()
                        ))
                    except Exception as e:
                        print(f"[WARNING] Error procesando fila: {e}")
                        continue
                
                # Mostrar resumen de preguntas cargadas
                print(f"[OK] Cargadas {len(self.questions)} preguntas desde '{file_found}'")
                for nivel in [1, 2, 3]:
                    count = len([q for q in self.questions if q.nivel == nivel])
                    print(f"     Nivel {nivel}: {count} preguntas")
                    
            except Exception as e:
                print(f"[ERROR] Error leyendo archivo Excel: {e}")
                self.load_default_questions()
        else:
            print(f"[INFO] Archivo '{excel_file}' no encontrado en ninguna ubicacion")
            print("[INFO] Usando preguntas por defecto")
            self.load_default_questions()
    
    def load_default_questions(self):
        """
        Carga un conjunto de preguntas predeterminadas.
        
        Se utiliza como fallback cuando no se encuentra o no se puede
        leer el archivo Excel de preguntas.
        
        Las preguntas estan organizadas por nivel de dificultad:
        - Nivel 1: Preguntas basicas de matematicas y geometria
        - Nivel 2: Conocimiento general y operaciones intermedias
        - Nivel 3: Matematicas avanzadas y calculos complejos
        
        Returns:
            None
        """
        # Estructura: (nivel, pregunta, respuesta_correcta, r1, r2)
        default_data = [
            # ============ NIVEL 1 - FACIL ============
            (1, "Cual de estos numeros es par?", "18", "15", "21"),
            (1, "Que figura tiene tres lados?", "Triangulo", "Cuadrado", "Circulo"),
            (1, "Cual numero es mayor?", "54", "45", "44"),
            (1, "Que figura es redonda?", "Circulo", "Triangulo", "Cuadrado"),
            (1, "Que numero es impar?", "19", "20", "18"),
            (1, "Cuantos lados tiene un cuadrado?", "4", "3", "5"),
            (1, "Que figura tiene cuatro lados iguales?", "Cuadrado", "Rectangulo", "Pentagono"),
            (1, "Cual numero es menor?", "23", "32", "29"),
            (1, "Que figura tiene forma de pelota?", "Esfera", "Cubo", "Piramide"),
            (1, "Que numero esta antes del 50?", "49", "48", "51"),
            (1, "Cuanto es 5 + 3?", "8", "7", "9"),
            (1, "Cuanto es 10 - 4?", "6", "5", "7"),
            
            # ============ NIVEL 2 - MEDIO ============
            (2, "Que unidad se usa para medir el tiempo?", "Hora", "Metro", "Kilo"),
            (2, "Cuanto es 7 x 8?", "56", "54", "58"),
            (2, "Que planeta es el mas cercano al Sol?", "Mercurio", "Venus", "Marte"),
            (2, "Cuantos minutos tiene una hora?", "60", "50", "100"),
            (2, "Que fraccion es mayor: 1/2 o 1/4?", "1/2", "1/4", "Son iguales"),
            (2, "Cual es el resultado de 15 + 27?", "42", "41", "43"),
            (2, "Que animal es mamifero?", "Delfin", "Tiburon", "Pulpo"),
            (2, "Cuantos lados tiene un hexagono?", "6", "5", "8"),
            (2, "Cuanto es 9 x 6?", "54", "52", "56"),
            (2, "Cual es la capital de Francia?", "Paris", "Londres", "Madrid"),
            
            # ============ NIVEL 3 - DIFICIL ============
            (3, "Cual es la raiz cuadrada de 144?", "12", "14", "11"),
            (3, "Cuanto es el 25% de 200?", "50", "40", "25"),
            (3, "Que tipo de angulo mide exactamente 90 grados?", "Recto", "Agudo", "Obtuso"),
            (3, "Cual es el area de un cuadrado de lado 7?", "49", "28", "14"),
            (3, "Cuanto es 3 al cubo?", "27", "9", "81"),
            (3, "Que numero es primo?", "17", "15", "21"),
            (3, "Cual es el perimetro de un rectangulo de 5x3?", "16", "15", "8"),
            (3, "Cuanto es 0.5 + 0.75?", "1.25", "1.20", "1.30"),
            (3, "Cuanto es 2 elevado a la 5?", "32", "16", "64"),
            (3, "Cual es el MCD de 12 y 18?", "6", "3", "9"),
        ]
        
        # Crear objetos Question a partir de los datos
        for data in default_data:
            self.questions.append(Question(*data))
        
        print(f"[OK] Cargadas {len(self.questions)} preguntas por defecto")
    
    # ==========================================================================
    #                    GESTION DE PREGUNTAS
    # ==========================================================================
    
    def get_questions_by_level(self, level: int) -> List[Question]:
        """
        Filtra y retorna las preguntas de un nivel especifico.
        
        Args:
            level (int): Nivel de dificultad (1, 2 o 3)
        
        Returns:
            List[Question]: Lista de preguntas del nivel especificado
        """
        return [q for q in self.questions if q.nivel == level]
    
    def shuffle_options(self, question: Question) -> List[str]:
        """
        Mezcla aleatoriamente las opciones de respuesta de una pregunta.
        
        Toma la respuesta correcta y las dos incorrectas, las combina
        en una lista y las mezcla para que el orden sea aleatorio.
        
        Args:
            question (Question): Objeto pregunta con las opciones
        
        Returns:
            List[str]: Lista de 3 opciones en orden aleatorio
        """
        options = [question.respuesta_correcta, question.r1, question.r2]
        random.shuffle(options)
        return options
    
    def start_countdown_for_next_question(self):
        """
        Inicia la cuenta regresiva "3, 2, 1" para la siguiente pregunta.
        
        Resetea los estados de la ronda anterior y prepara la siguiente pregunta.
        Si no hay mas preguntas, termina el juego.
        
        Returns:
            None
        """
        # Resetear estados de la ronda
        self.round_winner = None
        self.last_answer_correct = None
        self.player1.last_answer = None
        self.player1.message = ""
        self.player1.blocked_this_round = False
        self.player2.last_answer = None
        self.player2.message = ""
        self.player2.blocked_this_round = False
        
        # Verificar si hay preguntas disponibles
        if not self.available_questions:
            print("[INFO] No hay mas preguntas disponibles")
            self.determine_winner()
            return
        
        # Seleccionar y remover una pregunta de la lista
        self.current_question = self.available_questions.pop(0)
        self.current_options = self.shuffle_options(self.current_question)
        
        # Incrementar contador
        self.questions_answered += 1
        
        # Iniciar cuenta regresiva
        self.phase = GamePhase.COUNTDOWN
        self.countdown_number = 3
        self.countdown_start_time = time.time()
        
        print(f"\n[PREGUNTA {self.questions_answered}] Iniciando cuenta regresiva...")
        print(f"[INFO] Pregunta: {self.current_question.pregunta}")
        print(f"[INFO] Respuesta correcta: {self.current_question.respuesta_correcta}")
    
    def start_question_phase(self):
        """
        Inicia la fase de pregunta donde ambos jugadores pueden responder.
        
        Se llama despues de que termina la cuenta regresiva "3, 2, 1".
        
        Returns:
            None
        """
        self.phase = GamePhase.QUESTION
        self.question_start_time = time.time()
        self.question_time_remaining = QUESTION_TIME_LIMIT
        
        print(f"[PREGUNTA] Ambos jugadores pueden responder! ({QUESTION_TIME_LIMIT} segundos)")
    
    # ==========================================================================
    #                     CONTROL DEL JUEGO
    # ==========================================================================
    
    def start_game(self, level: int):
        """
        Inicia una nueva partida con el nivel especificado.
        
        Realiza las siguientes acciones:
        1. Resetea los estados de ambos jugadores
        2. Obtiene y mezcla las preguntas del nivel
        3. Inicia la cuenta regresiva para la primera pregunta
        
        Args:
            level (int): Nivel de dificultad seleccionado (1, 2 o 3)
        
        Returns:
            None
        """
        self.level = level
        self.winner = None
        self.questions_answered = 0
        
        # Resetear estados de jugadores
        self.player1 = PlayerState()
        self.player2 = PlayerState()
        
        # Obtener preguntas del nivel y mezclarlas
        level_questions = self.get_questions_by_level(level)
        self.available_questions = random.sample(level_questions, len(level_questions))
        
        print(f"\n[JUEGO] Iniciando nivel {level} con {len(level_questions)} preguntas")
        print(f"[JUEGO] Flujo: Cuenta regresiva (3,2,1) -> Pregunta ({QUESTION_TIME_LIMIT}s)")
        
        # Iniciar cuenta regresiva para primera pregunta
        self.start_countdown_for_next_question()
    
    def answer_question(self, player: int, answer_index: int):
        """
        Procesa la respuesta de un jugador.
        
        Cualquier jugador puede responder durante los 30 segundos,
        pero si responde incorrectamente queda bloqueado esa ronda.
        El primero en responder correctamente gana el punto.
        
        Args:
            player (int): Numero del jugador (1 o 2)
            answer_index (int): Indice de la opcion seleccionada (0, 1, o 2)
        
        Returns:
            None
        """
        # Solo procesar en fase QUESTION
        if self.phase != GamePhase.QUESTION:
            return
        
        # Verificar si el jugador esta bloqueado
        player_state = self.player1 if player == 1 else self.player2
        if player_state.blocked_this_round:
            print(f"[JUEGO] Jugador {player} esta bloqueado esta ronda")
            return
        
        # Verificar que haya pregunta actual
        if not self.current_question:
            return
        
        # Verificar indice valido
        if answer_index >= len(self.current_options):
            return
        
        # Obtener respuesta seleccionada
        selected_answer = self.current_options[answer_index]
        
        # Verificar si es correcta
        is_correct = selected_answer == self.current_question.respuesta_correcta
        
        if is_correct:
            # ========== RESPUESTA CORRECTA ==========
            self.round_winner = player
            self.last_answer_correct = True
            
            # Actualizar posicion del robot
            player_state.target_position = min(
                player_state.target_position + self.POSITION_INCREMENT, 
                self.WINNING_POSITION
            )
            
            # Incrementar puntuacion
            player_state.score += 1
            
            # Mostrar mensaje de exito
            player_state.message = "CORRECTO! +1 punto"
            player_state.message_type = "success"
            player_state.last_answer = "correct"
            
            # Mover robot fisico EV3
            move_robot(player, self.POSITION_INCREMENT)
            
            print(f"[JUEGO] Jugador {player}: CORRECTO - Puntos: {player_state.score}")
            
            # Verificar si llego a la meta
            if player_state.target_position >= self.WINNING_POSITION:
                self.winner = player
                self.phase = GamePhase.FINISHED
                celebrate_robot(player)
                print(f"[JUEGO] Jugador {player} GANA!")
                return
            
            # Cambiar a pausa de resultado
            self.phase = GamePhase.RESULT_PAUSE
            self.result_pause_start = pygame.time.get_ticks()
            
        else:
            # ========== RESPUESTA INCORRECTA ==========
            # Bloquear al jugador esta ronda
            player_state.blocked_this_round = True
            player_state.message = f"Incorrecto! Bloqueado esta ronda"
            player_state.message_type = "error"
            player_state.last_answer = "incorrect"
            
            print(f"[JUEGO] Jugador {player}: INCORRECTO - Bloqueado esta ronda")
            
            # Verificar si ambos jugadores estan bloqueados
            if self.player1.blocked_this_round and self.player2.blocked_this_round:
                # Ambos fallaron, mostrar respuesta correcta y pasar a siguiente
                self.last_answer_correct = False
                self.round_winner = None
                self.phase = GamePhase.RESULT_PAUSE
                self.result_pause_start = pygame.time.get_ticks()
                print("[JUEGO] Ambos jugadores fallaron - Siguiente pregunta")
    
    def handle_timeout(self):
        """
        Maneja el caso cuando se acaba el tiempo para responder.
        
        Si nadie responde en 30 segundos, la pregunta es invalidada
        y se pasa a la siguiente.
        
        Returns:
            None
        """
        print("[JUEGO] Tiempo agotado - Pregunta invalidada!")
        
        # Marcar como timeout
        self.round_winner = None
        self.last_answer_correct = None  # None indica timeout
        
        # Mensajes para ambos jugadores
        self.player1.message = "Tiempo agotado!"
        self.player1.message_type = "warning"
        self.player2.message = "Tiempo agotado!"
        self.player2.message_type = "warning"
        
        # Cambiar a pausa de resultado
        self.phase = GamePhase.RESULT_PAUSE
        self.result_pause_start = pygame.time.get_ticks()
    
    def determine_winner(self):
        """
        Determina el ganador cuando se acaban las preguntas.
        
        Compara las puntuaciones de ambos jugadores y establece:
        - winner = 1 si gana el jugador 1
        - winner = 2 si gana el jugador 2
        - winner = 0 si hay empate
        
        Tambien activa la celebracion del robot ganador (si hay uno).
        
        Returns:
            None
        """
        self.phase = GamePhase.FINISHED
        
        if self.player1.score > self.player2.score:
            # Jugador 1 gana
            self.winner = 1
            celebrate_robot(1)
            print(f"[JUEGO] Jugador 1 GANA! ({self.player1.score} vs {self.player2.score})")
        elif self.player2.score > self.player1.score:
            # Jugador 2 gana
            self.winner = 2
            celebrate_robot(2)
            print(f"[JUEGO] Jugador 2 GANA! ({self.player2.score} vs {self.player1.score})")
        else:
            # Empate
            self.winner = 0
            print(f"[JUEGO] EMPATE! ({self.player1.score} = {self.player2.score})")
    
    def reset_game(self):
        """
        Reinicia el juego al estado inicial (menu).
        
        Limpia todos los estados de jugadores, preguntas y
        temporizadores para permitir una nueva partida.
        
        Returns:
            None
        """
        self.phase = GamePhase.MENU
        self.winner = None
        self.player1 = PlayerState()
        self.player2 = PlayerState()
        self.available_questions = []
        self.current_question = None
        self.current_options = []
        self.questions_answered = 0
        self.countdown_number = 3
        self.question_time_remaining = QUESTION_TIME_LIMIT
        
        print("[JUEGO] Juego reiniciado - Volviendo al menu")
    
    # ==========================================================================
    #                       ACTUALIZACION DEL JUEGO
    # ==========================================================================
    
    def update(self):
        """
        Actualiza el estado del juego en cada frame.
        
        Esta funcion se llama 60 veces por segundo y maneja:
        1. Actualizacion del contador de animacion
        2. Manejo de la cuenta regresiva "3, 2, 1"
        3. Transicion de cuenta regresiva a pregunta
        4. Actualizacion del temporizador de pregunta (30 segundos)
        5. Manejo de pausas de resultado
        6. Animacion suave de posiciones de robots
        7. Calculo de offsets para animaciones flotantes
        
        Returns:
            None
        """
        # Incrementar contador de animacion
        self.animation_time += 1
        
        # ========== MANEJAR FASE DE CUENTA REGRESIVA ==========
        if self.phase == GamePhase.COUNTDOWN:
            elapsed = time.time() - self.countdown_start_time
            
            # Calcular que numero mostrar (3, 2, 1)
            if elapsed < COUNTDOWN_DURATION:
                self.countdown_number = 3
            elif elapsed < COUNTDOWN_DURATION * 2:
                self.countdown_number = 2
            elif elapsed < COUNTDOWN_DURATION * 3:
                self.countdown_number = 1
            else:
                # Termino la cuenta regresiva, iniciar fase de pregunta
                self.start_question_phase()
        
        # ========== MANEJAR FASE DE PREGUNTA ==========
        if self.phase == GamePhase.QUESTION:
            elapsed = time.time() - self.question_start_time
            self.question_time_remaining = max(0, QUESTION_TIME_LIMIT - int(elapsed))
            
            # Verificar si se acabo el tiempo
            if self.question_time_remaining <= 0:
                self.handle_timeout()
        
        # ========== MANEJAR PAUSA DE RESULTADO ==========
        if self.phase == GamePhase.RESULT_PAUSE:
            elapsed = pygame.time.get_ticks() - self.result_pause_start
            if elapsed >= RESULT_PAUSE_DURATION:
                # Termino la pausa, siguiente pregunta
                self.start_countdown_for_next_question()
        
        # ========== ANIMAR POSICIONES DE ROBOTS ==========
        for player_state in [self.player1, self.player2]:
            # Mover suavemente hacia la posicion objetivo
            if player_state.position < player_state.target_position:
                player_state.position += 2  # Velocidad de animacion
                # No sobrepasar el objetivo
                if player_state.position > player_state.target_position:
                    player_state.position = player_state.target_position
            
            # Calcular offset de animacion flotante (movimiento senoidal)
            player_state.animation_offset = math.sin(self.animation_time * 0.1) * 3
    
    # ==========================================================================
    #                       MANEJO DE EVENTOS
    # ==========================================================================
  
    def handle_events(self):
        """
        Procesa todos los eventos de entrada del usuario.
        
        Maneja:
        - Evento de cierre de ventana
        - Teclas del menu (1, 2, 3 para seleccionar nivel)
        - Teclas de respuesta durante fase QUESTION
        - Tecla ESC para volver al menu
        - Tecla ESPACIO para reiniciar
        
        Returns:
            bool: True para continuar el juego, False para salir
        """
        for event in pygame.event.get():
            # Cierre con la "X" de la ventana
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                
                # 1. Gestión de la tecla ESC (Dual)
                if event.key == pygame.K_ESCAPE:
                    if self.phase == GamePhase.MENU:
                        return False  # Cierra el juego
                    else:
                        self.reset_game() # Vuelve al menú
                
                # 2. Teclas solo en el MENU
                if self.phase == GamePhase.MENU:
                    if event.key == pygame.K_1:
                        self.start_game(1)
                    elif event.key == pygame.K_2:
                        self.start_game(2)
                    elif event.key == pygame.K_3:
                        self.start_game(3)
                
                # 3. Teclas solo durante la PREGUNTA
                elif self.phase == GamePhase.QUESTION:
                    # Controles Jugador 1
                    if event.key == pygame.K_a: self.answer_question(1, 0)
                    elif event.key == pygame.K_s: self.answer_question(1, 1)
                    elif event.key == pygame.K_d: self.answer_question(1, 2)
                    
                    # Controles Jugador 2
                    elif event.key == pygame.K_j: self.answer_question(2, 0)
                    elif event.key == pygame.K_k: self.answer_question(2, 1)
                    elif event.key == pygame.K_l: self.answer_question(2, 2)
                
                # 4. Teclas en FIN DE JUEGO
                elif self.phase == GamePhase.FINISHED:
                    # ESPACIO: Jugar de nuevo / Volver al menú
                    if event.key == pygame.K_SPACE:
                        print("[JUEGO] Reiniciando al menú...")
                        self.reset_game()  # Esto cambia la fase a MENU y limpia puntos
        
        return True
    
    # ==========================================================================
    #                    FUNCIONES DE DIBUJO (UTILIDADES)
    # ==========================================================================
    
    def draw_rounded_rect(self, surface, color, rect, radius, border=0, border_color=None):
        """
        Dibuja un rectangulo con esquinas redondeadas.
        
        Args:
            surface: Superficie de Pygame donde dibujar
            color: Color de relleno (RGB tuple)
            rect: Rectangulo a dibujar (pygame.Rect o tuple)
            radius: Radio de las esquinas en pixeles
            border: Grosor del borde (0 = sin borde)
            border_color: Color del borde (RGB tuple)
        
        Returns:
            None
        """
        pygame.draw.rect(surface, color, rect, border_radius=radius)
        if border > 0 and border_color:
            pygame.draw.rect(surface, border_color, rect, border, border_radius=radius)
    
    def draw_robot(self, x, y, size, color, offset=0):
        """
        Dibuja un robot animado en la posicion especificada.
        
        El robot tiene:
        - Cuerpo cuadrado con esquinas redondeadas
        - Dos ojos con pupilas animadas
        - Una boca rectangular
        - Una antena con luz
        
        Args:
            x (int): Posicion X del centro del robot
            y (int): Posicion Y del centro del robot
            size (int): Tamano del robot en pixeles
            color: Color principal del robot (RGB tuple)
            offset (int): Desplazamiento vertical para animacion
        
        Returns:
            None
        """
        # Aplicar offset de animacion
        y += offset
        
        # ========== CUERPO ==========
        body = pygame.Rect(x - size//2, y - size//2, size, size)
        self.draw_rounded_rect(self.screen, color, body, size//4)
        
        # Borde del cuerpo
        pygame.draw.rect(self.screen, COLORS['text_white'], body, 2, border_radius=size//4)
        
        # ========== OJOS ==========
        eye_size = size // 5
        eye_y = y - size//6
        
        # Fondo de los ojos (circulos oscuros)
        pygame.draw.circle(self.screen, COLORS['background'], 
                          (x - size//4, int(eye_y)), eye_size)
        pygame.draw.circle(self.screen, COLORS['background'], 
                          (x + size//4, int(eye_y)), eye_size)
        
        # Pupilas animadas (se mueven de lado a lado)
        pupil_offset = math.sin(self.animation_time * 0.05) * 2
        pygame.draw.circle(self.screen, COLORS['text_white'], 
                          (int(x - size//4 + pupil_offset), int(eye_y)), eye_size//2)
        pygame.draw.circle(self.screen, COLORS['text_white'], 
                          (int(x + size//4 + pupil_offset), int(eye_y)), eye_size//2)
        
        # ========== BOCA ==========
        mouth_rect = pygame.Rect(x - size//3, y + size//6, size//1.5, size//6)
        pygame.draw.rect(self.screen, COLORS['background'], mouth_rect, border_radius=3)
        
        # ========== ANTENA ==========
        # Linea de la antena
        pygame.draw.line(self.screen, color, 
                        (x, y - size//2), 
                        (x, y - size//2 - size//4), 3)
        # Luz de la antena (circulo amarillo)
        pygame.draw.circle(self.screen, COLORS['accent'], 
                          (x, int(y - size//2 - size//4)), 5)
    
    # ==========================================================================
    #                         DIBUJAR MENU
    # ==========================================================================
    
    def draw_menu(self):
        """
        Dibuja la pantalla del menu principal.
        
        Incluye:
        - Logos institucionales (Facultad de Matematicas e Ingeniotics)
        - Titulo del juego
        - Subtitulo descriptivo
        - Robots decorativos animados
        - Panel de controles con sistema de respuesta rapida
        - Botones de seleccion de nivel con efectos hover
        - Texto de compatibilidad
        
        Returns:
            None
        """
        # Limpiar pantalla con color de fondo
        self.screen.fill(COLORS['background'])
        
        # ========== LOGOS INSTITUCIONALES ==========
        # Logo Facultad de Matematicas (esquina superior izquierda)
        if self.logo_fac:
            self.screen.blit(self.logo_fac, (20, 10))
        
        # Logo Ingeniotics (esquina superior derecha)
        if self.logo_ingeniotics:
            self.screen.blit(self.logo_ingeniotics, (SCREEN_WIDTH - 170, 25))
        
        # ========== TITULO ==========
        title_text = "ROBOT RACE QUIZ"
        title = self.font_title.render(title_text, True, COLORS['text_white'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)
        
        # ========== SUBTITULO ==========
        subtitle = self.font_small.render(
            "Desarrollado por Octavo Semestre Matemáticas Computacional", 
            True, COLORS['accent']
        )
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 120))
        self.screen.blit(subtitle, subtitle_rect)
        
        # ========== ROBOTS DECORATIVOS ANIMADOS ==========
        # Robot del jugador 1 (izquierda)
        self.draw_robot(150, 200, 70, COLORS['player1'], self.player1.animation_offset)
        
        # Robot del jugador 2 (derecha) - con animacion inversa
        self.draw_robot(SCREEN_WIDTH - 150, 200, 70, COLORS['player2'], 
                       -math.sin(self.animation_time * 0.1) * 3)
        
        # ========== PANEL DE INSTRUCCIONES ==========
        instr_rect = pygame.Rect(SCREEN_WIDTH // 2 - 380, 160, 760, 100)
        self.draw_rounded_rect(self.screen, COLORS['card'], instr_rect, 12, 2, COLORS['question'])
        
        # Titulo del panel
        flow_title = self.font_medium.render("FLUJO DEL JUEGO", True, COLORS['question'])
        flow_title_rect = flow_title.get_rect(center=(SCREEN_WIDTH // 2, 180))
        self.screen.blit(flow_title, flow_title_rect)
        
        # Explicacion del flujo
        flow1 = self.font_tiny.render(
            "1. INTERLUDIO: Cuenta regresiva 3, 2, 1...", 
            True, COLORS['text_gray']
        )
        flow2 = self.font_tiny.render(
            "2. PREGUNTA: 30 segundos para responder (ambos jugadores pueden intentar)", 
            True, COLORS['text_gray']
        )
        flow3 = self.font_tiny.render(
            "3. El primero en responder CORRECTAMENTE gana el punto", 
            True, COLORS['text_gray']
        )
        self.screen.blit(flow1, (SCREEN_WIDTH // 2 - 360, 200))
        self.screen.blit(flow2, (SCREEN_WIDTH // 2 - 360, 218))
        self.screen.blit(flow3, (SCREEN_WIDTH // 2 - 360, 236))
        
        # ========== CONTROLES ==========
        ctrl_rect = pygame.Rect(SCREEN_WIDTH // 2 - 380, 270, 760, 50)
        self.draw_rounded_rect(self.screen, COLORS['card'], ctrl_rect, 8, 1, COLORS['border'])
        
        ctrl_text1 = self.font_tiny.render("J1 (Verde): A=op1, S=op2, D=op3", True, COLORS['player1'])
        ctrl_text2 = self.font_tiny.render("J2 (Naranja): J=op1, K=op2, L=op3", True, COLORS['player2'])
        self.screen.blit(ctrl_text1, (SCREEN_WIDTH // 2 - 360, 282))
        self.screen.blit(ctrl_text2, (SCREEN_WIDTH // 2 + 20, 282))
        
        # ========== BOTONES DE NIVEL ==========
        levels = [
            ("1", "Facil", "Preguntas basicas de matematicas", COLORS['player1']),
            ("2", "Medio", "Conocimiento general y operaciones", COLORS['accent']),
            ("3", "Dificil", "Matematicas avanzadas", COLORS['player2']),
        ]
        
        y_start = 340
        for i, (num, name, desc, color) in enumerate(levels):
            btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 220, y_start + i * 95, 440, 80)
            
            # Detectar hover del mouse
            mouse_pos = pygame.mouse.get_pos()
            is_hover = btn_rect.collidepoint(mouse_pos)
            
            # Colores segun estado hover
            bg_color = color if is_hover else COLORS['card']
            text_color = COLORS['background'] if is_hover else COLORS['text_white']
            desc_color = COLORS['background'] if is_hover else COLORS['text_gray']
            
            # Dibujar boton
            self.draw_rounded_rect(self.screen, bg_color, btn_rect, 12, 2, color)
            
            # Texto del nivel
            level_text = self.font_medium.render(f"Nivel {num}: {name}", True, text_color)
            self.screen.blit(level_text, (btn_rect.x + 20, btn_rect.y + 15))
            
            # Descripcion
            desc_text = self.font_tiny.render(desc, True, desc_color)
            self.screen.blit(desc_text, (btn_rect.x + 20, btn_rect.y + 48))
            
            # Indicador de tecla
            key_text = self.font_small.render(f"Presiona {num}", True, text_color)
            key_rect = key_text.get_rect(right=btn_rect.right - 20, centery=btn_rect.centery)
            self.screen.blit(key_text, key_rect)
        
        # ========== TEXTO DE COMPATIBILIDAD ==========
        comp_text = self.font_tiny.render(
            "Compatible con: Makey Makey | LEGO EV3 | Teclado estandar", 
            True, COLORS['text_muted']
        )
        comp_rect = comp_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
        self.screen.blit(comp_text, comp_rect)
        
        # Creditos
        credit_text = self.font_tiny.render(
            "Facultad de Matematicas | Ingeniotics", 
            True, COLORS['text_muted']
        )
        credit_rect = credit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20))
        self.screen.blit(credit_text, credit_rect)
    
    # ==========================================================================
    #                   DIBUJAR PISTA DE CARRERAS
    # ==========================================================================
    
    def draw_race_track(self):
        """
        Dibuja la pista de carreras con barras de progreso segmentadas.
        
        La pista incluye:
        - Titulo "PISTA DE CARRERA"
        - Dos carriles horizontales con segmentos
        - Robots animados en posicion del porcentaje
        - Porcentaje de avance para cada jugador
        - Linea de meta amarilla con texto "META"
        
        Returns:
            None
        """
        # ========== TITULO DE PISTA ==========
        track_title = self.font_medium.render("PISTA DE CARRERA", True, COLORS['text_white'])
        track_title_rect = track_title.get_rect(center=(SCREEN_WIDTH // 2, 85))
        self.screen.blit(track_title, track_title_rect)
        
        # ========== CONFIGURACION DE PISTA ==========
        track_x = 80                              # Posicion X inicial
        track_width = SCREEN_WIDTH - 200          # Ancho total de pista
        track_height = 40                         # Alto de cada carril
        segment_count = self.TOTAL_SEGMENTS       # Numero de segmentos
        segment_gap = 3                           # Espacio entre segmentos
         
        # Posiciones Y de los carriles
        track_y_1 = 115  # Carril del jugador 1
        track_y_2 = 175  # Carril del jugador 2
        
        # ========== DIBUJAR CARRIL JUGADOR 1 ==========
        self.draw_player_track(
            track_x, track_y_1, track_width, track_height,
            segment_count, segment_gap,
            self.player1, 1, COLORS['player1']
        )
        
        # ========== DIBUJAR CARRIL JUGADOR 2 ==========
        self.draw_player_track(
            track_x, track_y_2, track_width, track_height,
            segment_count, segment_gap,
            self.player2, 2, COLORS['player2']
        )
        
        # ========== LINEA DE META ==========
        finish_x = track_x + track_width + 20
        
        # Rectangulo de meta
        meta_rect = pygame.Rect(finish_x, track_y_1 - 10, 12, track_y_2 + track_height - track_y_1 + 20)
        pygame.draw.rect(self.screen, COLORS['finish'], meta_rect, border_radius=4)
        
        # Texto "META"
        meta_text = self.font_medium.render("META", True, COLORS['finish'])
        meta_text_rect = meta_text.get_rect(left=finish_x + 20, centery=(track_y_1 + track_y_2 + track_height) // 2)
        self.screen.blit(meta_text, meta_text_rect)
    
    def draw_player_track(self, x, y, width, height, segments, gap, player_state, player_num, color):
        """
        Dibuja el carril de progreso de un jugador con segmentos.
        
        Args:
            x (int): Posicion X inicial del carril
            y (int): Posicion Y del carril
            width (int): Ancho total del carril
            height (int): Alto del carril
            segments (int): Numero de segmentos
            gap (int): Espacio entre segmentos
            player_state (PlayerState): Estado del jugador
            player_num (int): Numero del jugador (1 o 2)
            color: Color del jugador
        
        Returns:
            None
        """
        # ========== ETIQUETA DE JUGADOR ==========
        label_text = self.font_small.render(f"Jugador {player_num}", True, color)
        self.screen.blit(label_text, (x - 5, y - 22))
        
        # ========== FONDO DEL CARRIL ==========
        track_rect = pygame.Rect(x, y, width, height)
        self.draw_rounded_rect(self.screen, COLORS['track_bg'], track_rect, height // 2, 2, COLORS['border'])
        
        # ========== CALCULAR SEGMENTOS ==========
        segment_width = (width - gap * (segments + 1)) / segments
        progress_segments = int((player_state.position / 100) * segments)
        
        # ========== DIBUJAR SEGMENTOS ==========
        for i in range(segments):
            seg_x = x + gap + i * (segment_width + gap)
            seg_rect = pygame.Rect(seg_x, y + 4, segment_width, height - 8)
            
            # Color del segmento (activo o inactivo)
            if i < progress_segments:
                seg_color = color
            else:
                seg_color = COLORS['track_segment']
            
            pygame.draw.rect(self.screen, seg_color, seg_rect, border_radius=4)
        
        # ========== ROBOT EN LA PISTA ==========
        # Calcular posicion X del robot segun progreso
        robot_progress_x = x + 30 + (width - 60) * (player_state.position / 100)
        robot_y = y + height // 2
        
        # Dibujar robot pequeno
        self.draw_robot(int(robot_progress_x), robot_y, 30, color, int(player_state.animation_offset * 0.5))
        
        # ========== PORCENTAJE ==========
        percent_text = self.font_small.render(f"{int(player_state.position)}%", True, COLORS['text_white'])
        percent_rect = percent_text.get_rect(left=x + width + 10, centery=y + height // 2)
        self.screen.blit(percent_text, percent_rect)
    
    # ==========================================================================
    #                   DIBUJAR INTERFAZ UNICA DE JUEGO
    # ==========================================================================
    
    def draw_game(self):
        """
        Dibuja la pantalla principal del juego con interfaz unica.
        
        Esta es la interfaz principal que muestra:
        - Header con titulo, nivel y puntuaciones
        - Pista de carreras con progreso
        - Panel central con la pregunta
        - Opciones de respuesta centradas
        - Estado actual de la fase
        
        Returns:
            None
        """
        # Limpiar pantalla
        self.screen.fill(COLORS['background'])
        
        # ========== HEADER ==========
        self.draw_header()
        
        # ========== PISTA DE CARRERAS ==========
        self.draw_race_track()
        
        # ========== CONTENIDO SEGUN FASE ==========
        if self.phase == GamePhase.COUNTDOWN:
            self.draw_countdown_phase()
        elif self.phase == GamePhase.QUESTION:
            self.draw_question_phase()
        elif self.phase == GamePhase.RESULT_PAUSE:
            self.draw_result_phase()
        
        # ========== FOOTER CON CONTROLES ==========
        self.draw_footer()
    
    def draw_header(self):
        """
        Dibuja el header del juego con titulo, nivel y puntuaciones.
        
        Returns:
            None
        """
        # Fondo del header
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 60)
        self.draw_rounded_rect(self.screen, COLORS['card'], header_rect, 0)
        pygame.draw.line(self.screen, COLORS['border'], (0, 60), (SCREEN_WIDTH, 60), 2)
        
        # Titulo
        title = self.font_medium.render("ROBOT RACE QUIZ", True, COLORS['text_white'])
        self.screen.blit(title, (20, 18))
        
        # Badge de nivel
        level_rect = pygame.Rect(200, 15, 80, 30)
        self.draw_rounded_rect(self.screen, COLORS['accent'], level_rect, 8)
        level_text = self.font_tiny.render(f"Nivel {self.level}", True, COLORS['background'])
        level_text_rect = level_text.get_rect(center=level_rect.center)
        self.screen.blit(level_text, level_text_rect)
        
        # Puntuaciones
        p1_score = self.font_small.render(f"J1: {self.player1.score}", True, COLORS['player1'])
        p2_score = self.font_small.render(f"J2: {self.player2.score}", True, COLORS['player2'])
        self.screen.blit(p1_score, (SCREEN_WIDTH // 2 - 100, 18))
        self.screen.blit(p2_score, (SCREEN_WIDTH // 2 + 50, 18))
        
        # Numero de pregunta
        q_text = self.font_tiny.render(f"Pregunta {self.questions_answered}", True, COLORS['text_gray'])
        q_rect = q_text.get_rect(right=SCREEN_WIDTH - 120, centery=30)
        self.screen.blit(q_text, q_rect)
        
        # Boton de salir
        exit_text = self.font_tiny.render("ESC: Salir", True, COLORS['text_muted'])
        self.screen.blit(exit_text, (SCREEN_WIDTH - 80, 22))
    
    def draw_footer(self):
        """
        Dibuja el footer con informacion de controles.
        
        Returns:
            None
        """
        footer_rect = pygame.Rect(40, SCREEN_HEIGHT - 45, SCREEN_WIDTH - 80, 35)
        self.draw_rounded_rect(self.screen, COLORS['card'], footer_rect, 8, 1, COLORS['border'])
        
        if self.phase == GamePhase.COUNTDOWN:
            text = "PREPARATE - La pregunta aparecera en unos segundos..."
        elif self.phase == GamePhase.QUESTION:
            text = "J1: A/S/D  |  J2: J/K/L  |  El primero en responder correctamente gana!"
        else:
            text = "Esperando..."
        
        ctrl_text = self.font_tiny.render(text, True, COLORS['text_muted'])
        ctrl_rect = ctrl_text.get_rect(center=footer_rect.center)
        self.screen.blit(ctrl_text, ctrl_rect)
    
    def draw_countdown_phase(self):
        """
        Dibuja la fase de cuenta regresiva "3, 2, 1".
        
        Muestra:
        - Numero grande animado (3, 2, 1)
        - Efectos visuales de pulso
        - La pregunta que viene (difuminada/preview)
        
        Returns:
            None
        """
        # ========== NUMERO DE CUENTA REGRESIVA ==========
        # Animacion de escala/pulso
        pulse = 1.0 + math.sin(self.animation_time * 0.3) * 0.1
        
        # Panel central para el numero
        center_y = 400
        
        # Fondo circular animado
        radius = int(100 * pulse)
        pygame.draw.circle(self.screen, COLORS['countdown'], 
                          (SCREEN_WIDTH // 2, center_y), radius)
        pygame.draw.circle(self.screen, COLORS['text_white'], 
                          (SCREEN_WIDTH // 2, center_y), radius, 4)
        
        # Numero
        number_text = self.font_countdown.render(str(self.countdown_number), True, COLORS['text_white'])
        number_rect = number_text.get_rect(center=(SCREEN_WIDTH // 2, center_y))
        self.screen.blit(number_text, number_rect)
        
        # ========== MENSAJE PREPARATE ==========
        prep_text = self.font_large.render("PREPARATE!", True, COLORS['accent'])
        prep_rect = prep_text.get_rect(center=(SCREEN_WIDTH // 2, 270))
        self.screen.blit(prep_text, prep_rect)
        
        # ========== PREVIEW DE LA PREGUNTA (difuminada) ==========
        if self.current_question:
            # Panel semi-transparente
            preview_rect = pygame.Rect(100, 520, SCREEN_WIDTH - 200, 80)
            preview_surface = pygame.Surface((preview_rect.width, preview_rect.height))
            preview_surface.fill(COLORS['card'])
            preview_surface.set_alpha(150)
            self.screen.blit(preview_surface, preview_rect)
            
            # Texto de siguiente pregunta
            next_label = self.font_tiny.render("SIGUIENTE PREGUNTA:", True, COLORS['text_muted'])
            next_label_rect = next_label.get_rect(center=(SCREEN_WIDTH // 2, 545))
            self.screen.blit(next_label, next_label_rect)
            
            # Preview de la pregunta
            q_preview = self.current_question.pregunta[:60] + "..." if len(self.current_question.pregunta) > 60 else self.current_question.pregunta
            q_text = self.font_small.render(q_preview, True, COLORS['text_gray'])
            q_rect = q_text.get_rect(center=(SCREEN_WIDTH // 2, 575))
            self.screen.blit(q_text, q_rect)
    
    def draw_question_phase(self):
        """
        Dibuja la fase de pregunta donde ambos jugadores pueden responder.
        
        Muestra:
        - Temporizador de 30 segundos
        - La pregunta actual
        - Opciones de respuesta con teclas para ambos jugadores
        - Estado de cada jugador (bloqueado o puede responder)
        
        Returns:
            None
        """
        # ========== TEMPORIZADOR ==========
        time_percent = self.question_time_remaining / QUESTION_TIME_LIMIT
        is_low_time = self.question_time_remaining <= 10
        
        # Panel del temporizador
        timer_panel = pygame.Rect(SCREEN_WIDTH // 2 - 150, 230, 300, 50)
        timer_color = COLORS['error'] if is_low_time else COLORS['question']
        self.draw_rounded_rect(self.screen, timer_color, timer_panel, 12, 3, COLORS['text_white'])
        
        # Texto del tiempo
        time_str = f"TIEMPO: {self.question_time_remaining}s"
        time_text = self.font_large.render(time_str, True, COLORS['text_white'])
        time_rect = time_text.get_rect(center=timer_panel.center)
        self.screen.blit(time_text, time_rect)
        
        # ========== BARRA DE TIEMPO ==========
        timer_bg_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, 290, 400, 15)
        timer_fg_width = int(400 * time_percent)
        timer_fg_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, 290, timer_fg_width, 15)
        
        self.draw_rounded_rect(self.screen, COLORS['border'], timer_bg_rect, 6)
        if time_percent > 0:
            bar_color = COLORS['error'] if is_low_time else COLORS['question']
            self.draw_rounded_rect(self.screen, bar_color, timer_fg_rect, 6)
        
        # ========== PREGUNTA ==========
        self.draw_question_panel(320)
        
        # ========== OPCIONES DE RESPUESTA ==========
        self.draw_answer_options_dual()
        
        # ========== ESTADO DE JUGADORES ==========
        self.draw_player_status()
    
    def draw_result_phase(self):
        """
        Dibuja la fase de resultado despues de responder o timeout.
        
        Muestra:
        - Si alguien acerto, quien gano el punto
        - Si ambos fallaron o hubo timeout
        - La respuesta correcta
        - Mensaje de siguiente pregunta
        
        Returns:
            None
        """
        # ========== RESULTADO ==========
        if self.round_winner is not None:
            # Alguien gano
            winner_color = COLORS['player1'] if self.round_winner == 1 else COLORS['player2']
            winner_name = "JUGADOR 1" if self.round_winner == 1 else "JUGADOR 2"
            result_text = f"{winner_name} GANA EL PUNTO!"
            result_color = winner_color
        elif self.last_answer_correct is None:
            # Timeout
            result_text = "TIEMPO AGOTADO!"
            result_color = COLORS['accent']
        else:
            # Ambos fallaron
            result_text = "NADIE ACERTO"
            result_color = COLORS['error']
        
        # Panel de resultado
        result_rect = pygame.Rect(SCREEN_WIDTH // 2 - 220, 240, 440, 80)
        self.draw_rounded_rect(self.screen, result_color, result_rect, 15, 4, COLORS['text_white'])
        
        result_label = self.font_large.render(result_text, True, COLORS['text_white'])
        result_label_rect = result_label.get_rect(center=result_rect.center)
        self.screen.blit(result_label, result_label_rect)
        
        # ========== PREGUNTA CON RESPUESTA CORRECTA ==========
        self.draw_question_panel(340)
        
        # Mostrar respuesta correcta
        if self.current_question:
            correct_text = self.font_medium.render(
                f"Respuesta correcta: {self.current_question.respuesta_correcta}", 
                True, COLORS['success']
            )
            correct_rect = correct_text.get_rect(center=(SCREEN_WIDTH // 2, 540))
            self.screen.blit(correct_text, correct_rect)
        
        # ========== ROBOT CELEBRANDO (si hay ganador) ==========
        if self.round_winner is not None:
            winner_color = COLORS['player1'] if self.round_winner == 1 else COLORS['player2']
            robot_x = SCREEN_WIDTH // 2
            robot_y = 620
            bounce = abs(math.sin(self.animation_time * 0.2)) * 15
            self.draw_robot(robot_x, int(robot_y - bounce), 50, winner_color, 0)
        
        # ========== MENSAJE SIGUIENTE ==========
        next_text = self.font_small.render("Siguiente pregunta en unos segundos...", True, COLORS['text_gray'])
        next_rect = next_text.get_rect(center=(SCREEN_WIDTH // 2, 680))
        self.screen.blit(next_text, next_rect)
    
    def draw_question_panel(self, y_pos: int):
        """
        Dibuja el panel con la pregunta actual.
        
        Args:
            y_pos (int): Posicion Y donde colocar el panel
        
        Returns:
            None
        """
        # Panel de pregunta
        q_panel_rect = pygame.Rect(60, y_pos, SCREEN_WIDTH - 120, 100)
        self.draw_rounded_rect(self.screen, COLORS['card'], q_panel_rect, 12, 2, COLORS['accent'])
        
        # Etiqueta
        q_label = self.font_tiny.render("PREGUNTA", True, COLORS['accent'])
        q_label_rect = q_label.get_rect(center=(SCREEN_WIDTH // 2, y_pos + 20))
        self.screen.blit(q_label, q_label_rect)
        
        # Texto de la pregunta
        if self.current_question:
            question_text = self.current_question.pregunta
            
            # Dividir en lineas si es muy largo
            if len(question_text) > 70:
                words = question_text.split()
                mid = len(words) // 2
                line1 = ' '.join(words[:mid])
                line2 = ' '.join(words[mid:])
                
                q_text1 = self.font_medium.render(line1, True, COLORS['text_white'])
                q_text2 = self.font_medium.render(line2, True, COLORS['text_white'])
                
                q_rect1 = q_text1.get_rect(center=(SCREEN_WIDTH // 2, y_pos + 50))
                q_rect2 = q_text2.get_rect(center=(SCREEN_WIDTH // 2, y_pos + 75))
                
                self.screen.blit(q_text1, q_rect1)
                self.screen.blit(q_text2, q_rect2)
            else:
                q_text = self.font_medium.render(question_text, True, COLORS['text_white'])
                q_rect = q_text.get_rect(center=(SCREEN_WIDTH // 2, y_pos + 60))
                self.screen.blit(q_text, q_rect)
    
    def draw_answer_options_dual(self):
        """
        Dibuja las opciones de respuesta mostrando teclas de ambos jugadores.
        
        Muestra:
        - Las 3 opciones de respuesta
        - Teclas de J1 (A, S, D) y J2 (J, K, L) en cada opcion
        - Estado bloqueado si aplica
        
        Returns:
            None
        """
        if not self.current_options:
            return
        
        # Configuracion
        option_width = 320
        option_height = 70
        option_gap = 20
        total_width = option_width * 3 + option_gap * 2
        start_x = (SCREEN_WIDTH - total_width) // 2
        option_y = 440
        
        # Teclas de cada jugador
        keys_p1 = ["A", "S", "D"]
        keys_p2 = ["J", "K", "L"]
        
        for i, option in enumerate(self.current_options):
            opt_x = start_x + i * (option_width + option_gap)
            opt_rect = pygame.Rect(opt_x, option_y, option_width, option_height)
            
            # Dibujar opcion
            self.draw_rounded_rect(self.screen, COLORS['card'], opt_rect, 12, 2, COLORS['border'])
            
            # Numero de opcion
            num_text = self.font_medium.render(f"{i+1}.", True, COLORS['accent'])
            self.screen.blit(num_text, (opt_rect.x + 15, opt_rect.y + 10))
            
            # Texto de la opcion (truncar si es muy largo)
            opt_text_str = str(option)[:20] + "..." if len(str(option)) > 20 else str(option)
            opt_text = self.font_medium.render(opt_text_str, True, COLORS['text_white'])
            opt_text_rect = opt_text.get_rect(centerx=opt_rect.centerx, top=opt_rect.y + 10)
            self.screen.blit(opt_text, opt_text_rect)
            
            # ========== TECLAS DE AMBOS JUGADORES ==========
            key_y = opt_rect.bottom - 25
            
            # Tecla J1 (izquierda)
            key_rect_p1 = pygame.Rect(opt_rect.x + 20, key_y, 35, 22)
            p1_color = COLORS['track_segment'] if self.player1.blocked_this_round else COLORS['player1']
            self.draw_rounded_rect(self.screen, p1_color, key_rect_p1, 6)
            key_text_p1 = self.font_small.render(keys_p1[i], True, COLORS['background'])
            key_text_rect_p1 = key_text_p1.get_rect(center=key_rect_p1.center)
            self.screen.blit(key_text_p1, key_text_rect_p1)
            
            # Tecla J2 (derecha)
            key_rect_p2 = pygame.Rect(opt_rect.right - 55, key_y, 35, 22)
            p2_color = COLORS['track_segment'] if self.player2.blocked_this_round else COLORS['player2']
            self.draw_rounded_rect(self.screen, p2_color, key_rect_p2, 6)
            key_text_p2 = self.font_small.render(keys_p2[i], True, COLORS['background'])
            key_text_rect_p2 = key_text_p2.get_rect(center=key_rect_p2.center)
            self.screen.blit(key_text_p2, key_text_rect_p2)
    
    def draw_player_status(self):
        """
        Dibuja el estado actual de cada jugador (puede responder o bloqueado).
        
        Returns:
            None
        """
        status_y = 530
        
        # ========== JUGADOR 1 ==========
        p1_rect = pygame.Rect(100, status_y, 200, 40)
        if self.player1.blocked_this_round:
            p1_color = COLORS['error']
            p1_text = "J1: BLOQUEADO"
        else:
            p1_color = COLORS['player1']
            p1_text = "J1: Puede responder"
        
        self.draw_rounded_rect(self.screen, p1_color, p1_rect, 10, 2, COLORS['text_white'])
        p1_label = self.font_small.render(p1_text, True, COLORS['text_white'])
        p1_label_rect = p1_label.get_rect(center=p1_rect.center)
        self.screen.blit(p1_label, p1_label_rect)
        
        # ========== JUGADOR 2 ==========
        p2_rect = pygame.Rect(SCREEN_WIDTH - 300, status_y, 200, 40)
        if self.player2.blocked_this_round:
            p2_color = COLORS['error']
            p2_text = "J2: BLOQUEADO"
        else:
            p2_color = COLORS['player2']
            p2_text = "J2: Puede responder"
        
        self.draw_rounded_rect(self.screen, p2_color, p2_rect, 10, 2, COLORS['text_white'])
        p2_label = self.font_small.render(p2_text, True, COLORS['text_white'])
        p2_label_rect = p2_label.get_rect(center=p2_rect.center)
        self.screen.blit(p2_label, p2_label_rect)
    
    # ==========================================================================
    #                     PANTALLA DE FIN DE JUEGO
    # ==========================================================================
    
    def draw_game_over(self):
        """
        Dibuja la pantalla de fin de juego con resultados.
        
        Muestra:
        - Overlay oscuro sobre el juego
        - Panel central con resultados
        - Mensaje de ganador o empate
        - Puntuaciones de ambos jugadores
        - Instrucciones para reiniciar
        
        Returns:
            None
        """
        # ========== OVERLAY OSCURO ==========
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(COLORS['background'])
        overlay.set_alpha(230)
        self.screen.blit(overlay, (0, 0))
        
        # ========== PANEL CENTRAL ==========
        panel_rect = pygame.Rect(SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 200, 500, 400)
        self.draw_rounded_rect(self.screen, COLORS['card'], panel_rect, 20, 3, COLORS['accent'])
        
        # ========== MENSAJE DE GANADOR ==========
        if self.winner == 0:
            winner_text = "EMPATE!"
            winner_color = COLORS['accent']
        elif self.winner == 1:
            winner_text = "JUGADOR 1 GANA!"
            winner_color = COLORS['player1']
        else:
            winner_text = "JUGADOR 2 GANA!"
            winner_color = COLORS['player2']
        
        title = self.font_large.render(winner_text, True, winner_color)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 120))
        self.screen.blit(title, title_rect)
        
        # ========== ROBOT GANADOR ==========
        if self.winner != 0:
            self.draw_robot(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, 60, winner_color, 
                           int(math.sin(self.animation_time * 0.1) * 5))
        
        # ========== ESTADISTICAS ==========
        stats_text = self.font_small.render(f"Preguntas respondidas: {self.questions_answered}", True, COLORS['text_white'])
        stats_rect = stats_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(stats_text, stats_rect)
        
        # ========== PANELES DE PUNTUACION ==========
        score_rect_1 = pygame.Rect(panel_rect.x + 30, SCREEN_HEIGHT // 2 + 50, 200, 80)
        score_rect_2 = pygame.Rect(panel_rect.right - 230, SCREEN_HEIGHT // 2 + 50, 200, 80)
        
        # Panel Jugador 1
        p1_bg = COLORS['player1'] if self.winner == 1 else COLORS['card_hover']
        self.draw_rounded_rect(self.screen, p1_bg, score_rect_1, 12, 2, COLORS['player1'])
        
        p1_label = self.font_small.render("Jugador 1", True, COLORS['text_gray'])
        p1_label_rect = p1_label.get_rect(centerx=score_rect_1.centerx, top=score_rect_1.y + 10)
        self.screen.blit(p1_label, p1_label_rect)
        
        p1_score = self.font_title.render(str(self.player1.score), True, COLORS['player1'])
        p1_score_rect = p1_score.get_rect(center=(score_rect_1.centerx, score_rect_1.centery + 15))
        self.screen.blit(p1_score, p1_score_rect)
        
        # Panel Jugador 2
        p2_bg = COLORS['player2'] if self.winner == 2 else COLORS['card_hover']
        self.draw_rounded_rect(self.screen, p2_bg, score_rect_2, 12, 2, COLORS['player2'])
        
        p2_label = self.font_small.render("Jugador 2", True, COLORS['text_white'])        
        p2_label_rect = p2_label.get_rect(centerx=score_rect_2.centerx, top=score_rect_2.y + 10)
        self.screen.blit(p2_label, p2_label_rect)
        
        p2_score = self.font_title.render(str(self.player2.score), True, COLORS['player2'])
        p2_score_rect = p2_score.get_rect(center=(score_rect_2.centerx, score_rect_2.centery + 15))
        self.screen.blit(p2_score, p2_score_rect)
        
        # ========== INSTRUCCIONES ==========
        restart_text = self.font_medium.render("Presiona ESPACIO para jugar de nuevo", True, COLORS['text_gray'])
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 160))
        self.screen.blit(restart_text, restart_rect)
    
    # ==========================================================================
    #                      FUNCION PRINCIPAL DE DIBUJO
    # ==========================================================================
    
    def draw(self):
        """
        Funcion principal de renderizado que dibuja segun la fase actual.
        
        Llama a la funcion de dibujo apropiada segun el estado del juego:
        - MENU: Dibuja el menu de seleccion de nivel
        - COUNTDOWN/QUESTION/RESULT_PAUSE: Dibuja la pantalla de juego
        - FINISHED: Dibuja la pantalla de juego con overlay de fin
        
        Returns:
            None
        """
        if self.phase == GamePhase.MENU:
            self.draw_menu()
        elif self.phase == GamePhase.FINISHED:
            self.draw_game()
            self.draw_game_over()
        else:
            self.draw_game()
        
        # Actualizar la pantalla
        pygame.display.flip()
    
    # ==========================================================================
    #                       BUCLE PRINCIPAL
    # ==========================================================================
    
    def run(self):
        """
        Ejecuta el bucle principal del juego.
        
        Este metodo contiene el game loop que:
        1. Procesa eventos de entrada
        2. Actualiza la logica del juego
        3. Renderiza los graficos
        4. Controla la velocidad de ejecucion
        
        El bucle continua hasta que el usuario cierra la ventana
        o handle_events() retorna False.
        
        Returns:
            None
        """
        print("\n" + "="*60)
        print("            ROBOT RACE QUIZ v6.0")
        print("       Interludio 3,2,1 + 30 segundos para responder")
        print("="*60)
        print("\nControles:")
        print("  INTERLUDIO: Cuenta regresiva 3, 2, 1...")
        print("  PREGUNTA: J1 (A/S/D) | J2 (J/K/L) - 30 segundos")
        print("  El primero en responder CORRECTAMENTE gana!")
        print("  Si respondes MAL quedas bloqueado esa ronda")
        print("  MENU: 1, 2, 3 para nivel | ESC para salir")
        print("="*60 + "\n")
        
        running = True
        while running:
            # Procesar eventos
            running = self.handle_events()
            
            # Actualizar estado del juego
            self.update()
            
            # Dibujar graficos
            self.draw()
            
            # Controlar FPS
            self.clock.tick(FPS)
        
        # Limpiar recursos de Pygame
        pygame.quit()
        print("\n[JUEGO] Robot Race Quiz finalizado. Gracias por jugar!")


# ==============================================================================
#                           PUNTO DE ENTRADA
# ==============================================================================

def main():
    """
    Funcion principal que inicia el juego.
    
    Crea una instancia de RobotRaceGame y ejecuta el bucle principal.
    Esta funcion es el punto de entrada cuando se ejecuta el script.
    
    Returns:
        None
    """
    game = RobotRaceGame()
    game.run()


if __name__ == "__main__":
    main()
