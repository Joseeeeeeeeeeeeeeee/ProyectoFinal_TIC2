import sys
from PyQt6.QtWidgets import QApplication, QLabel, QDialog, QMessageBox, QWidget
from PyQt6 import uic
from PyQt6.QtCore import QTimer, Qt
import random
import serial

class inicio(QWidget):
    def __init__(self, window=None, *args, **kwargs):
        super(inicio, self).__init__(*args, **kwargs)
        self.window = window
        uic.loadUi("menu_5.ui", self)
        self.start.clicked.connect(self.on_button_click)
        
    def on_button_click(self):
        self.close()
        self.window.show()
        self.window.tiempo.start(15)

class Perdiste(QWidget):
    def __init__(self, ventana=None, *args, **kwargs):
        super().__init__(ventana, *args, **kwargs)
        self.ventana = ventana
        uic.loadUi("perdiste.ui", self)
        self.retry.clicked.connect(self.reintentar)
        self.cancelar.clicked.connect(self.salir)
    
    def reintentar(self):
        self.close()
        self.window = FlappyBird()
        self.window.show()
        self.window.tiempo.start(15)
    
    def salir(self):
        self.close()

class FlappyBird(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("flpapy2.ui", self)
        self.tiempo = QTimer(self)
        self.tiempo.timeout.connect(self.mov_tubo_arriba)
        self.tiempo.timeout.connect(self.mov_tubo_abajo)

        self.espacio_inicial = 314
        self.x_inicial = 938
        self.limite_superior = 10
        self.limite_inferior = 10
        self.modificar_alturas_tubos()

        #self.tiempo.start(10) #mientras mas pequeño sea el numero, mas veloz se moveran los tubos. Lo ideal es 10

        self.velocidad_gravedad = 2
        self.velocidad_subida = -20
        self.velocidad_pajaro = 0

        self.serial_port= serial.Serial('COM3',9600)
        self.serial_timer = QTimer()
        self.serial_timer.timeout.connect(self.read_serial)
        self.serial_timer.start(10)  # Leer del puerto serie cada 10 ms

        self.pajaro_timer = QTimer(self)
        self.pajaro_timer.timeout.connect(self.actualizar_pajaro)
        self.pajaro_timer.start(30)

        self.score = 0
        self.tubo_pasado = False

    def modificar_alturas_tubos(self):
        window_height = self.height()
        
       # Altura aleatoria para el tubo superior
        altura_arriba = random.randint(self.limite_superior, window_height - (self.espacio_inicial + self.limite_inferior))
        
        
#       # Calcular la altura del espacio entre los tubos
        espacio = self.espacio_inicial
#        
#        # Calcular la altura del tubo inferior en función del espacio y la altura del tubo superior
        altura_abajo = window_height - altura_arriba - espacio
        print("Alturas Finales: {},{}".format(altura_arriba, altura_abajo))
#        
#        # Aplicar las geometrías
        self.Tubo_Arriba.setGeometry(self.x_inicial, 0, self.Tubo_Arriba.width(), altura_arriba)
        self.Tubo_Abajo.setGeometry(self.x_inicial, altura_arriba + espacio, self.Tubo_Abajo.width(), altura_abajo)

        self.tubo_pasado = False

    def mov_tubo_arriba(self):
        tubo_x = self.Tubo_Arriba.x()
        tubo_y = self.Tubo_Arriba.y()

        nuevo_tubo_x = tubo_x - 5  #se mueve 5 pixeles para la izquierda en cada frame
        
        if nuevo_tubo_x < -self.Tubo_Arriba.width(): #si el tubo se sale de la pantalla, reiniciar su posición
            self.modificar_alturas_tubos()
        else:
            self.Tubo_Arriba.setGeometry(nuevo_tubo_x, tubo_y, self.Tubo_Arriba.width(), self.Tubo_Arriba.height())#se actualiza la posición del tubo

    def mov_tubo_abajo(self):
        tubo_x = self.Tubo_Abajo.x()
        tubo_y = self.Tubo_Abajo.y()

        nuevo_tubo_x = tubo_x - 5 
        
        if nuevo_tubo_x < -self.Tubo_Abajo.width():
            self.modificar_alturas_tubos()
        else:
            self.Tubo_Abajo.setGeometry(nuevo_tubo_x, tubo_y, self.Tubo_Abajo.width(), self.Tubo_Abajo.height())
        
    def actualizar_pajaro(self):
        pajaro_x = self.pajaro.x()
        pajaro_y = self.pajaro.y()

        self.velocidad_pajaro += self.velocidad_gravedad #aplicar gravedad
        nuevo_pajaro_y = pajaro_y + self.velocidad_pajaro

        if nuevo_pajaro_y < 0: #limitar el movimiento dentro de la ventana
            nuevo_pajaro_y = 0
            self.velocidad_pajaro = 0

        elif nuevo_pajaro_y > self.height() - self.pajaro.height():
            nuevo_pajaro_y = self.height() - self.pajaro.height()
            self.velocidad_pajaro = 0

        self.pajaro.move(pajaro_x, nuevo_pajaro_y)

        if self.colusion(self.pajaro, self.Tubo_Arriba) or self.colusion(self.pajaro, self.Tubo_Abajo):
            self.show_game_over() #perder

        if self.Tubo_Arriba.x() + self.Tubo_Arriba.width() < pajaro_x and not self.tubo_pasado:
            self.incrementar_puntuacion()
            self.tubo_pasado = True

    def incrementar_puntuacion(self):
        self.score += 1
        self.lcdNumber.display(self.score)
        self.reducir_tiempo_timer()

    def reducir_tiempo_timer(self):
        interval = self.tiempo.interval() - 0.005 #mientras mas chico sea el numero (0.005), la velocidad aumentará mas lento entre tubo y tubo
        if interval > 0:
            self.tiempo.setInterval(int(interval))

    def colusion(self, label1, label2):
        return label1.geometry().intersects(label2.geometry())
    
    def show_game_over(self):
        self.serial_timer.stop()
        self.serial_port.close()
        self.tiempo.stop()
        self.pajaro_timer.stop()
        self.close()
        loose.show()
        
    def read_serial(self):  #arduino
        if self.serial_port.in_waiting > 0:
            data = self.serial_port.readline().decode('utf-8').strip()
            print (data)
            if data == 'FLAP':
                self.velocidad_pajaro = self.velocidad_subida

if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = FlappyBird()
    loose = Perdiste()
    menu = inicio(window=game)
    menu.show()
    #game.show()
    app.exec()
