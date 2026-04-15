"""
modelo.py — Modelo de la simulación RLC
======================================
"""
 
import numpy as np
 
# ── Valores por defecto ────────────────────────────────────────────────────────
DEFAULTS: dict[str, float] = {
    "R": 47.0,   # Ohms
    "L": 85.0,   # mH
    "C": 12.0,   # µF
    "f": 60.0,   # Hz
    "Vp": 15.0,  # V (pico)
}
 
# ── Parámetros de la señal ─────────────────────────────────────────────────────
N_PUNTOS = 150   # Resolución temporal
N_CICLOS = 3     # Ciclos a mostrar en la vista de ondas
 
# ── Resultado del modelo ───────────────────────────────────────────────────────
class ResultadoRLC:
    """Contenedor de todos los valores calculados para un instante dado."""
 
    __slots__ = (
        "XL", "XC", "X", "Z", "Im", "phi", "f0",
        "t_ms", "V", "I",
    )
 
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
 
    @property
    def phi_grados(self) -> float:
        return float(np.degrees(self.phi))
 
    @property
    def regimen(self) -> str:
        pd = self.phi_grados
        if abs(pd) < 5:
            return "resonancia"
        return "inductivo" if pd > 0 else "capacitivo"
 
# ── Función de cálculo principal ───────────────────────────────────────────────
def calcular(R: float, L: float, C: float, f: float, Vp: float) -> ResultadoRLC:
    Lh = L * 1e-3          # H
    Cf = C * 1e-6          # F
    w  = 2.0 * np.pi * f
 
    XL  = w * Lh
    XC  = 1.0 / (w * Cf) if Cf > 0 else 1e9
    X   = XL - XC
    Z   = np.sqrt(R ** 2 + X ** 2)
    Im  = Vp / Z
    phi = np.arctan2(X, R)
    f0  = (1.0 / (2.0 * np.pi * np.sqrt(Lh * Cf))
           if Lh > 0 and Cf > 0 else 0.0)
 
    t    = (np.linspace(-0.5 / f, N_CICLOS / f, N_PUNTOS)
            if f > 0 else np.zeros(N_PUNTOS))
    wt   = 2.0 * np.pi * f * t
 
    return ResultadoRLC(
        XL=XL, XC=XC, X=X, Z=Z, Im=Im, phi=phi, f0=f0,
        t_ms=t * 1000.0,
        V=Vp * np.sin(wt),
        I=Im * np.sin(wt - phi),
    )
 
# ── Barrido en frecuencia (para Bode) ─────────────────────────────────────────
def calcular_bode(
    R: float, L: float, C: float, Vp: float, f_actual: float, f0: float
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    f_max = max(200.0, f_actual * 1.5, f0 * 2.0)
    freqs = np.linspace(1.0, f_max, 300)
 
    w_arr  = 2.0 * np.pi * freqs
    XL_arr = w_arr * (L * 1e-3)
    XC_arr = 1.0 / (w_arr * (C * 1e-6))
    Z_arr  = np.sqrt(R ** 2 + (XL_arr - XC_arr) ** 2)
    I_arr  = Vp / Z_arr
 
    return freqs, I_arr, Z_arr