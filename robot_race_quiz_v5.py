"""
================================================================================
                        ROBOT RACE QUIZ - VERSION 7.0
                 Juego de carreras de robots con quiz educativo
          Compatible con Makey Makey + 2x LEGO EV3 (Bluetooth)
================================================================================

DESCRIPCION:
    Este programa implementa un juego educativo de carreras de robots donde 
    dos jugadores compiten respondiendo preguntas. Cada jugador tiene su 
    propio robot EV3 conectado por Bluetooth, y cada robot usa 2 motores
    (4 motores en total).

ARQUITECTURA DE HARDWARE:
    - Robot EV3 #1 (Jugador 1): Conectado por Bluetooth
        - Motor Puerto A: Motor izquierdo
        - Motor Puerto B: Motor derecho
    - Robot EV3 #2 (Jugador 2): Conectado por Bluetooth
        - Motor Puerto A: Motor izquierdo
        - Motor Puerto B: Motor derecho
    
    Total: 2 robots EV3, 4 motores

CARACTERISTICAS PRINCIPALES v7.0:
    - DOS ROBOTS EV3 INDEPENDIENTES conectados por Bluetooth
    - CADA ROBOT CON 2 MOTORES (avance sincronizado o diferencial)
    - INTERLUDIO "3, 2, 1": Cuenta regresiva animada antes de cada pregunta
    - TIEMPO DE 30 SEGUNDOS: Ambos jugadores pueden responder durante este tiempo
    - RESPUESTA RAPIDA: El primer jugador en responder correctamente gana
    - RESPUESTA INCORRECTA: Si alguien responde mal, queda bloqueado esa ronda
    - TIEMPO AGOTADO: Si nadie responde, la pregunta se invalida
    - INTERFAZ UNICA: Una sola pantalla con la pregunta centrada
    - PREGUNTAS DESECHABLES: Cada pregunta solo se usa una vez
    - Barra de progreso visual estilo pista de carreras segmentada
    - Logos institucionales (Facultad de Matematicas e Ingeniotics)

FLUJO DEL JUEGO:
    1. INTERLUDIO: Cuenta regresiva "3, 2, 1" animada (3 segundos)
    2. PREGUNTA: Se muestra la pregunta y respuestas (30 segundos)
       - Ambos jugadores pueden intentar responder
       - El primero en responder correctamente gana el punto
       - Si alguien responde incorrectamente, queda bloqueado esa ronda
    3. RESULTADO: Se muestra el resultado y se pasa a la siguiente pregunta

REQUISITOS:
    pip install pygame pandas openpyxl pybricks

CONFIGURACION BLUETOOTH:
    1. Emparejar ambos EV3 con la computadora via Bluetooth
    2. Configurar las direcciones MAC en EV3_ROBOT1_MAC y EV3_ROBOT2_MAC
    3. Los robots deben estar encendidos y con Bluetooth visible

CONTROLES:
    - RESPONDER (durante los 30 segundos):
        - Jugador 1: A=opcion1, S=opcion2, W=opcion3
        - Jugador 2: D=opcion1, F=opcion2, G=opcion3
    - Menu: Teclas A/D=Nivel1, S/F=Nivel2, W/G=Nivel3
    - ESC: Salir al menu
    - ESPACIO: Reiniciar (en pantalla de fin de juego)

ESTRUCTURA DEL ARCHIVO EXCEL (preguntas.xlsx):
    Nivel | Pregunta | Respuesta Correcta | R1 | R2

AUTORES:
    Desarrollado para uso educativo
    Facultad de Matematicas | Ingeniotics

FECHA:
    2024-2026
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
try:
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("[AVISO] requests no instalado. Logos desde URL no estaran disponibles.")
    print("        Instalar con: pip install requests")

# ==============================================================================
#            CONFIGURACION EV3 DUAL (2 ROBOTS LEGO MINDSTORMS)
# ==============================================================================
# Dos robots EV3 conectados por Bluetooth, cada uno con 2 motores.
#
# ARQUITECTURA:
#   Robot 1 (Jugador 1):
#     - ev3_robot1: EV3Brick conectado por Bluetooth
#     - motor_r1_left:  Motor Puerto A (izquierdo)
#     - motor_r1_right: Motor Puerto B (derecho)
#
#   Robot 2 (Jugador 2):
#     - ev3_robot2: EV3Brick conectado por Bluetooth
#     - motor_r2_left:  Motor Puerto A (izquierdo)
#     - motor_r2_right: Motor Puerto B (derecho)
#
# NOTA: Para conectar multiples EV3 por Bluetooth, se usa
#       el parametro 'name' del EV3Brick para diferenciarlos.
# ==============================================================================

# --- Intentar conectar con los 2 robots EV3 por Bluetooth ---
EV3_CONNECTED = False

try:
    from pybricks.hubs import EV3Brick
    from pybricks.pupdevices import Motor
    from pybricks.parameters import Port

    # ============================================================
    #  CONFIGURACION: Nombres Bluetooth de cada robot EV3
    #  Cambiar estos nombres segun la configuracion de sus robots
    # ============================================================
    EV3_ROBOT1_NAME = "CHAMCO3000OK"  # Nombre Bluetooth del robot del Jugador 1
    EV3_ROBOT2_NAME = "EV3_Robot2"  # Nombre Bluetooth del robot del Jugador 2

    print("=" * 60)
    print("  CONECTANDO CON 2 ROBOTS EV3 POR BLUETOOTH...")
    print("=" * 60)

    # --- ROBOT 1 (Jugador 1) ---
    print(f"\n[EV3] Conectando Robot 1 (Jugador 1): '{EV3_ROBOT1_NAME}'...")
    try:
        ev3_robot1 = EV3Brick()
        motor_r1_left  = Motor(Port.A)   # Motor izquierdo del Robot 1
        motor_r1_right = Motor(Port.B)   # Motor derecho del Robot 1
        print("[OK] Robot 1 conectado exitosamente")
        print(f"     - Motor izquierdo: Puerto A")
        print(f"     - Motor derecho:   Puerto B")
        ROBOT1_CONNECTED = True
    except Exception as e:
        print(f"[ERROR] No se pudo conectar Robot 1: {e}")
        ROBOT1_CONNECTED = False

    # --- ROBOT 2 (Jugador 2) ---
    print(f"\n[EV3] Conectando Robot 2 (Jugador 2): '{EV3_ROBOT2_NAME}'...")
    try:
        ev3_robot2 = EV3Brick()
        motor_r2_left  = Motor(Port.A)   # Motor izquierdo del Robot 2
        motor_r2_right = Motor(Port.B)   # Motor derecho del Robot 2
        print("[OK] Robot 2 conectado exitosamente")
        print(f"     - Motor izquierdo: Puerto A")
        print(f"     - Motor derecho:   Puerto B")
        ROBOT2_CONNECTED = True
    except Exception as e:
        print(f"[ERROR] No se pudo conectar Robot 2: {e}")
        ROBOT2_CONNECTED = False

    # Verificar si ambos estan conectados
    EV3_CONNECTED = ROBOT1_CONNECTED and ROBOT2_CONNECTED

    if EV3_CONNECTED:
        print("\n[OK] AMBOS ROBOTS EV3 CONECTADOS CORRECTAMENTE!")
        print("     Robot 1 (J1): 2 motores (Puerto A + Puerto B)")
        print("     Robot 2 (J2): 2 motores (Puerto A + Puerto B)")
        print("     Total: 4 motores activos")
    else:
        if not ROBOT1_CONNECTED:
            print("\n[AVISO] Robot 1 NO conectado - Jugador 1 usara simulacion")
        if not ROBOT2_CONNECTED:
            print("\n[AVISO] Robot 2 NO conectado - Jugador 2 usara simulacion")

except ImportError:
    print("[AVISO] pybricks no instalado. Usando modo simulacion.")
    print("        Instalar con: pip install pybricks")
    ROBOT1_CONNECTED = False
    ROBOT2_CONNECTED = False
except Exception as e:
    print(f"[ERROR] Error general conectando EV3: {e}")
    ROBOT1_CONNECTED = False
    ROBOT2_CONNECTED = False


# ==============================================================================
#              FUNCIONES DE CONTROL DE ROBOTS (2 EV3 + 4 MOTORES)
# ==============================================================================

# --- Velocidad de los motores (grados/segundo) ---
MOTOR_SPEED = 500           # Velocidad normal de avance
MOTOR_SPEED_CELEBRATE = 1000 # Velocidad de celebracion
DEGREES_PER_UNIT = 10        # Conversion: unidades de juego a grados de motor


def move_robot(player: int, distance: int):
    """
    Mueve el robot EV3 del jugador especificado una distancia determinada.
    Ambos motores del robot giran sincronizados para avanzar recto.
    
    Args:
        player (int): Numero del jugador (1 o 2)
        distance (int): Distancia a mover (en unidades del juego)
    
    Cada robot tiene 2 motores que giran en la misma direccion
    y a la misma velocidad para avanzar en linea recta.
    """
    degrees = distance * DEGREES_PER_UNIT  # Convertir unidades a grados

    if player == 1:
        if ROBOT1_CONNECTED:
            try:
                # Ambos motores del Robot 1 avanzan sincronizados
                motor_r1_left.run_angle(MOTOR_SPEED, degrees, wait=False)
                motor_r1_right.run_angle(MOTOR_SPEED, degrees, wait=True)
                print(f"[EV3-R1] Robot Jugador 1 avanza {distance} unidades ({degrees} grados)")
            except Exception as e:
                print(f"[ERROR] Error moviendo Robot 1: {e}")
        else:
            print(f"[EV3 SIMULADO] Robot Jugador 1 avanza {distance} unidades (2 motores)")

    elif player == 2:
        if ROBOT2_CONNECTED:
            try:
                # Ambos motores del Robot 2 avanzan sincronizados
                motor_r2_left.run_angle(MOTOR_SPEED, degrees, wait=False)
                motor_r2_right.run_angle(MOTOR_SPEED, degrees, wait=True)
                print(f"[EV3-R2] Robot Jugador 2 avanza {distance} unidades ({degrees} grados)")
            except Exception as e:
                print(f"[ERROR] Error moviendo Robot 2: {e}")
        else:
            print(f"[EV3 SIMULADO] Robot Jugador 2 avanza {distance} unidades (2 motores)")


def celebrate_robot(player: int):
    """
    Hace que el robot ganador ejecute una animacion de celebracion.
    Ambos motores giran en direcciones opuestas para hacer un "giro loco".
    
    Args:
        player (int): Numero del jugador ganador (1 o 2)
    
    Secuencia de celebracion (3 repeticiones):
        1. Motor izquierdo adelante + Motor derecho atras (giro sobre su eje)
        2. Motor izquierdo atras + Motor derecho adelante (giro inverso)
    """
    if player == 1 and ROBOT1_CONNECTED:
        try:
            print("[EV3-R1] Robot Jugador 1 celebrando!")
            for i in range(3):
                # Giro sobre su eje: motores en direcciones opuestas
                motor_r1_left.run_angle(MOTOR_SPEED_CELEBRATE, 360, wait=False)
                motor_r1_right.run_angle(MOTOR_SPEED_CELEBRATE, -360, wait=True)
                # Giro inverso
                motor_r1_left.run_angle(MOTOR_SPEED_CELEBRATE, -360, wait=False)
                motor_r1_right.run_angle(MOTOR_SPEED_CELEBRATE, 360, wait=True)
        except Exception as e:
            print(f"[ERROR] Error en celebracion Robot 1: {e}")

    elif player == 2 and ROBOT2_CONNECTED:
        try:
            print("[EV3-R2] Robot Jugador 2 celebrando!")
            for i in range(3):
                # Giro sobre su eje: motores en direcciones opuestas
                motor_r2_left.run_angle(MOTOR_SPEED_CELEBRATE, 360, wait=False)
                motor_r2_right.run_angle(MOTOR_SPEED_CELEBRATE, -360, wait=True)
                # Giro inverso
                motor_r2_left.run_angle(MOTOR_SPEED_CELEBRATE, -360, wait=False)
                motor_r2_right.run_angle(MOTOR_SPEED_CELEBRATE, 360, wait=True)
        except Exception as e:
            print(f"[ERROR] Error en celebracion Robot 2: {e}")

    else:
        print(f"[EV3 SIMULADO] Robot del Jugador {player} celebra la victoria! (2 motores)")


def stop_all_robots():
    """
    Detiene todos los motores de ambos robots.
    Util para paradas de emergencia o al finalizar el juego.
    """
    if ROBOT1_CONNECTED:
        try:
            motor_r1_left.stop()
            motor_r1_right.stop()
            print("[EV3-R1] Robot 1 detenido")
        except Exception as e:
            print(f"[ERROR] Error deteniendo Robot 1: {e}")

    if ROBOT2_CONNECTED:
        try:
            motor_r2_left.stop()
            motor_r2_right.stop()
            print("[EV3-R2] Robot 2 detenido")
        except Exception as e:
            print(f"[ERROR] Error deteniendo Robot 2: {e}")


def get_ev3_status() -> dict:
    """
    Retorna el estado de conexion de ambos robots.
    
    Returns:
        dict: Estado de conexion de cada robot y conteo de motores
    """
    return {
        'robot1_connected': ROBOT1_CONNECTED,
        'robot2_connected': ROBOT2_CONNECTED,
        'both_connected': EV3_CONNECTED,
        'total_motors': (2 if ROBOT1_CONNECTED else 0) + (2 if ROBOT2_CONNECTED else 0),
        'robot1_motors': 2 if ROBOT1_CONNECTED else 0,
        'robot2_motors': 2 if ROBOT2_CONNECTED else 0,
    }


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
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h

# Velocidad de actualizacion del juego
FPS = 60

# ==================== TIEMPOS DE CADA FASE ====================
COUNTDOWN_DURATION = 1.0       # 1 segundo por cada numero (total 3 segundos)
QUESTION_TIME_LIMIT = 30       # Tiempo limite para responder (segundos)
RESULT_PAUSE_DURATION = 2500   # Pausa despues de responder (milisegundos)

# Nombres de los archivos locales de logos
LOGO_FAC_FILE = "LOGO_FAC.png"
LOGO_INGENIOTICS_FILE = "ingenio2.png"

# ==============================================================================
#                         PALETA DE COLORES
# ==============================================================================

COLORS = {
    # Colores de fondo
    'background': (20, 22, 35),
    'card': (30, 32, 50),
    'card_hover': (40, 42, 65),
    
    # Colores de texto
    'text_white': (248, 250, 252),
    'text_gray': (148, 163, 184),
    'text_muted': (100, 116, 139),
    
    # Colores del Jugador 1 (Verde)
    'player1': (34, 197, 94),
    'player1_light': (74, 222, 128),
    'player1_dark': (22, 163, 74),
    
    # Colores del Jugador 2 (Naranja)
    'player2': (249, 115, 22),
    'player2_light': (251, 146, 60),
    'player2_dark': (234, 88, 12),
    
    # Colores de acento y estado
    'accent': (250, 204, 21),
    'success': (34, 197, 94),
    'error': (239, 68, 68),
    'countdown': (147, 51, 234),
    'question': (59, 130, 246),
    
    # Colores de interfaz
    'border': (51, 65, 85),
    'track_bg': (15, 23, 42),
    'track_segment': (30, 41, 59),
    'finish': (250, 204, 21),
    
    # Color para indicadores EV3
    'bluetooth': (59, 130, 246),
}


# ==============================================================================
#                      ENUMERACIONES Y CLASES DE DATOS
# ==============================================================================

class GamePhase(Enum):
    """
    Enumeracion que define las fases/estados posibles del juego.
    """
    MENU = "menu"
    COUNTDOWN = "countdown"
    QUESTION = "question"
    RESULT_PAUSE = "result_pause"
    FINISHED = "finished"


@dataclass
class Question:
    """
    Clase de datos que representa una pregunta del quiz.
    """
    nivel: int
    pregunta: str
    respuesta_correcta: str
    r1: str
    r2: str


@dataclass 
class PlayerState:
    """
    Clase de datos que mantiene el estado actual de un jugador.
    """
    position: float = 0.0
    target_position: float = 0.0
    score: int = 0
    last_answer: Optional[str] = None
    message: str = ""
    message_type: str = "info"
    animation_offset: float = 0.0
    blocked_this_round: bool = False


# ==============================================================================
#                      CLASE PRINCIPAL DEL JUEGO
# ==============================================================================

class RobotRaceGame:
    """
    Clase principal que controla toda la logica del juego Robot Race Quiz.
    
    Version 7.0: Soporta 2 robots EV3 independientes conectados por Bluetooth,
    cada uno con 2 motores (4 motores en total).
    """
    
    def __init__(self):
        """
        Constructor de la clase RobotRaceGame.
        """
        # ==================== CONFIGURACION DE PANTALLA ====================
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Robot Race Quiz v7.0 - Dual EV3 Bluetooth (4 Motores)")
        self.clock = pygame.time.Clock()
        
        # ==================== FUENTES TIPOGRAFICAS ====================
        self.font_title = pygame.font.Font(None, 56)
        self.font_countdown = pygame.font.Font(None, 200)
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        self.font_tiny = pygame.font.Font(None, 18)
        
        # ==================== ESTADO DEL JUEGO ====================
        self.phase = GamePhase.MENU
        self.level = 1
        self.player1 = PlayerState()
        self.player2 = PlayerState()
        self.winner = None
        
        # ==================== PREGUNTAS ====================
        self.questions: List[Question] = []
        self.available_questions: List[Question] = []
        self.current_question: Optional[Question] = None
        self.current_options: List[str] = []
        self.questions_answered = 0
        
        # ==================== SISTEMA DE INTERLUDIO ====================
        self.countdown_number = 3
        self.countdown_start_time = 0
        
        # ==================== RESULTADO DE RONDA ====================
        self.round_winner: Optional[int] = None
        self.last_answer_correct: Optional[bool] = None
        self.result_pause_start = 0
        
        # ==================== TEMPORIZADOR DE PREGUNTA ====================
        self.question_time_remaining = QUESTION_TIME_LIMIT
        self.question_start_time = 0
        
        # ==================== CONSTANTES DEL JUEGO ====================
        self.WINNING_POSITION = 100
        self.POSITION_INCREMENT = 20
        self.TOTAL_SEGMENTS = 5
        
        # ==================== ANIMACION ====================
        self.animation_time = 0
        self.hover_level = None
        
        # ==================== LOGOS ====================
        self.logo_fac = None
        self.logo_ingeniotics = None
        
        # ==================== ESTADO EV3 ====================
        self.ev3_status = get_ev3_status()
        
        # ==================== CARGAR RECURSOS ====================
        self.load_questions_from_excel()
        self.load_logos()
    
    # ==========================================================================
    #                        CARGA DE LOGOS
    # ==========================================================================
    
    def load_logos(self):
        """
        Carga los logos institucionales desde archivos locales.
        """
        base_path = os.path.dirname(os.path.abspath(__file__))
        
        path_fac = os.path.join(base_path, LOGO_FAC_FILE)
        path_ing = os.path.join(base_path, LOGO_INGENIOTICS_FILE)
        
        if os.path.exists(path_fac):
            try:
                print(f"[INFO] Cargando logo Facultad desde: {path_fac}")
                self.logo_fac = pygame.image.load(path_fac)
                self.logo_fac = pygame.transform.scale(self.logo_fac, (150, 100))
                print("[OK] Logo Facultad cargado correctamente")
            except Exception as e:
                print(f"[ERROR] No se pudo cargar la imagen {LOGO_FAC_FILE}: {e}")
        else:
            print(f"[AVISO] No se encontro el archivo: {LOGO_FAC_FILE}")
            
        if os.path.exists(path_ing):
            try:
                print(f"[INFO] Cargando logo Ingeniotics desde: {path_ing}")
                self.logo_ingeniotics = pygame.image.load(path_ing)
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
        """
        excel_file = "preguntasCompletasVirgilio.xlsx"
        
        possible_paths = [
            excel_file,
            os.path.join(os.path.dirname(__file__), excel_file),
            os.path.join(os.getcwd(), excel_file),
        ]
        
        file_found = None
        for path in possible_paths:
            if os.path.exists(path):
                file_found = path
                break
        
        if file_found:
            try:
                df = pd.read_excel(file_found)
                
                required_columns = ['Nivel', 'Pregunta', 'Respuesta Correcta', 'R1', 'R2']
                missing = [col for col in required_columns if col not in df.columns]
                
                if missing:
                    print(f"[ERROR] Columnas faltantes en Excel: {missing}")
                    print(f"[INFO] Columnas encontradas: {list(df.columns)}")
                    self.load_default_questions()
                    return
                
                for _, row in df.iterrows():
                    try:
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
        Carga un conjunto de preguntas predeterminadas como fallback.
        """
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
        
        for data in default_data:
            self.questions.append(Question(*data))
        
        print(f"[OK] Cargadas {len(self.questions)} preguntas por defecto")
    
    # ==========================================================================
    #                    GESTION DE PREGUNTAS
    # ==========================================================================
    
    def get_questions_by_level(self, level: int) -> List[Question]:
        return [q for q in self.questions if q.nivel == level]
    
    def shuffle_options(self, question: Question) -> List[str]:
        options = [question.respuesta_correcta, question.r1, question.r2]
        random.shuffle(options)
        return options
    
    def start_countdown_for_next_question(self):
        """
        Inicia la cuenta regresiva "3, 2, 1" para la siguiente pregunta.
        """
        self.round_winner = None
        self.last_answer_correct = None
        self.player1.last_answer = None
        self.player1.message = ""
        self.player1.blocked_this_round = False
        self.player2.last_answer = None
        self.player2.message = ""
        self.player2.blocked_this_round = False
        
        if not self.available_questions:
            print("[INFO] No hay mas preguntas disponibles")
            self.determine_winner()
            return
        
        self.current_question = self.available_questions.pop(0)
        self.current_options = self.shuffle_options(self.current_question)
        
        self.questions_answered += 1
        
        self.phase = GamePhase.COUNTDOWN
        self.countdown_number = 3
        self.countdown_start_time = time.time()
        
        print(f"\n[PREGUNTA {self.questions_answered}] Iniciando cuenta regresiva...")
        print(f"[INFO] Pregunta: {self.current_question.pregunta}")
        print(f"[INFO] Respuesta correcta: {self.current_question.respuesta_correcta}")
    
    def start_question_phase(self):
        """
        Inicia la fase de pregunta donde ambos jugadores pueden responder.
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
        """
        self.level = level
        self.winner = None
        self.questions_answered = 0
        
        self.player1 = PlayerState()
        self.player2 = PlayerState()
        
        level_questions = self.get_questions_by_level(level)
        self.available_questions = random.sample(level_questions, len(level_questions))
        
        print(f"\n[JUEGO] Iniciando nivel {level} con {len(level_questions)} preguntas")
        print(f"[JUEGO] Flujo: Cuenta regresiva (3,2,1) -> Pregunta ({QUESTION_TIME_LIMIT}s)")
        
        # Mostrar estado de conexion EV3
        status = get_ev3_status()
        print(f"[EV3] Estado: {status['total_motors']} motores activos")
        if status['robot1_connected']:
            print(f"     Robot 1 (J1): CONECTADO (2 motores)")
        else:
            print(f"     Robot 1 (J1): SIMULADO")
        if status['robot2_connected']:
            print(f"     Robot 2 (J2): CONECTADO (2 motores)")
        else:
            print(f"     Robot 2 (J2): SIMULADO")
        
        self.start_countdown_for_next_question()
    
    def answer_question(self, player: int, answer_index: int):
        """
        Procesa la respuesta de un jugador.
        Ambos motores del robot del jugador se activan al acertar.
        """
        if self.phase != GamePhase.QUESTION:
            return
        
        player_state = self.player1 if player == 1 else self.player2
        if player_state.blocked_this_round:
            print(f"[JUEGO] Jugador {player} esta bloqueado esta ronda")
            return
        
        if not self.current_question:
            return
        
        if answer_index >= len(self.current_options):
            return
        
        selected_answer = self.current_options[answer_index]
        is_correct = selected_answer == self.current_question.respuesta_correcta
        
        if is_correct:
            # ========== RESPUESTA CORRECTA ==========
            self.round_winner = player
            self.last_answer_correct = True
            
            player_state.target_position = min(
                player_state.target_position + self.POSITION_INCREMENT, 
                self.WINNING_POSITION
            )
            
            player_state.score += 1
            player_state.message = "CORRECTO! +1 punto"
            player_state.message_type = "success"
            player_state.last_answer = "correct"
            
            # Mover robot fisico EV3 (ambos motores del robot correspondiente)
            move_robot(player, self.POSITION_INCREMENT)
            
            print(f"[JUEGO] Jugador {player}: CORRECTO - Puntos: {player_state.score}")
            
            if player_state.target_position >= self.WINNING_POSITION:
                self.winner = player
                self.phase = GamePhase.FINISHED
                celebrate_robot(player)
                print(f"[JUEGO] Jugador {player} GANA!")
                return
            
            self.phase = GamePhase.RESULT_PAUSE
            self.result_pause_start = pygame.time.get_ticks()
            
        else:
            # ========== RESPUESTA INCORRECTA ==========
            player_state.blocked_this_round = True
            player_state.message = f"Incorrecto! Bloqueado esta ronda"
            player_state.message_type = "error"
            player_state.last_answer = "incorrect"
            
            print(f"[JUEGO] Jugador {player}: INCORRECTO - Bloqueado esta ronda")
            
            if self.player1.blocked_this_round and self.player2.blocked_this_round:
                self.last_answer_correct = False
                self.round_winner = None
                self.phase = GamePhase.RESULT_PAUSE
                self.result_pause_start = pygame.time.get_ticks()
                print("[JUEGO] Ambos jugadores fallaron - Siguiente pregunta")
    
    def handle_timeout(self):
        """
        Maneja el caso cuando se acaba el tiempo para responder.
        """
        print("[JUEGO] Tiempo agotado - Pregunta invalidada!")
        
        self.round_winner = None
        self.last_answer_correct = None
        
        self.player1.message = "Tiempo agotado!"
        self.player1.message_type = "warning"
        self.player2.message = "Tiempo agotado!"
        self.player2.message_type = "warning"
        
        self.phase = GamePhase.RESULT_PAUSE
        self.result_pause_start = pygame.time.get_ticks()
    
    def determine_winner(self):
        """
        Determina el ganador cuando se acaban las preguntas.
        """
        self.phase = GamePhase.FINISHED
        
        if self.player1.score > self.player2.score:
            self.winner = 1
            celebrate_robot(1)
            print(f"[JUEGO] Jugador 1 GANA! ({self.player1.score} vs {self.player2.score})")
        elif self.player2.score > self.player1.score:
            self.winner = 2
            celebrate_robot(2)
            print(f"[JUEGO] Jugador 2 GANA! ({self.player2.score} vs {self.player1.score})")
        else:
            self.winner = 0
            print(f"[JUEGO] EMPATE! ({self.player1.score} = {self.player2.score})")
    
    def reset_game(self):
        """
        Reinicia el juego al estado inicial (menu).
        Detiene todos los motores de ambos robots.
        """
        # Detener todos los robots al reiniciar
        stop_all_robots()
        
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
        """
        self.animation_time += 1
        
        # ========== MANEJAR FASE DE CUENTA REGRESIVA ==========
        if self.phase == GamePhase.COUNTDOWN:
            elapsed = time.time() - self.countdown_start_time
            
            if elapsed < COUNTDOWN_DURATION:
                self.countdown_number = 3
            elif elapsed < COUNTDOWN_DURATION * 2:
                self.countdown_number = 2
            elif elapsed < COUNTDOWN_DURATION * 3:
                self.countdown_number = 1
            else:
                self.start_question_phase()
        
        # ========== MANEJAR FASE DE PREGUNTA ==========
        if self.phase == GamePhase.QUESTION:
            elapsed = time.time() - self.question_start_time
            self.question_time_remaining = max(0, QUESTION_TIME_LIMIT - int(elapsed))
            
            if self.question_time_remaining <= 0:
                self.handle_timeout()
        
        # ========== MANEJAR PAUSA DE RESULTADO ==========
        if self.phase == GamePhase.RESULT_PAUSE:
            elapsed = pygame.time.get_ticks() - self.result_pause_start
            if elapsed >= RESULT_PAUSE_DURATION:
                self.start_countdown_for_next_question()
        
        # ========== ANIMAR POSICIONES DE ROBOTS ==========
        for player_state in [self.player1, self.player2]:
            if player_state.position < player_state.target_position:
                player_state.position += 2
                if player_state.position > player_state.target_position:
                    player_state.position = player_state.target_position
            
            player_state.animation_offset = math.sin(self.animation_time * 0.1) * 3
    
    # ==========================================================================
    #                       MANEJO DE EVENTOS
    # ==========================================================================
  
    def handle_events(self):
        """
        Procesa todos los eventos de entrada del usuario.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                
                # 1. Gestion de la tecla ESC
                if event.key == pygame.K_ESCAPE:
                    if self.phase == GamePhase.MENU:
                        return False
                    else:
                        self.reset_game()
                
                # 2. Teclas solo en el MENU
                if self.phase == GamePhase.MENU:
                    if event.key == pygame.K_a or event.key == pygame.K_d:
                        self.start_game(1)
                    elif event.key == pygame.K_s or event.key == pygame.K_f:
                        self.start_game(2)
                    elif event.key == pygame.K_w or event.key == pygame.K_g:
                        self.start_game(3)
                
                # 3. Teclas solo durante la PREGUNTA
                elif self.phase == GamePhase.QUESTION:
                    # Controles Jugador 1
                    if event.key == pygame.K_a: self.answer_question(1, 0)
                    elif event.key == pygame.K_s: self.answer_question(1, 1)
                    elif event.key == pygame.K_w: self.answer_question(1, 2)
                    
                    # Controles Jugador 2
                    elif event.key == pygame.K_d: self.answer_question(2, 0)
                    elif event.key == pygame.K_f: self.answer_question(2, 1)
                    elif event.key == pygame.K_g: self.answer_question(2, 2)
                
                # 4. Teclas en FIN DE JUEGO
                elif self.phase == GamePhase.FINISHED:
                    if event.key == pygame.K_SPACE:
                        print("[JUEGO] Reiniciando al menu...")
                        self.reset_game()
        
        return True
    
    # ==========================================================================
    #                    FUNCIONES DE DIBUJO (UTILIDADES)
    # ==========================================================================
    
    def draw_rounded_rect(self, surface, color, rect, radius, border=0, border_color=None):
        pygame.draw.rect(surface, color, rect, border_radius=radius)
        if border > 0 and border_color:
            pygame.draw.rect(surface, border_color, rect, border, border_radius=radius)
    
    def draw_robot(self, x, y, size, color, offset=0):
        """
        Dibuja un robot animado con indicadores de 2 motores.
        """
        y += offset
        
        # ========== CUERPO ==========
        body = pygame.Rect(x - size//2, y - size//2, size, size)
        self.draw_rounded_rect(self.screen, color, body, size//4)
        pygame.draw.rect(self.screen, COLORS['text_white'], body, 2, border_radius=size//4)
        
        # ========== OJOS ==========
        eye_size = size // 5
        eye_y = y - size//6
        
        pygame.draw.circle(self.screen, COLORS['background'], 
                          (x - size//4, int(eye_y)), eye_size)
        pygame.draw.circle(self.screen, COLORS['background'], 
                          (x + size//4, int(eye_y)), eye_size)
        
        pupil_offset = math.sin(self.animation_time * 0.05) * 2
        pygame.draw.circle(self.screen, COLORS['text_white'], 
                          (int(x - size//4 + pupil_offset), int(eye_y)), eye_size//2)
        pygame.draw.circle(self.screen, COLORS['text_white'], 
                          (int(x + size//4 + pupil_offset), int(eye_y)), eye_size//2)
        
        # ========== BOCA ==========
        mouth_rect = pygame.Rect(x - size//3, y + size//6, size//1.5, size//6)
        pygame.draw.rect(self.screen, COLORS['background'], mouth_rect, border_radius=3)
        
        # ========== ANTENA ==========
        pygame.draw.line(self.screen, color, 
                        (x, y - size//2), 
                        (x, y - size//2 - size//4), 3)
        pygame.draw.circle(self.screen, COLORS['accent'], 
                          (x, int(y - size//2 - size//4)), 5)
        
        # ========== INDICADORES DE RUEDAS (2 MOTORES) ==========
        # Solo dibujar para robots de tamano >= 50 (no en los pequenitos de pista)
        if size >= 50:
            wheel_size = size // 6
            # Rueda izquierda
            wheel_l = pygame.Rect(x - size//2 - wheel_size//2, y + size//4, wheel_size, wheel_size * 2)
            pygame.draw.rect(self.screen, COLORS['text_gray'], wheel_l, border_radius=3)
            pygame.draw.rect(self.screen, COLORS['text_white'], wheel_l, 1, border_radius=3)
            # Rueda derecha
            wheel_r = pygame.Rect(x + size//2 - wheel_size//2, y + size//4, wheel_size, wheel_size * 2)
            pygame.draw.rect(self.screen, COLORS['text_gray'], wheel_r, border_radius=3)
            pygame.draw.rect(self.screen, COLORS['text_white'], wheel_r, 1, border_radius=3)
    
    # ==========================================================================
    #                         DIBUJAR MENU
    # ==========================================================================
    
    def draw_menu(self):
        """
        Dibuja la pantalla del menu principal con informacion de conexion EV3.
        """
        self.screen.fill(COLORS['background'])
        
        # ========== LOGOS INSTITUCIONALES ==========
        if self.logo_fac:
            self.screen.blit(self.logo_fac, (20, 10))
        
        if self.logo_ingeniotics:
            self.screen.blit(self.logo_ingeniotics, (SCREEN_WIDTH - 170, 25))
        
        # ========== TITULO ==========
        title_text = "ROBOT RACE QUIZ"
        title = self.font_title.render(title_text, True, COLORS['text_white'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)
        
        # ========== SUBTITULO ==========
        subtitle = self.font_small.render(
            "Desarrollado por Octavo Semestre Matematicas Computacional", 
            True, COLORS['accent']
        )
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 120))
        self.screen.blit(subtitle, subtitle_rect)
        
        # ========== ROBOTS DECORATIVOS ANIMADOS (con 2 ruedas cada uno) ==========
        self.draw_robot(150, 200, 70, COLORS['player1'], self.player1.animation_offset)
        self.draw_robot(SCREEN_WIDTH - 150, 200, 70, COLORS['player2'], 
                       -math.sin(self.animation_time * 0.1) * 3)
        
        # ========== ESTADO DE CONEXION EV3 (BLUETOOTH) ==========
        ev3_panel_rect = pygame.Rect(SCREEN_WIDTH // 2 - 380, 148, 760, 40)
        self.draw_rounded_rect(self.screen, COLORS['card'], ev3_panel_rect, 8, 2, COLORS['bluetooth'])
        
        # Icono/texto de Bluetooth
        bt_label = self.font_tiny.render("BLUETOOTH EV3:", True, COLORS['bluetooth'])
        self.screen.blit(bt_label, (SCREEN_WIDTH // 2 - 365, 155))
        
        # Estado Robot 1
        r1_status = "CONECTADO (2 motores)" if ROBOT1_CONNECTED else "SIMULADO"
        r1_color = COLORS['success'] if ROBOT1_CONNECTED else COLORS['accent']
        r1_text = self.font_tiny.render(f"Robot 1 (J1): {r1_status}", True, r1_color)
        self.screen.blit(r1_text, (SCREEN_WIDTH // 2 - 200, 155))
        
        # Estado Robot 2
        r2_status = "CONECTADO (2 motores)" if ROBOT2_CONNECTED else "SIMULADO"
        r2_color = COLORS['success'] if ROBOT2_CONNECTED else COLORS['accent']
        r2_text = self.font_tiny.render(f"Robot 2 (J2): {r2_status}", True, r2_color)
        self.screen.blit(r2_text, (SCREEN_WIDTH // 2 + 100, 155))
        
        # Total motores
        total_motors = (2 if ROBOT1_CONNECTED else 0) + (2 if ROBOT2_CONNECTED else 0)
        motors_text = self.font_tiny.render(f"[{total_motors}/4 motores]", True, COLORS['text_muted'])
        motors_rect = motors_text.get_rect(right=SCREEN_WIDTH // 2 + 370, centery=ev3_panel_rect.centery)
        self.screen.blit(motors_text, motors_rect)
        
        # ========== PANEL DE INSTRUCCIONES ==========
        instr_rect = pygame.Rect(SCREEN_WIDTH // 2 - 380, 195, 760, 100)
        self.draw_rounded_rect(self.screen, COLORS['card'], instr_rect, 12, 2, COLORS['question'])
        
        flow_title = self.font_medium.render("FLUJO DEL JUEGO", True, COLORS['question'])
        flow_title_rect = flow_title.get_rect(center=(SCREEN_WIDTH // 2, 215))
        self.screen.blit(flow_title, flow_title_rect)
        
        flow1 = self.font_tiny.render(
            "1. INTERLUDIO: Cuenta regresiva 3, 2, 1...", 
            True, COLORS['text_gray']
        )
        flow2 = self.font_tiny.render(
            "2. PREGUNTA: 30 segundos - Ambos jugadores pueden intentar (cada robot tiene 2 motores)", 
            True, COLORS['text_gray']
        )
        flow3 = self.font_tiny.render(
            "3. El primero en responder CORRECTAMENTE avanza con su robot EV3!", 
            True, COLORS['text_gray']
        )
        self.screen.blit(flow1, (SCREEN_WIDTH // 2 - 360, 235))
        self.screen.blit(flow2, (SCREEN_WIDTH // 2 - 360, 253))
        self.screen.blit(flow3, (SCREEN_WIDTH // 2 - 360, 271))
        
        # ========== CONTROLES ==========
        ctrl_rect = pygame.Rect(SCREEN_WIDTH // 2 - 380, 305, 760, 50)
        self.draw_rounded_rect(self.screen, COLORS['card'], ctrl_rect, 8, 1, COLORS['border'])
        
        ctrl_text1 = self.font_tiny.render("J1 (Verde) Robot 1: Boton Azul / Rojo / Verde", True, COLORS['player1'])
        ctrl_text2 = self.font_tiny.render("J2 (Naranja) Robot 2: Boton Azul / Rojo / Verde", True, COLORS['player2'])
        self.screen.blit(ctrl_text1, (SCREEN_WIDTH // 2 - 360, 317))
        self.screen.blit(ctrl_text2, (SCREEN_WIDTH // 2 + 20, 317))
        
        # ========== BOTONES DE NIVEL ==========
        levels = [
            ("Azul", "Facil", "Preguntas basicas de matematicas", COLORS['player1']),
            ("Rojo", "Medio", "Conocimiento general y operaciones", COLORS['accent']),
            ("Verde", "Dificil", "Matematicas avanzadas", COLORS['player2']),
        ]
        
        y_start = 370
        for i, (btn_name, name, desc, color) in enumerate(levels):
            btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 220, y_start + i * 95, 440, 80)
            
            mouse_pos = pygame.mouse.get_pos()
            is_hover = btn_rect.collidepoint(mouse_pos)
            
            bg_color = color if is_hover else COLORS['card']
            text_color = COLORS['background'] if is_hover else COLORS['text_white']
            
            self.draw_rounded_rect(self.screen, bg_color, btn_rect, 12, 2, color)
            
            level_text = self.font_medium.render(f"Nivel {i+1}: {name}", True, text_color)
            self.screen.blit(level_text, (btn_rect.x + 20, btn_rect.y + 15))
            
            key_text = self.font_small.render(f"Presiona Boton {btn_name}", True, text_color)
            key_rect = key_text.get_rect(right=btn_rect.right - 20, centery=btn_rect.centery)
            self.screen.blit(key_text, key_rect)
        
        # ========== TEXTO DE COMPATIBILIDAD ==========
        comp_text = self.font_tiny.render(
            "Compatible con: Makey Makey | 2x LEGO EV3 Bluetooth (4 motores) | Teclado estandar", 
            True, COLORS['text_muted']
        )
        comp_rect = comp_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
        self.screen.blit(comp_text, comp_rect)
        
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
        """
        track_title = self.font_medium.render("PISTA DE CARRERA", True, COLORS['text_white'])
        track_title_rect = track_title.get_rect(center=(SCREEN_WIDTH // 2, 85))
        self.screen.blit(track_title, track_title_rect)
        
        track_x = 80
        track_width = SCREEN_WIDTH - 200
        track_height = 40
        segment_count = self.TOTAL_SEGMENTS
        segment_gap = 3
         
        track_y_1 = 115
        track_y_2 = 175
        
        self.draw_player_track(
            track_x, track_y_1, track_width, track_height,
            segment_count, segment_gap,
            self.player1, 1, COLORS['player1']
        )
        
        self.draw_player_track(
            track_x, track_y_2, track_width, track_height,
            segment_count, segment_gap,
            self.player2, 2, COLORS['player2']
        )
        
        # ========== LINEA DE META ==========
        finish_x = track_x + track_width + 20
        meta_rect = pygame.Rect(finish_x, track_y_1 - 10, 12, track_y_2 + track_height - track_y_1 + 20)
        pygame.draw.rect(self.screen, COLORS['finish'], meta_rect, border_radius=4)
        
        meta_text = self.font_medium.render("META", True, COLORS['finish'])
        meta_text_rect = meta_text.get_rect(left=finish_x + 20, centery=(track_y_1 + track_y_2 + track_height) // 2)
        self.screen.blit(meta_text, meta_text_rect)
    
    def draw_player_track(self, x, y, width, height, segments, gap, player_state, player_num, color):
        """
        Dibuja el carril de progreso de un jugador con segmentos.
        Incluye indicador de robot EV3 y sus 2 motores.
        """
        # ========== ETIQUETA DE JUGADOR CON INDICADOR EV3 ==========
        is_connected = ROBOT1_CONNECTED if player_num == 1 else ROBOT2_CONNECTED
        ev3_indicator = " [EV3]" if is_connected else " [SIM]"
        label_color = color
        label_text = self.font_small.render(f"Jugador {player_num}{ev3_indicator}", True, label_color)
        self.screen.blit(label_text, (x - 5, y - 22))
        
        # Indicador de estado de conexion (punto verde/rojo)
        indicator_x = x + label_text.get_width() + 5
        indicator_color = COLORS['success'] if is_connected else COLORS['error']
        pygame.draw.circle(self.screen, indicator_color, (indicator_x, y - 12), 5)
        
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
            
            if i < progress_segments:
                seg_color = color
            else:
                seg_color = COLORS['track_segment']
            
            pygame.draw.rect(self.screen, seg_color, seg_rect, border_radius=4)
        
        # ========== ROBOT EN LA PISTA ==========
        robot_progress_x = x + 30 + (width - 60) * (player_state.position / 100)
        robot_y = y + height // 2
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
        Dibuja la pantalla principal del juego.
        """
        self.screen.fill(COLORS['background'])
        
        self.draw_header()
        self.draw_race_track()
        
        if self.phase == GamePhase.COUNTDOWN:
            self.draw_countdown_phase()
        elif self.phase == GamePhase.QUESTION:
            self.draw_question_phase()
        elif self.phase == GamePhase.RESULT_PAUSE:
            self.draw_result_phase()
        
        self.draw_footer()
    
    def draw_header(self):
        """
        Dibuja el header del juego con titulo, nivel, puntuaciones e info EV3.
        """
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
        
        # Puntuaciones con indicador EV3
        p1_label = "J1"
        p2_label = "J2"
        if ROBOT1_CONNECTED:
            p1_label += "[EV3]"
        if ROBOT2_CONNECTED:
            p2_label += "[EV3]"
        
        p1_score = self.font_small.render(f"{p1_label}: {self.player1.score}", True, COLORS['player1'])
        p2_score = self.font_small.render(f"{p2_label}: {self.player2.score}", True, COLORS['player2'])
        self.screen.blit(p1_score, (SCREEN_WIDTH // 2 - 120, 18))
        self.screen.blit(p2_score, (SCREEN_WIDTH // 2 + 30, 18))
        
        # Numero de pregunta
        q_text = self.font_tiny.render(f"Pregunta {self.questions_answered}", True, COLORS['text_gray'])
        q_rect = q_text.get_rect(right=SCREEN_WIDTH - 120, centery=30)
        self.screen.blit(q_text, q_rect)
        
        # Boton de salir
        exit_text = self.font_tiny.render("ESC: Salir", True, COLORS['text_muted'])
        self.screen.blit(exit_text, (SCREEN_WIDTH - 80, 22))
    
    def draw_footer(self):
        """
        Dibuja el footer con informacion de controles y estado EV3.
        """
        footer_rect = pygame.Rect(40, SCREEN_HEIGHT - 45, SCREEN_WIDTH - 80, 35)
        self.draw_rounded_rect(self.screen, COLORS['card'], footer_rect, 8, 1, COLORS['border'])
        
        if self.phase == GamePhase.COUNTDOWN:
            text = "PREPARATE! Ambos robots EV3 listos..."
        elif self.phase == GamePhase.QUESTION:
            text = "Usa los botones AZUL, ROJO o VERDE para responder - Tu robot EV3 avanzara!"
        else:
            text = "Esperando..."
        
        ctrl_text = self.font_tiny.render(text, True, COLORS['text_muted'])
        ctrl_rect = ctrl_text.get_rect(center=footer_rect.center)
        self.screen.blit(ctrl_text, ctrl_rect)
    
    def draw_countdown_phase(self):
        """
        Dibuja la fase de cuenta regresiva "3, 2, 1".
        """
        pulse = 1.0 + math.sin(self.animation_time * 0.3) * 0.1
        center_y = 400
        
        radius = int(100 * pulse)
        pygame.draw.circle(self.screen, COLORS['countdown'], 
                          (SCREEN_WIDTH // 2, center_y), radius)
        pygame.draw.circle(self.screen, COLORS['text_white'], 
                          (SCREEN_WIDTH // 2, center_y), radius, 4)
        
        number_text = self.font_countdown.render(str(self.countdown_number), True, COLORS['text_white'])
        number_rect = number_text.get_rect(center=(SCREEN_WIDTH // 2, center_y))
        self.screen.blit(number_text, number_rect)
        
        prep_text = self.font_large.render("PREPARATE!", True, COLORS['accent'])
        prep_rect = prep_text.get_rect(center=(SCREEN_WIDTH // 2, 270))
        self.screen.blit(prep_text, prep_rect)
        
        if self.current_question:
            preview_rect = pygame.Rect(100, 520, SCREEN_WIDTH - 200, 80)
            preview_surface = pygame.Surface((preview_rect.width, preview_rect.height))
            preview_surface.fill(COLORS['card'])
            preview_surface.set_alpha(150)
            self.screen.blit(preview_surface, preview_rect)
            
            next_label = self.font_tiny.render("SIGUIENTE PREGUNTA:", True, COLORS['text_muted'])
            next_label_rect = next_label.get_rect(center=(SCREEN_WIDTH // 2, 545))
            self.screen.blit(next_label, next_label_rect)
            
            q_preview = self.current_question.pregunta[:60] + "..." if len(self.current_question.pregunta) > 60 else self.current_question.pregunta
            q_text = self.font_small.render(q_preview, True, COLORS['text_gray'])
            q_rect = q_text.get_rect(center=(SCREEN_WIDTH // 2, 575))
            self.screen.blit(q_text, q_rect)
    
    def draw_question_phase(self):
        """
        Dibuja la fase de pregunta.
        """
        # ========== TEMPORIZADOR ==========
        time_percent = self.question_time_remaining / QUESTION_TIME_LIMIT
        is_low_time = self.question_time_remaining <= 10
        
        timer_panel = pygame.Rect(SCREEN_WIDTH // 2 - 150, 230, 300, 50)
        timer_color = COLORS['error'] if is_low_time else COLORS['question']
        self.draw_rounded_rect(self.screen, timer_color, timer_panel, 12, 3, COLORS['text_white'])
        
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
        Dibuja la fase de resultado.
        """
        if self.round_winner is not None:
            winner_color = COLORS['player1'] if self.round_winner == 1 else COLORS['player2']
            winner_name = "JUGADOR 1" if self.round_winner == 1 else "JUGADOR 2"
            robot_label = "Robot 1" if self.round_winner == 1 else "Robot 2"
            result_text = f"{winner_name} GANA EL PUNTO! ({robot_label} avanza)"
            result_color = winner_color
        elif self.last_answer_correct is None:
            result_text = "TIEMPO AGOTADO!"
            result_color = COLORS['accent']
        else:
            result_text = "NADIE ACERTO"
            result_color = COLORS['error']
        
        result_rect = pygame.Rect(SCREEN_WIDTH // 2 - 280, 240, 560, 80)
        self.draw_rounded_rect(self.screen, result_color, result_rect, 15, 4, COLORS['text_white'])
        
        result_label = self.font_large.render(result_text, True, COLORS['text_white'])
        result_label_rect = result_label.get_rect(center=result_rect.center)
        self.screen.blit(result_label, result_label_rect)
        
        # ========== PREGUNTA CON RESPUESTA CORRECTA ==========
        self.draw_question_panel(340)
        
        if self.current_question:
            correct_text = self.font_medium.render(
                f"Respuesta correcta: {self.current_question.respuesta_correcta}", 
                True, COLORS['success']
            )
            correct_rect = correct_text.get_rect(center=(SCREEN_WIDTH // 2, 540))
            self.screen.blit(correct_text, correct_rect)
        
        # ========== ROBOT CELEBRANDO ==========
        if self.round_winner is not None:
            winner_color = COLORS['player1'] if self.round_winner == 1 else COLORS['player2']
            robot_x = SCREEN_WIDTH // 2
            robot_y = 620
            bounce = abs(math.sin(self.animation_time * 0.2)) * 15
            self.draw_robot(robot_x, int(robot_y - bounce), 50, winner_color, 0)
        
        next_text = self.font_small.render("Siguiente pregunta en unos segundos...", True, COLORS['text_gray'])
        next_rect = next_text.get_rect(center=(SCREEN_WIDTH // 2, 680))
        self.screen.blit(next_text, next_rect)
    
    def draw_question_panel(self, y_pos: int):
        """
        Dibuja el panel con la pregunta actual.
        """
        q_panel_rect = pygame.Rect(60, y_pos, SCREEN_WIDTH - 120, 100)
        self.draw_rounded_rect(self.screen, COLORS['card'], q_panel_rect, 12, 2, COLORS['accent'])
        
        q_label = self.font_tiny.render("PREGUNTA", True, COLORS['accent'])
        q_label_rect = q_label.get_rect(center=(SCREEN_WIDTH // 2, y_pos + 20))
        self.screen.blit(q_label, q_label_rect)
        
        if self.current_question:
            question_text = self.current_question.pregunta
            
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
        Dibuja las opciones de respuesta con etiquetas de color.
        """
        if not self.current_options:
            return
        
        option_width = 320
        option_height = 80
        option_gap = 20
        total_width = option_width * 3 + option_gap * 2
        start_x = (SCREEN_WIDTH - total_width) // 2
        option_y = 440
        
        color_names = ["AZUL", "ROJO", "VERDE"]
        button_colors = [COLORS['question'], COLORS['error'], COLORS['success']]
        
        for i, option in enumerate(self.current_options):
            opt_x = start_x + i * (option_width + option_gap)
            opt_rect = pygame.Rect(opt_x, option_y, option_width, option_height)
            
            self.draw_rounded_rect(self.screen, COLORS['card'], opt_rect, 12, 2, COLORS['border'])
            
            opt_text_str = str(option)[:25] + "..." if len(str(option)) > 25 else str(option)
            opt_text = self.font_medium.render(opt_text_str, True, COLORS['text_white'])
            opt_text_rect = opt_text.get_rect(centerx=opt_rect.centerx, top=opt_rect.y + 12)
            self.screen.blit(opt_text, opt_text_rect)
            
            badge_rect = pygame.Rect(0, 0, 140, 24)
            badge_rect.centerx = opt_rect.centerx
            badge_rect.bottom = opt_rect.bottom - 10
            
            if self.player1.blocked_this_round and self.player2.blocked_this_round:
                current_badge_color = COLORS['track_segment']
            else:
                current_badge_color = button_colors[i]
                
            self.draw_rounded_rect(self.screen, current_badge_color, badge_rect, 6)
            
            color_label = self.font_tiny.render(f"BOTON {color_names[i]}", True, COLORS['background'])
            color_label_rect = color_label.get_rect(center=badge_rect.center)
            self.screen.blit(color_label, color_label_rect)

    def draw_player_status(self):
        """
        Dibuja el estado actual de cada jugador con indicador de robot EV3.
        """
        status_y = 530
        
        # ========== JUGADOR 1 ==========
        p1_rect = pygame.Rect(100, status_y, 250, 40)
        if self.player1.blocked_this_round:
            p1_color = COLORS['error']
            p1_text = "J1 Robot1: BLOQUEADO"
        else:
            p1_color = COLORS['player1']
            p1_text = "J1 Robot1: Puede responder"
        
        self.draw_rounded_rect(self.screen, p1_color, p1_rect, 10, 2, COLORS['text_white'])
        p1_label = self.font_small.render(p1_text, True, COLORS['text_white'])
        p1_label_rect = p1_label.get_rect(center=p1_rect.center)
        self.screen.blit(p1_label, p1_label_rect)
        
        # ========== JUGADOR 2 ==========
        p2_rect = pygame.Rect(SCREEN_WIDTH - 350, status_y, 250, 40)
        if self.player2.blocked_this_round:
            p2_color = COLORS['error']
            p2_text = "J2 Robot2: BLOQUEADO"
        else:
            p2_color = COLORS['player2']
            p2_text = "J2 Robot2: Puede responder"
        
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
        """
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(COLORS['background'])
        overlay.set_alpha(230)
        self.screen.blit(overlay, (0, 0))
        
        panel_rect = pygame.Rect(SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 200, 500, 400)
        self.draw_rounded_rect(self.screen, COLORS['card'], panel_rect, 20, 3, COLORS['accent'])
        
        if self.winner == 0:
            winner_text = "EMPATE!"
            winner_color = COLORS['accent']
        elif self.winner == 1:
            winner_text = "JUGADOR 1 GANA! (Robot 1)"
            winner_color = COLORS['player1']
        else:
            winner_text = "JUGADOR 2 GANA! (Robot 2)"
            winner_color = COLORS['player2']
        
        title = self.font_large.render(winner_text, True, winner_color)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 120))
        self.screen.blit(title, title_rect)
        
        # ========== ROBOT GANADOR (con 2 ruedas) ==========
        if self.winner != 0:
            self.draw_robot(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, 60, winner_color, 
                           int(math.sin(self.animation_time * 0.1) * 5))
        
        # ========== ESTADISTICAS ==========
        stats_text = self.font_small.render(f"Preguntas respondidas: {self.questions_answered}", True, COLORS['text_white'])
        stats_rect = stats_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(stats_text, stats_rect)
        
        # Info de motores usados
        total_motors = (2 if ROBOT1_CONNECTED else 0) + (2 if ROBOT2_CONNECTED else 0)
        motors_info = self.font_tiny.render(
            f"Motores EV3 activos: {total_motors}/4 | 2 robots Bluetooth", 
            True, COLORS['bluetooth']
        )
        motors_rect = motors_info.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 42))
        self.screen.blit(motors_info, motors_rect)
        
        # ========== PANELES DE PUNTUACION ==========
        score_rect_1 = pygame.Rect(panel_rect.x + 30, SCREEN_HEIGHT // 2 + 55, 200, 80)
        score_rect_2 = pygame.Rect(panel_rect.right - 230, SCREEN_HEIGHT // 2 + 55, 200, 80)
        
        # Panel Jugador 1
        p1_bg = COLORS['player1'] if self.winner == 1 else COLORS['card_hover']
        self.draw_rounded_rect(self.screen, p1_bg, score_rect_1, 12, 2, COLORS['player1'])
        
        p1_label = self.font_small.render("Jugador 1 (Robot 1)", True, COLORS['text_gray'])
        p1_label_rect = p1_label.get_rect(centerx=score_rect_1.centerx, top=score_rect_1.y + 8)
        self.screen.blit(p1_label, p1_label_rect)
        
        p1_score = self.font_title.render(str(self.player1.score), True, COLORS['player1'])
        p1_score_rect = p1_score.get_rect(center=(score_rect_1.centerx, score_rect_1.centery + 18))
        self.screen.blit(p1_score, p1_score_rect)
        
        # Panel Jugador 2
        p2_bg = COLORS['player2'] if self.winner == 2 else COLORS['card_hover']
        self.draw_rounded_rect(self.screen, p2_bg, score_rect_2, 12, 2, COLORS['player2'])
        
        p2_label = self.font_small.render("Jugador 2 (Robot 2)", True, COLORS['text_white'])
        p2_label_rect = p2_label.get_rect(centerx=score_rect_2.centerx, top=score_rect_2.y + 8)
        self.screen.blit(p2_label, p2_label_rect)
        
        p2_score = self.font_title.render(str(self.player2.score), True, COLORS['player2'])
        p2_score_rect = p2_score.get_rect(center=(score_rect_2.centerx, score_rect_2.centery + 18))
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
        Funcion principal de renderizado.
        """
        if self.phase == GamePhase.MENU:
            self.draw_menu()
        elif self.phase == GamePhase.FINISHED:
            self.draw_game()
            self.draw_game_over()
        else:
            self.draw_game()
        
        pygame.display.flip()
    
    # ==========================================================================
    #                       BUCLE PRINCIPAL
    # ==========================================================================
    
    def run(self):
        """
        Ejecuta el bucle principal del juego.
        """
        print("\n" + "="*60)
        print("         ROBOT RACE QUIZ v7.0 - DUAL EV3 BLUETOOTH")
        print("       2 Robots EV3 | 4 Motores | Conexion Bluetooth")
        print("="*60)
        print("\nARQUITECTURA DE HARDWARE:")
        print("  Robot 1 (Jugador 1): Motor A (izq) + Motor B (der)")
        print("  Robot 2 (Jugador 2): Motor A (izq) + Motor B (der)")
        print(f"  Total motores activos: {(2 if ROBOT1_CONNECTED else 0) + (2 if ROBOT2_CONNECTED else 0)}/4")
        print("\nControles:")
        print("  INTERLUDIO: Cuenta regresiva 3, 2, 1...")
        print("  PREGUNTA: J1 (A/S/W) | J2 (D/F/G) - 30 segundos")
        print("  El primero en responder CORRECTAMENTE gana!")
        print("  Si respondes MAL quedas bloqueado esa ronda")
        print("  MENU: A/D=Nivel1, S/F=Nivel2, W/G=Nivel3 | ESC para salir")
        print("="*60 + "\n")
        
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        # Detener todos los robots antes de salir
        stop_all_robots()
        
        # Limpiar recursos de Pygame
        pygame.quit()
        print("\n[JUEGO] Robot Race Quiz finalizado. Gracias por jugar!")
        print("[EV3] Todos los motores detenidos.")


# ==============================================================================
#                           PUNTO DE ENTRADA
# ==============================================================================

def main():
    """
    Funcion principal que inicia el juego.
    """
    game = RobotRaceGame()
    game.run()


if __name__ == "__main__":
    main()
