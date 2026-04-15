"""
vista.py — Vista de la simulación RLC 
=====================================
"""

import pyqtgraph as pg
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QFormLayout, QLabel, QSlider, QDoubleSpinBox,
                             QTabWidget, QGroupBox, QPushButton)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPainter, QPen, QColor, QBrush

# ── Paleta de Colores (Estilo Dark) ──────────────────────────────────────────
ACCENT_BLUE = (88, 166, 255)
ACCENT_CYAN = (57, 208, 216)
ACCENT_ORG  = (247, 129, 102)
ACCENT_GRN  = (63, 185, 80)
ACCENT_YLW  = (227, 179, 65)

from PyQt6.QtGui import QPainter, QPen, QColor, QFont
from PyQt6.QtCore import QRect, Qt

from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QBrush
from PyQt6.QtCore import QRect, Qt

class WidgetCircuito(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(350)
        
        self.color_R = QColor(247, 129, 102)
        self.color_L = QColor(139, 148, 158)
        self.color_C = QColor(139, 148, 158)
        
        self.val_R = self.val_L = self.val_C = 0.0
        self.val_XL = self.val_XC = 0.0
        self.val_Vp = self.val_f = 0.0
        self.regimen = ""
        
        self.offset_electrones = 0.0

    def actualizar_esquema(self, res, p, I_inst=0.0):
        self.regimen = res.regimen
        self.val_R = p["R"]
        self.val_L = p["L"]
        self.val_C = p["C"]
        self.val_XL = res.XL
        self.val_XC = res.XC
        self.val_Vp = p["Vp"]
        self.val_f = p["f"]
        
        # --- Magia de la animación ---
        # Acumulamos la posición empujando los electrones según la corriente instantánea.
        # Multiplicamos por 15.0 para que el movimiento sea bien visible en la pantalla.
        self.offset_electrones += I_inst * 15.0 
        
        base_gris = QColor(139, 148, 158)
        color_inductivo = QColor(88, 166, 255)
        color_capacitivo = QColor(57, 208, 216)
        color_resonancia = QColor(63, 185, 80)

        if self.regimen == "resonancia":
            self.color_L = color_resonancia
            self.color_C = color_resonancia
        elif self.regimen == "inductivo":
            self.color_L = color_inductivo
            self.color_C = base_gris
        else:
            self.color_C = color_capacitivo
            self.color_L = base_gris
        
        self.update()

    def _map_s_to_xy(self, s, cx, cy, w, h):
        """Convierte una distancia 1D en coordenadas 2D alrededor del rectángulo."""
        perimetro = 2 * w + 2 * h
        s = s % perimetro # El módulo evita que el número crezca al infinito
        x0, y0 = cx - w//2, cy - h//2
        
        if s < w: # Borde superior (hacia la derecha)
            return x0 + s, y0
        elif s < w + h: # Borde derecho (hacia abajo)
            return x0 + w, y0 + (s - w)
        elif s < 2*w + h: # Borde inferior (hacia la izquierda)
            return x0 + w - (s - w - h), y0 + h
        else: # Borde izquierdo (hacia arriba)
            return x0, y0 + h - (s - 2*w - h)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        cx, cy = self.width() // 2, self.height() // 2
        w, h = 450, 200
        
        # --- 1. Dibujo de los cables principales ---
        pen_cable = QPen(QColor(48, 54, 61), 3)
        painter.setPen(pen_cable)
        
        painter.drawLine(cx - w//2, cy - h//2, cx + w//2, cy - h//2)
        painter.drawLine(cx + w//2, cy - h//2, cx + w//2, cy + h//2)
        painter.drawLine(cx - w//2, cy + h//2, cx + w//2, cy + h//2)
        painter.drawLine(cx - w//2, cy - h//2, cx - w//2, cy - 25)
        painter.drawLine(cx - w//2, cy + 25, cx - w//2, cy + h//2)

        # --- 2. Electrones (Se dibujan ANTES de los componentes para que pasen "por debajo") ---
        painter.setBrush(QBrush(QColor(230, 237, 243))) # Bolitas blancas/celestes
        painter.setPen(Qt.PenStyle.NoPen)
        
        num_electrones = 24
        perimetro = 2 * w + 2 * h
        espaciado = perimetro / num_electrones
        
        for i in range(num_electrones):
            s_base = i * espaciado
            # Sumamos el offset dinámico a cada bolita
            s_actual = s_base + self.offset_electrones
            ex, ey = self._map_s_to_xy(s_actual, cx, cy, w, h)
            painter.drawEllipse(int(ex) - 4, int(ey) - 4, 8, 8)

        # --- 3. Componentes (Les ponemos fondo oscuro para tapar a los electrones que los cruzan) ---
        
        # Fuente de AC
        painter.setBrush(QBrush(QColor(13, 17, 23))) # Color de fondo exacto de tu app
        painter.setPen(QPen(QColor(227, 179, 65), 3))
        painter.drawEllipse(cx - w//2 - 25, cy - 25, 50, 50)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawArc(cx - w//2 - 15, cy - 10, 15, 20, 0, 180 * 16)
        painter.drawArc(cx - w//2, cy - 10, 15, 20, 180 * 16, -180 * 16) 

        # Resistencia
        painter.setBrush(QBrush(QColor(13, 17, 23))) 
        painter.setPen(QPen(self.color_R, 4))
        painter.drawRect(cx - 30, cy - h//2 - 10, 60, 20)
        
        # Inductor (Este lo dejamos sin fondo para que los electrones se vean pasando por las bobinas)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(self.color_L, 4))
        painter.drawArc(cx + w//2 - 15, cy - 40, 30, 26, 90*16, 180*16)
        painter.drawArc(cx + w//2 - 15, cy - 14, 30, 26, 90*16, 180*16)
        painter.drawArc(cx + w//2 - 15, cy + 12, 30, 26, 90*16, 180*16)

        # Capacitor
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(13, 17, 23)))
        painter.drawRect(cx - 18, cy + h//2 - 20, 36, 40) # Tapa el cable que pasa por el medio
        painter.setPen(QPen(self.color_C, 4))
        painter.drawLine(cx - 20, cy + h//2 - 20, cx - 20, cy + h//2 + 20)
        painter.drawLine(cx + 20, cy + h//2 - 20, cx + 20, cy + h//2 + 20)

        # --- 4. Textos Inteligentes ---
        font = QFont("Monospace", 11, QFont.Weight.Bold)
        painter.setFont(font)
        
        painter.setPen(QColor(227, 179, 65))
        painter.drawText(QRect(cx - w//2 - 100, cy - 65, 200, 30), Qt.AlignmentFlag.AlignCenter, f"{self.val_Vp:.1f} V")
        painter.drawText(QRect(cx - w//2 - 100, cy + 35, 200, 30), Qt.AlignmentFlag.AlignCenter, f"{self.val_f:.1f} Hz")
        
        painter.setPen(self.color_R)
        painter.drawText(QRect(cx - 100, cy - h//2 - 45, 200, 25), Qt.AlignmentFlag.AlignCenter, f"R = {self.val_R:.1f} Ω")
        
        painter.setPen(self.color_L)
        painter.drawText(QRect(cx + w//2 + 25, cy - 20, 150, 25), Qt.AlignmentFlag.AlignLeft, f"L = {self.val_L:.1f} mH")
        painter.drawText(QRect(cx + w//2 + 25, cy + 5, 150, 25), Qt.AlignmentFlag.AlignLeft, f"XL = {self.val_XL:.1f} Ω")

        painter.setPen(self.color_C)
        painter.drawText(QRect(cx - 100, cy + h//2 + 25, 200, 25), Qt.AlignmentFlag.AlignCenter, f"C = {self.val_C:.1f} µF")
        painter.drawText(QRect(cx - 100, cy + h//2 + 45, 200, 25), Qt.AlignmentFlag.AlignCenter, f"XC = {self.val_XC:.1f} Ω")

# ── Estilo Corregido para los Paneles ──
ESTILO_GRUPO = """
    QGroupBox { 
        font-weight: bold; 
        border: 1px solid #30363D; 
        border-radius: 6px;
        margin-top: 18px; 
        padding-top: 12px;
    } 
    QGroupBox::title { 
        subcontrol-origin: margin; 
        subcontrol-position: top left; 
        left: 10px; 
        padding: 0 5px;
        color: #8B949E;
    }
"""

class VistaRLC(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("⚡ Simulación Interactiva — Circuito RLC AC (PyQt6)")
        self.resize(1200, 800)

        # Configuración global de PyQtGraph
        pg.setConfigOptions(antialias=True)
        pg.setConfigOption('background', '#0D1117')
        pg.setConfigOption('foreground', '#E6EDF3')

        # Contenedor principal
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout_principal = QHBoxLayout(self.main_widget)

        # ── Panel Izquierdo (Controles e Info) ──
        self.panel_izq = QWidget()
        self.panel_izq.setFixedWidth(350)
        self.layout_izq = QVBoxLayout(self.panel_izq)
        self.layout_principal.addWidget(self.panel_izq)

        self._construir_controles()
        self._construir_panel_info()

        # ── Panel Derecho (Gráficos con Pestañas) ──
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabBar::tab { background: #161B22; color: #8B949E; padding: 10px; border: 1px solid #30363D; }
            QTabBar::tab:selected { background: #21262D; color: #58A6FF; font-weight: bold; }
            QTabWidget::pane { border: 1px solid #30363D; }
        """)
        self.layout_principal.addWidget(self.tabs)

        self._construir_vista_ondas()
        self._construir_vista_bode()
        self._construir_vista_circuito()


    def _construir_vista_circuito(self):
        contenedor = QWidget()
        layout = QVBoxLayout(contenedor)
        
        self.esquema = WidgetCircuito()
        layout.addWidget(self.esquema)
        
        lbl_hint = QLabel("Los componentes se iluminan según el régimen dominante")
        lbl_hint.setStyleSheet("color: #8B949E; font-style: italic;")
        lbl_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_hint)
        
        self.tabs.addTab(contenedor, "⚡ ESQUEMA")

    def _construir_controles(self):
        grupo = QGroupBox("Parámetros del Circuito")
        grupo.setStyleSheet(ESTILO_GRUPO)
        layout = QFormLayout(grupo)

        self.controles = {}
        # Definición: (Clave, Etiqueta, Mínimo, Máximo, Paso)
        parametros = [
            ("R", "Resistencia (Ω)", 1.0, 500.0, 1.0),
            ("L", "Inductancia (mH)", 1.0, 500.0, 1.0),
            ("C", "Capacitancia (µF)", 1.0, 100.0, 1.0),
            ("f", "Frecuencia (Hz)", 1.0, 500.0, 1.0),
            ("Vp", "Voltaje Pico (V)", 1.0, 100.0, 1.0),
        ]

        for key, label, vmin, vmax, step in parametros:
            # Layout horizontal para el slider y el spinbox
            row_layout = QHBoxLayout()
            
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setMinimum(int(vmin))
            slider.setMaximum(int(vmax))
            
            spinbox = QDoubleSpinBox()
            spinbox.setRange(vmin, vmax)
            spinbox.setSingleStep(step)
            spinbox.setDecimals(1)
            spinbox.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
            spinbox.setStyleSheet("background-color: #21262D; color: #E3B341; border: 1px solid #30363D;")

            row_layout.addWidget(slider)
            row_layout.addWidget(spinbox)
            layout.addRow(label, row_layout)

            self.controles[key] = {"slider": slider, "spinbox": spinbox}

        layout_botones = QHBoxLayout()

        self.btn_reset = QPushButton("↺ RESETEAR")
        self.btn_reset.setStyleSheet("background-color: #21262D; color: #F78166; padding: 8px; border: 1px solid #30363D; font-weight: bold;")

        self.btn_pausa = QPushButton("⏸ PAUSAR")
        self.btn_pausa.setStyleSheet("background-color: #21262D; color: #E3B341; padding: 8px; border: 1px solid #30363D; font-weight: bold;")

        layout_botones.addWidget(self.btn_reset)
        layout_botones.addWidget(self.btn_pausa)

        layout.addRow(layout_botones)

        self.layout_izq.addWidget(grupo)

    def _construir_panel_info(self):
        grupo = QGroupBox("Resultados Calculados")
        grupo.setStyleSheet(ESTILO_GRUPO)
        layout = QFormLayout(grupo)
        
        layout.setVerticalSpacing(12)

        self.info_labels = {}
        
        campos = [
            ("XL", "React. Inductiva:<br><span style='font-weight:normal; font-size:10px; color:#8B949E;'>XL = 2π*f*L</span>"), 
            ("XC", "React. Capacitiva:<br><span style='font-weight:normal; font-size:10px; color:#8B949E;'>XC = 1 / (2π*f*C)</span>"),
            ("X",  "Reactancia Neta:<br><span style='font-weight:normal; font-size:10px; color:#8B949E;'>X = XL - XC</span>"), 
            ("Z",  "Impedancia:<br><span style='font-weight:normal; font-size:10px; color:#8B949E;'>Z = √(R² + X²)</span>"),
            ("Im", "Corriente Pico:<br><span style='font-weight:normal; font-size:10px; color:#8B949E;'>I = Vp / Z</span>"), 
            ("phi","Desfase (φ):<br><span style='font-weight:normal; font-size:10px; color:#8B949E;'>φ = arctan(X/R)</span>"),
            ("f0", "Frec. Resonancia:<br><span style='font-weight:normal; font-size:10px; color:#8B949E;'>f₀ = 1 / (2π*√L*C)</span>")
        ]

        font_val = QFont("Monospace", 10, QFont.Weight.Bold)

        for key, texto in campos:
            # Etiqueta del título + fórmula
            lbl_titulo = QLabel(texto)
            lbl_titulo.setTextFormat(Qt.TextFormat.RichText) # Activamos el modo HTML
            
            # Etiqueta del valor numérico
            lbl_val = QLabel("0.00")
            lbl_val.setFont(font_val)
            # Alineamos el número al centro verticalmente y a la derecha
            lbl_val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            
            layout.addRow(lbl_titulo, lbl_val)
            self.info_labels[key] = lbl_val

        self.lbl_regimen = QLabel("RÉGIMEN")
        self.lbl_regimen.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_regimen.setStyleSheet("font-weight: bold; padding: 10px; margin-top: 5px; border-radius: 5px; background: #21262D;")
        layout.addRow(self.lbl_regimen)

        self.layout_izq.addWidget(grupo)
        self.layout_izq.addStretch()

    def _construir_vista_ondas(self):
        self.plot_ondas = pg.PlotWidget(title="Voltaje y Corriente en el Tiempo")
        self.plot_ondas.setLabel('left', 'Voltaje (V)', color='#58A6FF')
        self.plot_ondas.setLabel('bottom', 'Tiempo (ms)')
        self.plot_ondas.showGrid(x=True, y=True, alpha=0.3)
        self.plot_ondas.addLegend(offset=(10, 10))

        # Eje Y secundario para la corriente (FORMA CORREGIDA Y LIMPIA)
        self.plot_ondas.showAxis('right') # Habilitamos el eje derecho
        self.eje_corriente = self.plot_ondas.getAxis('right')
        self.eje_corriente.setLabel('Corriente (A)', color='#39D0D8')
        
        self.view_corriente = pg.ViewBox()
        self.plot_ondas.scene().addItem(self.view_corriente)
        self.eje_corriente.linkToView(self.view_corriente)
        self.view_corriente.setXLink(self.plot_ondas)

        # Líneas de las ondas
        self.line_V = self.plot_ondas.plot(pen=pg.mkPen(color=ACCENT_BLUE, width=2.5), name="Voltaje")
        self.line_I = pg.PlotCurveItem(pen=pg.mkPen(color=ACCENT_CYAN, width=2.5, style=Qt.PenStyle.DashLine), name="Corriente")
        self.view_corriente.addItem(self.line_I)

        # Para que el eje secundario se redimensione correctamente
        def updateViews():
            self.view_corriente.setGeometry(self.plot_ondas.getViewBox().sceneBoundingRect())
            self.view_corriente.linkedViewChanged(self.plot_ondas.getViewBox(), self.view_corriente.XAxis)
        
        self.plot_ondas.getViewBox().sigResized.connect(updateViews)

        self.tabs.addTab(self.plot_ondas, "👁 VISTA ONDAS")

    def _construir_vista_bode(self):
        self.plot_bode = pg.PlotWidget(title="Respuesta en Frecuencia (Corriente)")
        self.plot_bode.setLabel('left', 'Corriente Pico (A)', color='#39D0D8')
        self.plot_bode.setLabel('bottom', 'Frecuencia (Hz)')
        self.plot_bode.showGrid(x=True, y=True, alpha=0.3)

        self.line_bode_I = self.plot_bode.plot(pen=pg.mkPen(color=ACCENT_CYAN, width=2.5))
        
        # Línea vertical para la frecuencia actual
        self.vline_f = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen(color='#E6EDF3', style=Qt.PenStyle.DotLine))
        self.plot_bode.addItem(self.vline_f)
        
        # Punto indicador de la corriente actual
        self.punto_I = self.plot_bode.plot([], [], pen=None, symbol='o', symbolPen=None, symbolBrush=ACCENT_YLW, symbolSize=10)

        self.tabs.addTab(self.plot_bode, "👁 VISTA BODE")

    def actualizar_info(self, cr):
        self.info_labels["XL"].setText(f"{cr.XL:.2f} Ω")
        self.info_labels["XC"].setText(f"{cr.XC:.2f} Ω")
        self.info_labels["X"].setText(f"{cr.X:.2f} Ω")
        self.info_labels["Z"].setText(f"{cr.Z:.2f} Ω")
        self.info_labels["Im"].setText(f"{cr.Im:.4f} A")
        
        # --- ARREGLO: Limpiamos el desfase para que no salga -0.0° ---
        phi_val = cr.phi_grados
        if abs(phi_val) < 0.05: # Si está muy cerca de cero, es cero absoluto
            phi_val = 0.0
        self.info_labels["phi"].setText(f"{phi_val:.1f}°")
        
        self.info_labels["f0"].setText(f"{cr.f0:.2f} Hz")

        # Aplicar colores a los números para que resalten sobre las fórmulas grises
        self.info_labels["XL"].setStyleSheet(f"color: rgb{ACCENT_BLUE};")
        self.info_labels["XC"].setStyleSheet(f"color: rgb{ACCENT_CYAN};")
        self.info_labels["Z"].setStyleSheet(f"color: rgb{ACCENT_ORG};")
        self.info_labels["Im"].setStyleSheet(f"color: rgb{ACCENT_GRN};")

        # Actualizar el letrero de régimen
        reg = cr.regimen
        if reg == "resonancia":
            self.lbl_regimen.setText("⚡ RESONANCIA")
            self.lbl_regimen.setStyleSheet(f"color: rgb{ACCENT_GRN}; font-weight: bold; padding: 10px; background: #21262D;")
        elif reg == "inductivo":
            self.lbl_regimen.setText("↑ Régimen INDUCTIVO")
            self.lbl_regimen.setStyleSheet(f"color: rgb{ACCENT_BLUE}; font-weight: bold; padding: 10px; background: #21262D;")
        else:
            self.lbl_regimen.setText("↓ Régimen CAPACITIVO")
            self.lbl_regimen.setStyleSheet(f"color: rgb{ACCENT_CYAN}; font-weight: bold; padding: 10px; background: #21262D;")
    
    def actualizar_ondas(self, t, V, I):
        self.line_V.setData(t, V)
        self.line_I.setData(t, I)
        
        v_max = max(1.0, abs(V).max())
        i_max = max(0.001, abs(I).max())
        
        self.plot_ondas.setYRange(-v_max * 1.15, v_max * 1.15, padding=0)
        self.view_corriente.setYRange(-i_max * 1.15, i_max * 1.15, padding=0)
        
        self.plot_ondas.enableAutoRange(axis=pg.ViewBox.XAxis)

    def actualizar_bode(self, freqs, I_arr, f_actual, Im):
        self.line_bode_I.setData(freqs, I_arr)
        self.vline_f.setValue(f_actual)
        self.punto_I.setData([f_actual], [Im])
        

        self.plot_bode.enableAutoRange(axis=pg.ViewBox.XYAxes)