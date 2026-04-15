"""
controlador.py — Controlador de la simulación RLC (PyQt6 + Animación)
=====================================================================
"""

import numpy as np
from PyQt6.QtCore import QTimer
from modelo import DEFAULTS, calcular, calcular_bode

class ControladorRLC:
    def __init__(self):
        # 1. Importamos la Vista aquí para evitar importaciones circulares
        from vista import VistaRLC
        self.vista = VistaRLC()
        
        # 2. Estado inicial de los parámetros
        self._params = dict(**DEFAULTS)
        self._t_anim = 0.0  # Llevamos la cuenta del tiempo para la animación
        
        # 3. Configurar el Timer para la animación PRIMERO (aprox 60 FPS = 16ms)
        self.timer_animacion = QTimer()
        self.timer_animacion.timeout.connect(self._animar_ondas)
        self.timer_animacion.start(16)
        
        # 4. Conectar señales de la interfaz
        self._configurar_conexiones()
        
        # 5. Sincronizar valores iniciales en los controles
        self._resetear_ui_a_defaults()
        
        # 6. Primer cálculo y dibujado (ahora que el timer ya existe no dará error)
        self._actualizar_todo()

    def _configurar_conexiones(self):
        """Conecta sliders y spinboxes entre sí y con la lógica de actualización."""
        for key, widgets in self.vista.controles.items():
            slider = widgets["slider"]
            spinbox = widgets["spinbox"]

            slider.valueChanged.connect(lambda val, sb=spinbox: sb.setValue(float(val)))
            spinbox.valueChanged.connect(lambda val, sl=slider: sl.setValue(int(val)))
            
            slider.valueChanged.connect(self._actualizar_todo)
            spinbox.valueChanged.connect(self._actualizar_todo)

        self.vista.btn_reset.clicked.connect(self._on_reset)
        self.vista.btn_pausa.clicked.connect(self._toggle_pausa)

    def _resetear_ui_a_defaults(self):
        """Carga los valores de DEFAULTS en los widgets de la vista."""
        self.vista.blockSignals(True)
        for key, val in DEFAULTS.items():
            self.vista.controles[key]["slider"].setValue(int(val))
            self.vista.controles[key]["spinbox"].setValue(val)
        self.vista.blockSignals(False)

    def _on_reset(self):
        self._resetear_ui_a_defaults()
        self._actualizar_todo()

    def _actualizar_todo(self):
        """Recupera valores de la UI, calcula física y actualiza la info estática."""
        p = {key: self.vista.controles[key]["spinbox"].value() for key in self._params.keys()}
        res = calcular(**p)
        
        self.vista.actualizar_info(res)
        
        freqs, I_arr, _ = calcular_bode(p["R"], p["L"], p["C"], p["Vp"], p["f"], res.f0)
        self.vista.actualizar_bode(freqs, I_arr, p["f"], res.Im)

        # Llamada normal sin parámetros extra
        self._dibujar_estado_actual(p, res)

    def _animar_ondas(self):
        # 0 = Ondas, 1 = Bode, 2 = Esquema. 
        # Pausamos la animación de fondo SOLO si estamos en Bode, ya que es estática.
        if self.vista.tabs.currentIndex() == 1:
            return

        self._t_anim += 0.05  
        
        p = {key: self.vista.controles[key]["spinbox"].value() for key in self._params.keys()}
        res = calcular(**p)
        
        # Llamada normal sin parámetros extra
        self._dibujar_estado_actual(p, res)

    def _dibujar_estado_actual(self, p, res):
        """Función MAESTRA que dibuja las ondas sincronizadas (sin flecha)."""
        w = 2.0 * np.pi * p["f"]
        t_seg = res.t_ms / 1000.0
        
        offset = self._t_anim * w * 0.015 
        
        V_anim = p["Vp"] * np.sin(w * t_seg + offset)
        I_anim = res.Im * np.sin(w * t_seg - res.phi + offset)
        
        # Actualiza directamente
        self.vista.actualizar_ondas(res.t_ms, V_anim, I_anim)

        I_inst = res.Im * np.sin(-res.phi + offset)
        
        # Le enviamos esa corriente al dibujo para que empuje las partículas
        self.vista.esquema.actualizar_esquema(res, p, I_inst)

    def _toggle_pausa(self):
        """Pausa o reanuda la animación de forma limpia."""
        if self.timer_animacion.isActive():
            self.timer_animacion.stop()
            self.vista.btn_pausa.setText("▶ REANUDAR")
            self.vista.btn_pausa.setStyleSheet("background-color: #21262D; color: #3FB950; padding: 8px; border: 1px solid #30363D; font-weight: bold;")
        else:
            self.timer_animacion.start(16)
            self.vista.btn_pausa.setText("⏸ PAUSAR")
            self.vista.btn_pausa.setStyleSheet("background-color: #21262D; color: #E3B341; padding: 8px; border: 1px solid #30363D; font-weight: bold;")