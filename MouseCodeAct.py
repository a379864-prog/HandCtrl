#------------------------------ Importamos las librerias ----------------------------------------
import cv2
import numpy as np
import SeguimientoManos as sm
import autopy
import time
import pyautogui

#---------------------------------Declaracion de variables---------------------------------------
anchocam, altocam = 640, 480
cuadro = 60
#Aumente el tamaño a comparacion de antes (100)
anchopanta, altopanta = autopy.screen.size()
sua = 5
pubix, pubiy = 0, 0
cubix, cubiy = 0, 0

# Variables para zoom
nivel_zoom = 1.0
distancia_inicial_zoom = None
zoom_activo = False
ultimo_nivel_zoom = 1.0

# Variables para scroll
scroll_activo = False
scroll_y_inicial = None

# Variables para evitar clicks múltiples
tiempo_ultimo_click = 0
tiempo_entre_clicks = 0.3

# Variable para pausar - MEJORADO
sistema_pausado = False
tiempo_ultimo_cambio_pausa = 0
cooldown_pausa = 1.0  # 1 segundo entre cambios de pausa
#No lo quise aumentar más para que no pareciera que tarda en despausar y así

# Variable para detectar cambio de gesto
gesto_anterior = None
frames_mismo_gesto = 0

#----------------------------------- Lectura de la camara----------------------------------------
cap = cv2.VideoCapture(0)
cap.set(3, anchocam)
cap.set(4, altocam)

#------------------------------------ Declaramos el detector -----------------------------
detector = sm.detectormanos(maxManos=1)

print("=== SISTEMA DE CONTROL POR GESTOS ===")
print("1. Solo INDICE = Mover cursor")
print("2. INDICE + CORAZON juntos = Click")
print("3. INDICE + MENIQUE = Zoom")
print("   - SEPARAR dedos = Zoom IN (agrandar)")
print("   - JUNTAR dedos = Zoom OUT (achicar)")
print("4. INDICE + CORAZON + ANULAR = Scroll")
print("5. PUNIO CERRADO = Pausar/Reanudar")
print("Presiona ESC para salir\n")

while True:
    ret, frame = cap.read()
    #frame = cv2.flip(frame, 1) Esto era lo del espejo
    frame = detector.encontrarmanos(frame)
    lista, bbox = detector.encontrarposicion(frame, dibujar=False)

    # Dibujar área de control
    cv2.rectangle(frame, (cuadro, cuadro), (anchocam - cuadro, altocam - cuadro), (255, 0, 255), 2)
    
    # Estado del sistema
    estado_texto = "PAUSADO" if sistema_pausado else "ACTIVO"
    color_estado = (0, 0, 255) if sistema_pausado else (0, 255, 0)
    cv2.putText(frame, f'Estado: {estado_texto}', (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_estado, 2)

    if len(lista) != 0:
        x1, y1 = lista[8][1:]  # Índice
        x2, y2 = lista[12][1:]  # Corazón
        x_pulgar, y_pulgar = lista[4][1:]  # Pulgar
        x_anular, y_anular = lista[16][1:]  # Anular

        dedos = detector.dedosarriba()
        
        # ====== DEBUG: Mostrar dedos detectados ======
        nombres_dedos = ['Pulgar', 'Indice', 'Corazon', 'Anular', 'Menique']
        for i, (nombre, estado) in enumerate(zip(nombres_dedos, dedos)):
            color = (0, 255, 0) if estado == 1 else (0, 0, 255)
            cv2.putText(frame, f'{nombre}: {estado}', (400, 50 + i*25), 
                       cv2.FONT_HERSHEY_PLAIN, 1.2, color, 2)
        
        # Identificar gesto actual
        gesto_actual = tuple(dedos)
        
        # Contar frames con el mismo gesto (para estabilidad)
        if gesto_actual == gesto_anterior:
            frames_mismo_gesto += 1
        else:
            frames_mismo_gesto = 0
            gesto_anterior = gesto_actual
        
        # ======================= GESTO 5: PUÑO CERRADO - PAUSAR/REANUDAR =======================
        if dedos == [0, 0, 0, 0, 0] and frames_mismo_gesto > 10:  # Requiere 10 frames estables
            tiempo_actual = time.time()
            if tiempo_actual - tiempo_ultimo_cambio_pausa > cooldown_pausa:
                cv2.putText(frame, 'CAMBIO DE PAUSA!', (100, 240), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 165, 255), 3)
                sistema_pausado = not sistema_pausado
                tiempo_ultimo_cambio_pausa = tiempo_actual
                frames_mismo_gesto = 0  # Reset para evitar múltiples cambios
                print(f"Sistema {'PAUSADO' if sistema_pausado else 'REANUDADO'}")
        
        # Si el sistema está pausado, no procesar otros gestos
        if sistema_pausado:
            cv2.putText(frame, 'Sistema en pausa - Cierra puño para reanudar', (50, 240), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            cv2.imshow("Control por Gestos", frame)
            if cv2.waitKey(1) == 27:
                break
            continue

        # ======================= GESTO 1: SOLO ÍNDICE - MOVER CURSOR =======================
        if dedos[1] == 1 and dedos[2] == 0 and dedos[0] == 0:
            cv2.putText(frame, 'Modo: MOVER', (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            x3 = np.interp(x1, (cuadro, anchocam - cuadro), (0, anchopanta))
            y3 = np.interp(y1, (cuadro, altocam - cuadro), (0, altopanta))

            cubix = pubix + (x3 - pubix) / sua
            cubiy = pubiy + (y3 - pubiy) / sua

            autopy.mouse.move(anchopanta - cubix, cubiy) ##Esto mantiene la inversión del mouse
            cv2.circle(frame, (x1, y1), 15, (255, 255, 0), cv2.FILLED)
            pubix, pubiy = cubix, cubiy
            
            zoom_activo = False
            scroll_activo = False

        # ======================= GESTO 2: ÍNDICE + CORAZÓN - CLICK =======================
        elif dedos[1] == 1 and dedos[2] == 1 and dedos[3] == 0 and dedos[0] == 0:
            longitud, frame, linea = detector.distancia(8, 12, frame)
            cv2.putText(frame, 'Modo: CLICK', (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            if longitud < 40:
                tiempo_actual = time.time()
                if tiempo_actual - tiempo_ultimo_click > tiempo_entre_clicks:
                    cv2.circle(frame, (linea[4], linea[5]), 15, (0, 255, 0), cv2.FILLED)
                    autopy.mouse.click()
                    tiempo_ultimo_click = tiempo_actual
                    print("Click realizado!")
            
            zoom_activo = False
            scroll_activo = False

        # ======================= GESTO 3: INDICE + MEÑIQUE - ZOOM =======================
        # CAMBIO: Usamos índice (8) + meñique (20) porque es más confiable que el pulgar
        elif dedos[1] == 1 and dedos[4] == 1 and dedos[2] == 0 and dedos[3] == 0:
            distancia_zoom, frame, linea = detector.distancia(8, 20, frame)
            
            cv2.putText(frame, 'Modo: ZOOM', (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
            cv2.putText(frame, 'SEPARAR dedos = Zoom IN', (10, 130), 
                       cv2.FONT_HERSHEY_PLAIN, 1.2, (255, 255, 255), 1)
            cv2.putText(frame, 'JUNTAR dedos = Zoom OUT', (10, 150), 
                       cv2.FONT_HERSHEY_PLAIN, 1.2, (255, 255, 255), 1)
            
            if not zoom_activo:
                distancia_inicial_zoom = distancia_zoom
                zoom_activo = True
            
            # Rango más amplio: 50-400 px para mejor control
            nivel_zoom = np.interp(distancia_zoom, (50, 400), (0.5, 3.0))
            nivel_zoom = max(0.5, min(nivel_zoom, 3.0))
            
            cv2.putText(frame, f'Zoom: {nivel_zoom:.2f}x | Distancia: {distancia_zoom:.0f}px', (10, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
            
            # ===== ZOOM MEJORADO: Más sensible y con indicadores claros =====
            if abs(nivel_zoom - ultimo_nivel_zoom) > 0.08:  # Más sensible
                if nivel_zoom > ultimo_nivel_zoom:
                    pyautogui.hotkey('ctrl', '=')  # Zoom in (Ctrl + =)
                    cv2.putText(frame, '>>> ZOOM IN <<<', (180, 70), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    print(f"ZOOM IN: {nivel_zoom:.2f}x (distancia: {distancia_zoom:.0f}px)")
                else:
                    pyautogui.hotkey('ctrl', '-')  # Zoom out (Ctrl + -)
                    cv2.putText(frame, '<<< ZOOM OUT >>>', (180, 70), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                    print(f"ZOOM OUT: {nivel_zoom:.2f}x (distancia: {distancia_zoom:.0f}px)")
                ultimo_nivel_zoom = nivel_zoom
            
            # Indicador visual mejorado
            if 0.95 < nivel_zoom < 1.05:
                color_indicador = (0, 255, 0)  # Verde = zoom neutral (1x)
                cv2.putText(frame, 'NEUTRAL 1x', (180, 100), 
                           cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0), 2)
            else:
                color_indicador = (255, 0, 255)  # Magenta = zoom activo
            
            cv2.circle(frame, (linea[4], linea[5]), 15, color_indicador, cv2.FILLED)
            
            scroll_activo = False

        # ======================= GESTO 4: 3 DEDOS - SCROLL =======================
        elif dedos[1] == 1 and dedos[2] == 1 and dedos[3] == 1 and dedos[0] == 0:
            cv2.putText(frame, 'Modo: SCROLL', (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            # ===== CORREGIDO: Orden correcto del código =====
            if not scroll_activo:
                scroll_y_inicial = y1
                scroll_activo = True
            
            # Calcular desplazamiento PRIMERO
            diferencia_y = scroll_y_inicial - y1
            
            if abs(diferencia_y) > 20:  # Umbral para activar scroll
                if diferencia_y > 0:
                    cv2.putText(frame, 'SCROLL UP', (200, 70), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    pyautogui.scroll(3)  # Scroll hacia arriba
                else:
                    cv2.putText(frame, 'SCROLL DOWN', (200, 70), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    pyautogui.scroll(-3)  # Scroll hacia abajo
                
                scroll_y_inicial = y1  # Actualizar posición base
            
            cv2.circle(frame, (x1, y1), 15, (0, 255, 255), cv2.FILLED)
            zoom_activo = False

        # ======================= OTROS GESTOS - RESETEAR =======================
        else:
            zoom_activo = False
            scroll_activo = False
            cv2.putText(frame, 'Modo: ESPERANDO', (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (128, 128, 128), 2)

    # Mostrar gestos detectados
    if len(lista) != 0:
        dedos = detector.dedosarriba()
        cv2.putText(frame, f'Gesto: {dedos}', (10, altocam - 20), 
                   cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), 2)

    cv2.imshow("Control por Gestos", frame)
    
    k = cv2.waitKey(1)
    if k == 27:
        break

cap.release()
cv2.destroyAllWindows()
print("\n¡Sistema cerrado correctamente!")