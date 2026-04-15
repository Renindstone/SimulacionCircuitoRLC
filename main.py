import sys
from PyQt6.QtWidgets import QApplication
from controlador import ControladorRLC

def main():
    # 1. Toda aplicación PyQt necesita una instancia de QApplication
    app = QApplication(sys.argv)
    
    # 2. Instanciamos el controlador (el cual construirá la Vista y el Modelo)
    controlador = ControladorRLC()
    
    # 3. Mostramos la ventana principal que el controlador maneja
    controlador.vista.show()
    
    # 4. Iniciamos el bucle de eventos de la aplicación
    sys.exit(app.exec())

if __name__ == "__main__":
    main()