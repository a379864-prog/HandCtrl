# -*- coding: utf-8 -*-
import sys

# --- VERIFICACIÓN DE VERSIÓN ---
if sys.version_info[0] < 3:
    print("Error: Necesitas Python 3.")
    exit()

import cv2
import numpy as np
import SeguimientoManos as sm
import time
import pyautogui
import os
import webbrowser
import tkinter as tk

# Configuración para máxima velocidad de respuesta
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

# --- CONFIGURACIÓN DEL HUD ---
HUD_WIDTH, HUD_HEIGHT = 300, 100
HUD_WINDOW_NAME = "MediHand Status"
#---------------------------------


# ============= CLASE VENTANA DE ESTADO (OVERLAY) =============
class VentanaEstado:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MediHand Status")
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.95)

        ancho_ventana = 250
        alto_ventana = 150
        ancho_pantalla = self.root.winfo_screenwidth()
        pos_x = ancho_pantalla - ancho_ventana - 20
        pos_y = 50

        self.root.geometry(f'{ancho_ventana}x{alto_ventana}+{pos_x}+{pos_y}')
        self.root.configure(bg='#2b2b2b')

        frame = tk.Frame(self.root, bg='#2b2b2b', padx=10, pady=10)
        frame.pack(fill='both', expand=True)

        self.titulo = tk.Label(frame, text="CONTROL POR GESTOS",
                               font=('Arial', 10, 'bold'), fg='#00ffff', bg='#2b2b2b')
        self.titulo.pack()

        tk.Frame(frame, height=2, bg='#00ffff').pack(fill='x', pady=5)

        self.label_estado = tk.Label(frame, text="Estado: ACTIVO",
                                     font=('Arial', 11, 'bold'), fg='#00ff00', bg='#2b2b2b')
        self.label_estado.pack(anchor='w')

        self.label_modo = tk.Label(frame, text="Modo: ESPERANDO",
                                   font=('Arial', 10), fg='#ffffff', bg='#2b2b2b')
        self.label_modo.pack(anchor='w', pady=2)

        self.label_info = tk.Label(frame, text="", font=('Arial', 9),
                                   fg='#aaaaaa', bg='#2b2b2b')
        self.label_info.pack(anchor='w')

        self.label_evento = tk.Label(frame, text="", font=('Arial', 9, 'italic'),
                                     fg='#ffff00', bg='#2b2b2b')
        self.label_evento.pack(anchor='w', pady=5)

        self.activa = True
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar)

    def actualizar_estado(self, pausado):
        if pausado:
            self.label_estado.config(text="Estado: PAUSADO", fg='#ff4444')
        else:
            self.label_estado.config(text="Estado: ACTIVO", fg='#00ff00')

    def actualizar_modo(self, modo):
        colores = {
            'MOVER': '#ffff00', 'CLICK': '#00ff00', 'ZOOM': '#ff00ff',
            'SCROLL': '#00ffff', 'PAUSA': '#ff6600', 'ESPERANDO': '#888888'
        }
        self.label_modo.config(text=f"Modo: {modo}", fg=colores.get(modo, '#ffffff'))

    def actualizar_info(self, texto):
        self.label_info.config(text=texto)

    def mostrar_evento(self, evento):
        self.label_evento.config(text=evento)
        self.root.after(1500, lambda: self.label_evento.config(text=""))

    def cerrar(self):
        self.activa = False
        self.root.destroy()

    def actualizar(self):
        if self.activa:
            try:
                self.root.update_idletasks()
                self.root.update()
            except tk.TclError:
                self.activa = False


# ============= FUNCIONES DE GESTIÓN DE VENTANA =============
ventana_estado = None

def iniciar_ventana_estado():
    global ventana_estado
    ventana_estado = VentanaEstado()


#======================== PANTALLA DE BIENVENIDA (IMAGEN) ========================
def mostrar_bienvenida_animada():
    directorio_base = os.path.dirname(os.path.abspath(__file__))
    nombre_archivo = "Instrucciones Videohand control2.png"
    ruta_imagen = os.path.join(directorio_base, nombre_archivo)

    img_instrucciones = cv2.imread(ruta_imagen)

    if img_instrucciones is not None:
        print(f"Imagen cargada correctamente desde: {ruta_imagen}")
        h, w, _ = img_instrucciones.shape
        aspect_ratio = h / w
        nuevo_ancho = 400
        nuevo_alto = int(nuevo_ancho * aspect_ratio)
        img_instrucciones = cv2.resize(img_instrucciones, (nuevo_ancho, nuevo_alto))

        titulo_ventana = 'Bienvenida - MediHand Control. Presiona ESPACIO para iniciar'

        while True:
            cv2.imshow(titulo_ventana, img_instrucciones)
            tecla = cv2.waitKey(1) & 0xFF

            if tecla == 32:  # ESPACIO
                print("Iniciando sistema de control por gestos...")
                cv2.destroyWindow(titulo_ventana)

                

                
                try:
                    print(" Cargando modelo en Meshmixer...")
                    
                    # 1. Ruta del archivo que quieres abrir (ejemplo: .mix o .stl)
                    # REEMPLAZA ESTA RUTA por la ubicación real de tu archivo
                    ruta_archivo_3d = r"C:\Users\pauli\Downloads\Segmentation_Segment_1\Feto1.mix"
                    
                    # 2. Abrir el archivo directamente
                    # Windows detectará que debe abrirlo con Meshmixer
                    os.startfile(ruta_archivo_3d)
                    
                    print(f" Archivo {os.path.basename(ruta_archivo_3d)} cargado.")
                    print(" Sistema listo para manipulación 3D")
                except Exception as error_app:
                    print(f" Error al intentar abrir el archivo: {error_app}")
                return True

            elif tecla == 27:  # ESC
                print("Sistema médico cerrado por el usuario")
                cv2.destroyAllWindows()
                return False
    else:
        print(f"ALERTA: No se encontró la imagen en: {ruta_imagen}")
        print("Usando interfaz por defecto.")

        ancho, alto = 800, 600
        pantalla = np.zeros((alto, ancho, 3), dtype=np.uint8)
        pantalla[:] = (40, 40, 40)

        cv2.putText(pantalla, 'SISTEMA DE CONTROL', (150, 200),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 255), 4)
        cv2.putText(pantalla, 'Presiona ESPACIO para iniciar', (180, 500),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        while True:
            cv2.imshow('Bienvenida', pantalla)
            tecla = cv2.waitKey(1) & 0xFF
            if tecla == 32: return True
            elif tecla == 27: return False


#======================== INICIALIZACIÓN ========================
if not mostrar_bienvenida_animada():
    exit()

iniciar_ventana_estado()
print("Iniciando cámara...")

# Variables de configuración
ANCHO_CAM, ALTO_CAM = 640, 480
CUADRO = 70
ANCHO_PANTA, ALTO_PANTA = pyautogui.size()
SUAVIZADO = 5

cv2.namedWindow("Control por Gestos")
cv2.moveWindow("Control por Gestos", 20, 20)

# Variables de control
pubix, pubiy = 0, 0
cubix, cubiy = 0, 0

# Zoom
distancia_zoom_anterior = 0

# Clicks
tiempo_ultimo_click = 0
TIEMPO_ENTRE_CLICKS = 0.6

# Pausa
sistema_pausado = False
tiempo_ultimo_cambio_pausa = 0
COOLDOWN_PAUSA = 1.0

# Estabilidad de gesto pausa
gesto_anterior = None
frames_mismo_gesto = 0

# -- VARIABLE PARA ESTABILIDAD MOVER/ZOOM --
modo_actual = "MOVER"

# ==== FILTRO PARA EVITAR ZOOM ACCIDENTAL ====
frames_para_cambiar_modo = 0
FRAMES_ENTRAR_ZOOM = 6
FRAMES_SALIR_ZOOM = 6
DIST_ENTRAR_ZOOM = 85
DIST_SALIR_ZOOM = 55

# cooldown para zoom
ultimo_zoom_accion = 0
COOLDOWN_ZOOM = 0.15


# ==== SCROLL PROPORCIONAL CON ACELERACIÓN ====
scroll_anchor_y = None
ultimo_scroll_accion = 0
COOLDOWN_SCROLL = 0.06

DEADZONE_SCROLL = 18
MAX_SCROLL_STEP = 300
MIN_SCROLL_STEP = 30

MAX_DIST_SCROLL = 220   # distancia máxima considerada (px)
SCROLL_GAMMA = 1.6      # >1 = acelera (curva), 1 = lineal


#======================== INICIAR CÁMARA ========================
cap = cv2.VideoCapture(0)
cap.set(3, ANCHO_CAM)
cap.set(4, ALTO_CAM)

detector = sm.detectormanos(maxManos=1)

while True:
    if not ventana_estado.activa:
        break

    ret, frame = cap.read()
    if not ret:
        break

    frame = detector.encontrarmanos(frame)
    lista, bbox = detector.encontrarposicion(frame, dibujar=False)

    modo_texto_actual = "ESPERANDO"

    cv2.rectangle(frame, (CUADRO, CUADRO), (ANCHO_CAM - CUADRO, ALTO_CAM - CUADRO),
                  (255, 0, 255), 2)

    color_estado = (0, 0, 255) if sistema_pausado else (0, 255, 0)
    estado_txt = "PAUSADO" if sistema_pausado else "ACTIVO"
    cv2.putText(frame, f'Estado: {estado_txt}', (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_estado, 2)

    ventana_estado.actualizar_estado(sistema_pausado)

    if len(lista) != 0:
        x_indice, y_indice = lista[8][1:]
        dedos = detector.dedosarriba()

        # --- 1. GESTIÓN DE PAUSA ---
        gesto_actual = tuple(dedos)
        if gesto_actual == gesto_anterior:
            frames_mismo_gesto += 1
        else:
            frames_mismo_gesto = 0
            gesto_anterior = gesto_actual

        if dedos == [0, 0, 0, 0, 0] and frames_mismo_gesto > 15:
            tiempo_actual = time.time()
            if tiempo_actual - tiempo_ultimo_cambio_pausa > COOLDOWN_PAUSA:
                sistema_pausado = not sistema_pausado
                tiempo_ultimo_cambio_pausa = tiempo_actual
                frames_mismo_gesto = 0
                ventana_estado.mostrar_evento("Sistema PAUSADO" if sistema_pausado else "Sistema REANUDADO")

        if sistema_pausado:
            cv2.putText(frame, 'PAUSA', (250, 240),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
            modo_texto_actual = "PAUSA"
            ventana_estado.actualizar_modo(modo_texto_actual)
            cv2.imshow("Control por Gestos", frame)
            ventana_estado.actualizar()
            if cv2.waitKey(1) == 27:
                break
            continue

        # --- 2. ZONA UNIFICADA (MOVER vs ZOOM) ---
        if dedos[1] == 1 and dedos[2] == 0 and dedos[3] == 0 and dedos[4] == 0:

            distancia_pulgar_indice, frame, linea = detector.distancia(4, 8, frame)

            if modo_actual == "MOVER":
                if distancia_pulgar_indice > DIST_ENTRAR_ZOOM:
                    frames_para_cambiar_modo += 1
                else:
                    frames_para_cambiar_modo = 0

                if frames_para_cambiar_modo >= FRAMES_ENTRAR_ZOOM:
                    modo_actual = "ZOOM"
                    frames_para_cambiar_modo = 0
                    distancia_zoom_anterior = distancia_pulgar_indice
                    ventana_estado.mostrar_evento("Entró a ZOOM")

            elif modo_actual == "ZOOM":
                if distancia_pulgar_indice < DIST_SALIR_ZOOM:
                    frames_para_cambiar_modo += 1
                else:
                    frames_para_cambiar_modo = 0

                if frames_para_cambiar_modo >= FRAMES_SALIR_ZOOM:
                    modo_actual = "MOVER"
                    frames_para_cambiar_modo = 0
                    distancia_zoom_anterior = 0
                    ventana_estado.mostrar_evento("Entró a MOVER")

            if modo_actual == "ZOOM":
                cv2.putText(frame, 'ZOOM (L)', (10, 70),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
                modo_texto_actual = "ZOOM"

                if distancia_zoom_anterior == 0:
                    distancia_zoom_anterior = distancia_pulgar_indice

                umbral_cambio = 6
                ahora = time.time()

                if abs(distancia_pulgar_indice - distancia_zoom_anterior) > umbral_cambio and (ahora - ultimo_zoom_accion) > COOLDOWN_ZOOM:
                    pyautogui.keyDown('ctrl')
                    if distancia_pulgar_indice > distancia_zoom_anterior:
                        pyautogui.scroll(120)
                        ventana_estado.mostrar_evento("Zoom IN")
                    else:
                        pyautogui.scroll(-120)
                        ventana_estado.mostrar_evento("Zoom OUT")
                    pyautogui.keyUp('ctrl')

                    ultimo_zoom_accion = ahora
                    distancia_zoom_anterior = distancia_pulgar_indice

                scroll_anchor_y = None
                ventana_estado.actualizar_info(f"Distancia: {distancia_pulgar_indice:.0f}px")

            else:
                cv2.putText(frame, 'MOVER', (10, 70),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                modo_texto_actual = "MOVER"

                x3 = np.interp(x_indice, (CUADRO, ANCHO_CAM - CUADRO), (0, ANCHO_PANTA))
                y3 = np.interp(y_indice, (CUADRO, ALTO_CAM - CUADRO), (0, ALTO_PANTA))

                cubix = pubix + (x3 - pubix) / SUAVIZADO
                cubiy = pubiy + (y3 - pubiy) / SUAVIZADO

                try:
                    pyautogui.moveTo(ANCHO_PANTA - cubix, cubiy)
                except:
                    pass

                cv2.circle(frame, (x_indice, y_indice), 15, (255, 255, 0), cv2.FILLED)
                pubix, pubiy = cubix, cubiy

                distancia_zoom_anterior = 0
                scroll_anchor_y = None
                ventana_estado.actualizar_info(f"Cursor: ({cubix:.0f}, {cubiy:.0f})")

        # --- 3. CLICK IZQUIERDO (Índice + Medio) ---
        elif dedos[1] == 1 and dedos[2] == 1 and dedos[3] == 0 and dedos[4] == 0 and dedos[0] == 0:
            longitud, frame, linea = detector.distancia(8, 12, frame)
            cv2.putText(frame, 'CLICK', (10, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            modo_texto_actual = "CLICK"

            if longitud < 40:
                tiempo_actual = time.time()
                if tiempo_actual - tiempo_ultimo_click > TIEMPO_ENTRE_CLICKS:
                    pyautogui.click()
                    tiempo_ultimo_click = tiempo_actual
                    ventana_estado.mostrar_evento("Click!")

            distancia_zoom_anterior = 0
            modo_actual = "MOVER"
            frames_para_cambiar_modo = 0
            scroll_anchor_y = None
            ventana_estado.actualizar_info("")

        # --- 4. SCROLL CON ACELERACIÓN (3 dedos) ---
        elif dedos[1] == 1 and dedos[2] == 1 and dedos[3] == 1 and dedos[0] == 0:
            cv2.putText(frame, 'SCROLL', (10, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            modo_texto_actual = "SCROLL"

            # Fija neutro al entrar
            if scroll_anchor_y is None:
                scroll_anchor_y = y_indice
                ultimo_scroll_accion = time.time()
                ventana_estado.mostrar_evento("Scroll activado")

            delta = scroll_anchor_y - y_indice  # + => UP, - => DOWN
            d = abs(delta)

            if d <= DEADZONE_SCROLL:
                ventana_estado.actualizar_info("Scroll neutro")
            else:
                # ===== ACELERACIÓN NO LINEAL =====
                # normaliza distancia (0..1)
                norm = (d - DEADZONE_SCROLL) / float(MAX_DIST_SCROLL)
                norm = max(0.0, min(1.0, norm))

                # curva con potencia (gamma)
                norm_curve = norm ** SCROLL_GAMMA

                # magnitud final
                magnitud = int(MIN_SCROLL_STEP + (MAX_SCROLL_STEP - MIN_SCROLL_STEP) * norm_curve)

                ahora = time.time()
                if (ahora - ultimo_scroll_accion) >= COOLDOWN_SCROLL:
                    if delta > 0:
                        pyautogui.scroll(magnitud)
                        ventana_estado.mostrar_evento(f"Scroll UP ({magnitud})")
                    else:
                        pyautogui.scroll(-magnitud)
                        ventana_estado.mostrar_evento(f"Scroll DOWN ({magnitud})")

                    ultimo_scroll_accion = ahora

                ventana_estado.actualizar_info(f"ΔY={delta:.0f}px | vel={magnitud}")

            cv2.circle(frame, (x_indice, y_indice), 15, (0, 255, 255), cv2.FILLED)
            distancia_zoom_anterior = 0
            modo_actual = "MOVER"

        # --- 5. OTROS GESTOS ---
        else:
            distancia_zoom_anterior = 0
            frames_para_cambiar_modo = 0
            scroll_anchor_y = None

            if modo_actual != "PAUSA":
                modo_texto_actual = modo_actual

            cv2.putText(frame, 'ESPERANDO', (10, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (128, 128, 128), 2)
            ventana_estado.actualizar_info("Coloca tu mano")

    ventana_estado.actualizar_modo(modo_texto_actual)
    ventana_estado.actualizar()

    cv2.imshow("Control por Gestos", frame)
    if cv2.waitKey(1) == 27:
        break

# --- LIMPIEZA FINAL ---
cap.release()
cv2.destroyAllWindows()
ventana_estado.cerrar()
print("\nSistema cerrado correctamente!")

