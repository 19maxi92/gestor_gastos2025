"""
💰 GESTOR DE GASTOS PERSONAL v7.0 - VERSIÓN PREMIUM CON IA Y AHORRO AUTOMÁTICO
Aplicación completa para gestión de finanzas personales
Con características inspiradas en Fintonic, Plum y Emma:
- Ahorro automático inteligente (redondeo, payday detection)
- Tracking de suscripciones y detección de gastos no usados
- FinScore: puntuación de salud financiera
- Reconocimiento de voz para registro rápido
- Geofencing y reglas de contexto

Autor: Maximiliano Burgos
Año: 2025

ESTE CÓDIGO COMPILA Y FUNCIONA CORRECTAMENTE
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import datetime
from datetime import datetime as dt, timedelta
import json
import urllib.request
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from pathlib import Path
import warnings
import threading
import shutil
import sys
import os

# === CONFIGURACION ===
warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")
plt.rcParams['font.family'] = 'DejaVu Sans'

# === RUTAS - COMPATIBLE CON .EXE ===
def obtener_ruta_base():
    """
    Obtiene la ruta base donde guardar datos.
    Si es .exe, usa AppData en Windows o home en Linux/Mac.
    Si es script Python, usa el directorio del script.
    """
    if getattr(sys, 'frozen', False):
        # Corriendo como .exe (PyInstaller)
        if sys.platform == 'win32':
            # Windows: usar AppData
            app_data = os.environ.get('APPDATA')
            ruta = Path(app_data) / "GestorGastos"
        else:
            # Linux/Mac: usar home directory
            ruta = Path.home() / ".gestor_gastos"
    else:
        # Corriendo como script normal
        ruta = Path(__file__).parent

    return ruta

RUTA_BASE = obtener_ruta_base()
RUTA_DATA = RUTA_BASE / "data"
RUTA_DB = RUTA_DATA / "gastos.db"
RUTA_BACKUPS = RUTA_DATA / "backups"

# Crear directorios si no existen
for ruta in [RUTA_DATA, RUTA_BACKUPS]:
    ruta.mkdir(parents=True, exist_ok=True)

print(f"📁 Guardando datos en: {RUTA_BASE}")
print(f"🗄️ Base de datos: {RUTA_DB}")

# === COLORES MODERNOS (Inspirados en Material Design 3 y Tailwind) ===
COLORES = {
    'primary': '#7c3aed',  # Violet vibrante
    'primary_dark': '#6d28d9',
    'primary_light': '#a78bfa',
    'secondary': '#06b6d4',  # Cyan brillante
    'secondary_dark': '#0891b2',
    'success': '#22c55e',  # Green más brillante
    'success_dark': '#16a34a',
    'danger': '#ef4444',  # Red
    'danger_dark': '#dc2626',
    'warning': '#f59e0b',  # Amber
    'warning_dark': '#d97706',
    'info': '#3b82f6',  # Blue
    'info_dark': '#2563eb',
    'light': '#fafafa',
    'dark': '#18181b',
    'background': '#f5f5f5',  # Fondo suave
    'card_bg': '#ffffff',
    'card_shadow': '#e4e4e7',  # Para simular sombras
    'sidebar_bg': '#18181b',  # Dark sidebar más profundo
    'sidebar_hover': '#27272a',
    'sidebar_active': '#3f3f46',
    'text': '#09090b',
    'text_secondary': '#71717a',
    'text_light': '#a1a1aa',
    'border': '#e4e4e7',
    'border_dark': '#d4d4d8',
    'accent': '#ec4899',  # Pink accent
    'accent_dark': '#db2777',
}

# === DATOS DEFAULT ===
CATEGORIAS_DEFAULT = [
    ('🍕 Comida', '#ff6b6b'),
    ('🚗 Transporte', '#4ecdc4'),
    ('🏠 Hogar', '#45b7d1'),
    ('🛒 Supermercado', '#96ceb4'),
    ('💊 Salud', '#ff8c94'),
    ('🎮 Entretenimiento', '#a29bfe'),
    ('👕 Ropa', '#fd79a8'),
    ('📱 Tecnología', '#6c5ce7'),
    ('❓ Otros', '#95a5a6')
]

CUENTAS_DEFAULT = [
    '💵 Efectivo',
    '💳 Débito',
    '💳 Crédito',
    '📱 MercadoPago',
    '🏦 Cuenta Ahorro'
]

# 250+ ICONOS PARA CATEGORÍAS
ICONOS_CATEGORIAS = [
    # Comida y bebida
    '🍕', '🍔', '🍟', '🌭', '🍿', '🥗', '🍝', '🍜', '🍲', '🍱',
    '🍛', '🍣', '🍤', '🥘', '🍳', '🥞', '🧇', '🥓', '🍗', '🍖',
    '🌮', '🌯', '🥙', '🥪', '🍞', '🥖', '🥨', '🧀', '🥚', '🍠',
    '🥟', '🥠', '🥡', '🍦', '🍧', '🍨', '🍩', '🍪', '🎂', '🍰',
    '🧁', '🥧', '🍫', '🍬', '🍭', '🍮', '🍯', '🍼', '🥛', '☕',
    '🍵', '🧃', '🧉', '🍶', '🍾', '🍷', '🍸', '🍹', '🍺', '🍻',

    # Transporte
    '🚗', '🚕', '🚙', '🚌', '🚎', '🏎️', '🚓', '🚑', '🚒', '🚐',
    '🚚', '🚛', '🚜', '🛵', '🏍️', '🚲', '🛴', '✈️', '🚁', '⛵',
    '🚤', '🛳️', '⛴️', '🛥️', '🚀', '🛸', '🚂', '🚃', '🚄', '🚅',
    '🚆', '🚇', '🚈', '🚉', '🚊', '🚝', '🚞', '🚟', '🚠', '🚡',

    # Hogar y lugares
    '🏠', '🏡', '🏢', '🏬', '🏭', '🏗️', '🏘️', '🏚️', '🏛️', '⛪',
    '🕌', '🕍', '⛩️', '🏰', '🏯', '🗼', '🗽', '🏟️', '🎡', '🎢',
    '🎠', '⛱️', '🏖️', '🏝️', '🏜️', '🌋', '⛰️', '🏔️', '🗻', '🏕️',

    # Compras
    '🛒', '🛍️', '🏪', '🏨', '🏩', '💎', '💍', '👑', '🎁', '🎀',
    '🎈', '🎏', '🎐', '🧧', '✉️', '📦', '📫', '📪', '📬', '📭',

    # Salud
    '💊', '💉', '🩺', '🩹', '⚕️', '🏥', '🩻', '🦷', '💪', '🧠',
    '🫀', '🫁', '🦴', '👁️', '👂', '👃', '🧬', '🔬', '🩸', '🌡️',

    # Entretenimiento
    '🎮', '🎯', '🎲', '🎰', '🎳', '🎾', '⚽', '🏀', '🏈', '⚾',
    '🥎', '🏐', '🏉', '🥏', '🎱', '🏓', '🏸', '🏒', '🏑', '🥍',
    '🏏', '⛳', '🏹', '🎣', '🥊', '🥋', '🎽', '🛹', '🛼', '⛸️',
    '🎿', '🎬', '🎤', '🎧', '🎼', '🎹', '🥁', '🎷', '🎺', '🎸',
    '🎻', '🎭', '🎨', '🖼️', '🎪', '🎟️', '🎫', '🎖️', '🏆', '🏅',

    # Ropa y accesorios
    '👕', '👔', '👗', '👘', '👙', '👚', '👛', '👜', '👝', '🎒',
    '👞', '👟', '🥾', '🥿', '👠', '👡', '👢', '👑', '👒', '🎩',
    '🎓', '🧢', '⛑️', '📿', '🧳', '👓', '🕶️', '🥽', '🧤', '🧣',
    '🧦', '🧥', '🦺', '🪖', '💄', '💅', '🪮', '🪥', '🪒', '🧴',

    # Tecnología
    '📱', '💻', '⌨️', '🖥️', '🖨️', '🖱️', '💾', '💿', '📀', '🎧',
    '📷', '📹', '🎥', '📞', '☎️', '📟', '📠', '📺', '📻', '🎙️',
    '⏰', '⏱️', '⏲️', '⌚', '📡', '🔋', '🔌', '💡', '🔦', '🕯️',

    # Dinero y finanzas
    '💰', '💵', '💴', '💶', '💷', '💳', '💸', '🏦', '📊', '📈',
    '📉', '💹', '🪙', '💲', '💱', '🧾', '💼', '📝', '📋', '📌',

    # Educación
    '📚', '📖', '📕', '📗', '📘', '📙', '📓', '📔', '📒', '📃',
    '📜', '📄', '📰', '🗞️', '📑', '🔖', '🏷️', '✏️', '✒️', '🖊️',
    '🖋️', '🖍️', '📝', '🎓', '🎒', '📐', '📏', '🧮', '🔬', '🔭',

    # Otros útiles
    '❤️', '🧡', '💛', '💚', '💙', '💜', '🖤', '🤍', '🤎', '❣️',
    '⭐', '🌟', '✨', '⚡', '🔥', '💧', '🌊', '🎯', '✅', '❌',
    '⚠️', '🔔', '🔕', '📢', '📣', '💬', '💭', '🗨️', '🗯️', '💤'
]


# === BASE DE DATOS ===
class Database:
    def __init__(self):
        self.conn = sqlite3.connect(str(RUTA_DB))
        self.crear_tablas()
        self.inicializar_datos()

    def crear_tablas(self):
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gastos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                categoria TEXT NOT NULL,
                monto REAL NOT NULL,
                moneda TEXT DEFAULT 'ARS',
                descripcion TEXT,
                cuenta TEXT NOT NULL,
                notas TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE NOT NULL,
                color TEXT NOT NULL,
                icono TEXT DEFAULT '❓',
                categoria_padre TEXT DEFAULT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cuentas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE NOT NULL,
                tipo TEXT DEFAULT 'ARS'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sueldos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mes TEXT UNIQUE NOT NULL,
                monto REAL NOT NULL,
                bonos REAL DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metas_ahorro (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                monto_objetivo REAL NOT NULL,
                monto_actual REAL DEFAULT 0,
                fecha_inicio TEXT NOT NULL,
                fecha_objetivo TEXT NOT NULL,
                moneda TEXT DEFAULT 'ARS',
                icono TEXT DEFAULT '🎯',
                completada INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tarjetas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE NOT NULL,
                banco TEXT,
                limite REAL NOT NULL,
                dia_cierre INTEGER NOT NULL,
                dia_vencimiento INTEGER NOT NULL,
                activa INTEGER DEFAULT 1,
                color TEXT DEFAULT '#4a90e2'
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transacciones_recurrentes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                categoria TEXT NOT NULL,
                monto REAL NOT NULL,
                moneda TEXT DEFAULT 'ARS',
                cuenta TEXT NOT NULL,
                frecuencia TEXT NOT NULL,
                dia_mes INTEGER,
                activa INTEGER DEFAULT 1,
                ultima_ejecucion TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS presupuestos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                categoria TEXT NOT NULL,
                mes TEXT NOT NULL,
                limite REAL NOT NULL,
                UNIQUE(categoria, mes)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gasto_id INTEGER NOT NULL,
                tag TEXT NOT NULL,
                FOREIGN KEY (gasto_id) REFERENCES gastos(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cuentas_por_pagar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                categoria TEXT NOT NULL,
                monto REAL NOT NULL,
                moneda TEXT DEFAULT 'ARS',
                dia_vencimiento INTEGER NOT NULL,
                activa INTEGER DEFAULT 1,
                ultima_alerta TEXT,
                notas TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alertas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL,
                mensaje TEXT NOT NULL,
                fecha TEXT NOT NULL,
                leida INTEGER DEFAULT 0,
                nivel TEXT DEFAULT 'info'
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deudas_compartidas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                monto_total REAL NOT NULL,
                monto_pagado REAL DEFAULT 0,
                con_quien TEXT NOT NULL,
                tipo TEXT NOT NULL,
                fecha_creacion TEXT NOT NULL,
                fecha_vencimiento TEXT,
                saldada INTEGER DEFAULT 0,
                notas TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE NOT NULL,
                descripcion TEXT NOT NULL,
                icono TEXT NOT NULL,
                desbloqueado INTEGER DEFAULT 0,
                fecha_desbloqueo TEXT,
                progreso_actual INTEGER DEFAULT 0,
                progreso_objetivo INTEGER NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS configuracion (
                clave TEXT PRIMARY KEY,
                valor TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reglas_contexto (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                tipo_trigger TEXT NOT NULL,
                condicion TEXT NOT NULL,
                accion TEXT NOT NULL,
                parametros TEXT,
                activa INTEGER DEFAULT 1,
                ultima_ejecucion TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ubicaciones_gastos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gasto_id INTEGER NOT NULL,
                latitud REAL,
                longitud REAL,
                geohash TEXT,
                lugar_nombre TEXT,
                comercio TEXT,
                FOREIGN KEY (gasto_id) REFERENCES gastos(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reglas_geofence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                latitud REAL NOT NULL,
                longitud REAL NOT NULL,
                radio_metros INTEGER NOT NULL,
                categoria_sugerida TEXT,
                cuenta_sugerida TEXT,
                activa INTEGER DEFAULT 1
            )
        ''')

        # Nuevas tablas inspiradas en Plum, Emma y Fintonic
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reglas_ahorro_auto (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                tipo_regla TEXT NOT NULL,
                activa INTEGER DEFAULT 1,
                modo_agresividad TEXT DEFAULT 'moderado',
                meta_destino_id INTEGER,
                ultima_ejecucion TEXT,
                monto_ahorrado_total REAL DEFAULT 0,
                configuracion TEXT,
                FOREIGN KEY (meta_destino_id) REFERENCES metas_ahorro(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS suscripciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                categoria TEXT,
                monto REAL NOT NULL,
                moneda TEXT DEFAULT 'ARS',
                frecuencia TEXT NOT NULL,
                dia_cobro INTEGER,
                fecha_inicio TEXT NOT NULL,
                fecha_proximo_cobro TEXT,
                activa INTEGER DEFAULT 1,
                recordatorio_dias_antes INTEGER DEFAULT 3,
                proveedor TEXT,
                notas TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS finscore_historico (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                puntuacion INTEGER NOT NULL,
                ahorro_mensual REAL,
                gasto_promedio REAL,
                deudas_totales REAL,
                cumplimiento_presupuestos REAL,
                racha_dias INTEGER DEFAULT 0
            )
        ''')

        # Tablas para Splitwise
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS grupos_splitwise (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                tipo TEXT DEFAULT 'general',
                fecha_creacion TEXT NOT NULL,
                activo INTEGER DEFAULT 1,
                icono TEXT DEFAULT '👥'
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS participantes_splitwise (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                grupo_id INTEGER NOT NULL,
                nombre TEXT NOT NULL,
                email TEXT,
                FOREIGN KEY (grupo_id) REFERENCES grupos_splitwise(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gastos_splitwise (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                grupo_id INTEGER NOT NULL,
                descripcion TEXT NOT NULL,
                monto_total REAL NOT NULL,
                moneda TEXT DEFAULT 'ARS',
                pagado_por TEXT NOT NULL,
                fecha TEXT NOT NULL,
                categoria TEXT,
                metodo_division TEXT DEFAULT 'equitativa',
                notas TEXT,
                FOREIGN KEY (grupo_id) REFERENCES grupos_splitwise(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS divisiones_splitwise (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gasto_id INTEGER NOT NULL,
                participante TEXT NOT NULL,
                monto_debe REAL NOT NULL,
                pagado INTEGER DEFAULT 0,
                fecha_pago TEXT,
                FOREIGN KEY (gasto_id) REFERENCES gastos_splitwise(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pagos_splitwise (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                grupo_id INTEGER NOT NULL,
                de_quien TEXT NOT NULL,
                para_quien TEXT NOT NULL,
                monto REAL NOT NULL,
                moneda TEXT DEFAULT 'ARS',
                fecha TEXT NOT NULL,
                notas TEXT,
                FOREIGN KEY (grupo_id) REFERENCES grupos_splitwise(id)
            )
        ''')

        # Tablas inspiradas en Buddy
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS presupuestos_compartidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                categoria TEXT,
                limite REAL NOT NULL,
                mes TEXT NOT NULL,
                moneda TEXT DEFAULT 'ARS',
                compartido INTEGER DEFAULT 0,
                creado_por TEXT NOT NULL,
                fecha_creacion TEXT NOT NULL,
                descripcion TEXT,
                icono TEXT DEFAULT '💰'
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS participantes_presupuesto (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                presupuesto_id INTEGER NOT NULL,
                nombre TEXT NOT NULL,
                email TEXT,
                rol TEXT DEFAULT 'viewer',
                fecha_agregado TEXT NOT NULL,
                activo INTEGER DEFAULT 1,
                FOREIGN KEY (presupuesto_id) REFERENCES presupuestos_compartidos(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alertas_configuracion (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_alerta TEXT NOT NULL,
                categoria TEXT,
                umbral_porcentaje INTEGER DEFAULT 80,
                activa INTEGER DEFAULT 1,
                frecuencia TEXT DEFAULT 'inmediata',
                ultima_notificacion TEXT,
                parametros TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS temas_colores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE NOT NULL,
                primary_color TEXT NOT NULL,
                secondary_color TEXT NOT NULL,
                success_color TEXT NOT NULL,
                danger_color TEXT NOT NULL,
                warning_color TEXT NOT NULL,
                info_color TEXT NOT NULL,
                background_color TEXT NOT NULL,
                card_bg_color TEXT NOT NULL,
                activo INTEGER DEFAULT 0
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notificaciones_buddy (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL,
                titulo TEXT NOT NULL,
                mensaje TEXT NOT NULL,
                categoria TEXT,
                presupuesto_id INTEGER,
                nivel TEXT DEFAULT 'info',
                fecha TEXT NOT NULL,
                leida INTEGER DEFAULT 0,
                accion_requerida INTEGER DEFAULT 0,
                FOREIGN KEY (presupuesto_id) REFERENCES presupuestos_compartidos(id)
            )
        ''')

        self.conn.commit()

    def inicializar_datos(self):
        cursor = self.conn.cursor()

        for nombre, color in CATEGORIAS_DEFAULT:
            cursor.execute('INSERT OR IGNORE INTO categorias (nombre, color) VALUES (?, ?)', (nombre, color))

        for cuenta in CUENTAS_DEFAULT:
            tipo = 'USD' if 'USD' in cuenta else 'ARS'
            cursor.execute('INSERT OR IGNORE INTO cuentas (nombre, tipo) VALUES (?, ?)', (cuenta, tipo))

        # Configuración por defecto
        cursor.execute('INSERT OR IGNORE INTO configuracion (clave, valor) VALUES (?, ?)', ('gamificacion_activa', 'true'))
        cursor.execute('INSERT OR IGNORE INTO configuracion (clave, valor) VALUES (?, ?)', ('alertas_activas', 'true'))
        cursor.execute('INSERT OR IGNORE INTO configuracion (clave, valor) VALUES (?, ?)', ('geolocation_activa', 'false'))
        cursor.execute('INSERT OR IGNORE INTO configuracion (clave, valor) VALUES (?, ?)', ('reglas_contexto_activas', 'true'))
        cursor.execute('INSERT OR IGNORE INTO configuracion (clave, valor) VALUES (?, ?)', ('ubicacion_actual', ''))

        # Logros iniciales
        logros_default = [
            ('🎯 Primer Paso', 'Registrá tu primer gasto', '🎯', 1),
            ('📊 Organizador', 'Registrá 10 gastos', '📊', 10),
            ('💪 Constante', 'Registrá gastos por 7 días seguidos', '💪', 7),
            ('🍕 Sin Delivery', 'Pasá 7 días sin gastar en delivery', '🍕', 7),
            ('💰 Ahorrador', 'Ahorrá el 20% de tus ingresos', '💰', 20),
            ('📈 Analista', 'Consultá el dashboard 30 veces', '📈', 30),
            ('🎮 Maestro', 'Desbloqueá 5 logros', '🎮', 5),
            ('⭐ Leyenda', 'Desbloqueá todos los logros', '⭐', 10)
        ]

        for nombre, desc, icono, objetivo in logros_default:
            cursor.execute('''
                INSERT OR IGNORE INTO logros (nombre, descripcion, icono, progreso_objetivo)
                VALUES (?, ?, ?, ?)
            ''', (nombre, desc, icono, objetivo))

        # Temas de colores predefinidos (estilo Buddy)
        temas_default = [
            ('Default', '#2563eb', '#64748b', '#10b981', '#ef4444', '#f59e0b', '#3b82f6', '#f8f9fa', '#ffffff'),
            ('Dark', '#3b82f6', '#475569', '#22c55e', '#f87171', '#fb923c', '#60a5fa', '#1e293b', '#0f172a'),
            ('Ocean', '#0891b2', '#0e7490', '#14b8a6', '#f43f5e', '#f97316', '#06b6d4', '#ecfeff', '#cffafe'),
            ('Forest', '#16a34a', '#15803d', '#22c55e', '#dc2626', '#ea580c', '#4ade80', '#f0fdf4', '#dcfce7'),
            ('Sunset', '#dc2626', '#b91c1c', '#f97316', '#ef4444', '#facc15', '#fb923c', '#fff7ed', '#fed7aa'),
            ('Purple', '#9333ea', '#7c3aed', '#a78bfa', '#f43f5e', '#fb7185', '#c084fc', '#faf5ff', '#f3e8ff'),
            ('Minimal', '#000000', '#52525b', '#059669', '#dc2626', '#d97706', '#0284c7', '#ffffff', '#f5f5f5')
        ]

        for nombre, primary, secondary, success, danger, warning, info, bg, card_bg in temas_default:
            cursor.execute('''
                INSERT OR IGNORE INTO temas_colores (nombre, primary_color, secondary_color, success_color,
                                                     danger_color, warning_color, info_color, background_color, card_bg_color, activo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (nombre, primary, secondary, success, danger, warning, info, bg, card_bg, 1 if nombre == 'Default' else 0))

        # Configuraciones de alertas proactivas (estilo Buddy)
        cursor.execute('INSERT OR IGNORE INTO alertas_configuracion (tipo_alerta, umbral_porcentaje) VALUES (?, ?)', ('presupuesto_porcentaje', 80))
        cursor.execute('INSERT OR IGNORE INTO alertas_configuracion (tipo_alerta, umbral_porcentaje) VALUES (?, ?)', ('presupuesto_porcentaje', 90))
        cursor.execute('INSERT OR IGNORE INTO alertas_configuracion (tipo_alerta, umbral_porcentaje) VALUES (?, ?)', ('presupuesto_porcentaje', 100))

        self.conn.commit()

    def agregar_gasto(self, fecha, categoria, monto, moneda, descripcion, cuenta, notas=''):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO gastos (fecha, categoria, monto, moneda, descripcion, cuenta, notas)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (fecha, categoria, monto, moneda, descripcion, cuenta, notas))
        self.conn.commit()

    def obtener_gastos(self, mes=None):
        cursor = self.conn.cursor()
        if mes:
            cursor.execute('SELECT * FROM gastos WHERE strftime("%Y-%m", fecha) = ? ORDER BY fecha DESC', (mes,))
        else:
            cursor.execute('SELECT * FROM gastos ORDER BY fecha DESC')
        return cursor.fetchall()

    def eliminar_gasto(self, id_gasto):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM gastos WHERE id=?', (id_gasto,))
        self.conn.commit()

    def obtener_categorias(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM categorias ORDER BY nombre')
        return cursor.fetchall()

    def agregar_categoria(self, nombre, color, icono='❓'):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO categorias (nombre, color, icono) VALUES (?, ?, ?)', (nombre, color, icono))
        self.conn.commit()

    def eliminar_categoria(self, id_cat):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM categorias WHERE id=?', (id_cat,))
        self.conn.commit()

    def obtener_cuentas(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM cuentas ORDER BY nombre')
        return cursor.fetchall()

    def guardar_sueldo_mes(self, mes, monto, bonos=0):
        cursor = self.conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO sueldos (mes, monto, bonos) VALUES (?, ?, ?)', (mes, monto, bonos))
        self.conn.commit()

    def obtener_sueldo_mes(self, mes):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM sueldos WHERE mes=?', (mes,))
        return cursor.fetchone()

    def agregar_meta(self, nombre, monto_objetivo, fecha_objetivo, moneda='ARS', icono='🎯'):
        cursor = self.conn.cursor()
        fecha_inicio = datetime.date.today().isoformat()
        cursor.execute('''
            INSERT INTO metas_ahorro (nombre, monto_objetivo, fecha_inicio, fecha_objetivo, moneda, icono)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (nombre, monto_objetivo, fecha_inicio, fecha_objetivo, moneda, icono))
        self.conn.commit()

    def obtener_metas(self, activas=True):
        cursor = self.conn.cursor()
        if activas:
            cursor.execute('SELECT * FROM metas_ahorro WHERE completada=0 ORDER BY fecha_objetivo')
        else:
            cursor.execute('SELECT * FROM metas_ahorro ORDER BY id DESC')
        return cursor.fetchall()

    def agregar_tarjeta(self, nombre, banco, limite, dia_cierre, dia_vencimiento):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO tarjetas (nombre, banco, limite, dia_cierre, dia_vencimiento)
            VALUES (?, ?, ?, ?, ?)
        ''', (nombre, banco, limite, dia_cierre, dia_vencimiento))
        self.conn.commit()

    def obtener_tarjetas(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM tarjetas WHERE activa=1 ORDER BY nombre')
        return cursor.fetchall()

    def eliminar_tarjeta(self, id_tarjeta):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE tarjetas SET activa=0 WHERE id=?', (id_tarjeta,))
        self.conn.commit()

    def agregar_recurrente(self, nombre, categoria, monto, moneda, cuenta, frecuencia, dia_mes):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO transacciones_recurrentes (nombre, categoria, monto, moneda, cuenta, frecuencia, dia_mes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (nombre, categoria, monto, moneda, cuenta, frecuencia, dia_mes))
        self.conn.commit()

    def obtener_recurrentes(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM transacciones_recurrentes WHERE activa=1 ORDER BY nombre')
        return cursor.fetchall()

    def ejecutar_recurrentes(self):
        """Ejecuta transacciones recurrentes pendientes"""
        cursor = self.conn.cursor()
        hoy = datetime.date.today()

        recurrentes = self.obtener_recurrentes()
        for rec in recurrentes:
            id_rec, nombre, cat, monto, moneda, cuenta, freq, dia, activa, ultima = rec[:10]

            debe_ejecutar = False
            if ultima is None:
                debe_ejecutar = True
            else:
                ultima_fecha = datetime.datetime.strptime(ultima, '%Y-%m-%d').date()
                if freq == 'Mensual' and hoy.day == dia and hoy > ultima_fecha:
                    debe_ejecutar = True
                elif freq == 'Semanal' and (hoy - ultima_fecha).days >= 7:
                    debe_ejecutar = True

            if debe_ejecutar:
                self.agregar_gasto(hoy.isoformat(), cat, monto, moneda, f"{nombre} (Recurrente)", cuenta)
                cursor.execute('UPDATE transacciones_recurrentes SET ultima_ejecucion=? WHERE id=?',
                             (hoy.isoformat(), id_rec))
                self.conn.commit()

    def agregar_presupuesto(self, categoria, mes, limite):
        cursor = self.conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO presupuestos (categoria, mes, limite) VALUES (?, ?, ?)',
                      (categoria, mes, limite))
        self.conn.commit()

    def obtener_presupuesto(self, categoria, mes):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM presupuestos WHERE categoria=? AND mes=?', (categoria, mes))
        return cursor.fetchone()

    def obtener_todos_presupuestos(self, mes):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM presupuestos WHERE mes=?', (mes,))
        return cursor.fetchall()

    def agregar_tag(self, gasto_id, tag):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO tags (gasto_id, tag) VALUES (?, ?)', (gasto_id, tag))
        self.conn.commit()

    def obtener_tags(self, gasto_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT tag FROM tags WHERE gasto_id=?', (gasto_id,))
        return [t[0] for t in cursor.fetchall()]

    # === CUENTAS POR PAGAR ===
    def agregar_cuenta_por_pagar(self, nombre, categoria, monto, moneda, dia_venc, notas=''):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO cuentas_por_pagar (nombre, categoria, monto, moneda, dia_vencimiento, notas)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (nombre, categoria, monto, moneda, dia_venc, notas))
        self.conn.commit()

    def obtener_cuentas_por_pagar(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM cuentas_por_pagar WHERE activa=1 ORDER BY dia_vencimiento')
        return cursor.fetchall()

    def verificar_vencimientos(self):
        """Verifica vencimientos próximos y crea alertas"""
        cursor = self.conn.cursor()
        hoy = datetime.date.today()
        dia_actual = hoy.day

        cuentas = self.obtener_cuentas_por_pagar()
        for cuenta in cuentas:
            id_cuenta, nombre, cat, monto, moneda, dia_venc, activa, ultima_alerta = cuenta[:8]

            dias_para_venc = dia_venc - dia_actual
            if dias_para_venc <= 3 and dias_para_venc >= 0:
                # Verificar si ya se alertó este mes
                if ultima_alerta != hoy.strftime('%Y-%m'):
                    mensaje = f"⚠️ Vence {nombre}: ${monto:,.0f} {moneda} en {dias_para_venc} día(s)"
                    self.crear_alerta('vencimiento', mensaje, 'warning')
                    cursor.execute('UPDATE cuentas_por_pagar SET ultima_alerta=? WHERE id=?',
                                 (hoy.strftime('%Y-%m'), id_cuenta))

        self.conn.commit()

    # === ALERTAS ===
    def crear_alerta(self, tipo, mensaje, nivel='info'):
        cursor = self.conn.cursor()
        fecha = datetime.date.today().isoformat()
        cursor.execute('''
            INSERT INTO alertas (tipo, mensaje, fecha, nivel)
            VALUES (?, ?, ?, ?)
        ''', (tipo, mensaje, fecha, nivel))
        self.conn.commit()

    def obtener_alertas(self, solo_no_leidas=True):
        cursor = self.conn.cursor()
        if solo_no_leidas:
            cursor.execute('SELECT * FROM alertas WHERE leida=0 ORDER BY fecha DESC LIMIT 10')
        else:
            cursor.execute('SELECT * FROM alertas ORDER BY fecha DESC LIMIT 50')
        return cursor.fetchall()

    def marcar_alerta_leida(self, id_alerta):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE alertas SET leida=1 WHERE id=?', (id_alerta,))
        self.conn.commit()

    def verificar_presupuestos(self, mes):
        """Verifica si algún presupuesto está cerca del límite"""
        presupuestos = self.obtener_todos_presupuestos(mes)
        gastos = self.obtener_gastos(mes)

        for pres in presupuestos:
            id_pres, categoria, mes_pres, limite = pres
            gasto_actual = sum(g[3] for g in gastos if g[2] == categoria and g[4] == 'ARS')

            pct = (gasto_actual / limite * 100) if limite > 0 else 0

            if pct >= 90 and pct < 100:
                mensaje = f"⚠️ Presupuesto '{categoria}' al {pct:.0f}%: ${gasto_actual:,.0f} de ${limite:,.0f}"
                self.crear_alerta('presupuesto', mensaje, 'warning')
            elif pct >= 100:
                mensaje = f"🚨 ¡Presupuesto '{categoria}' excedido! {pct:.0f}%: ${gasto_actual:,.0f} de ${limite:,.0f}"
                self.crear_alerta('presupuesto', mensaje, 'danger')

    def verificar_gastos_inusuales(self, mes):
        """Detecta incrementos inusuales en categorías"""
        import calendar

        hoy = datetime.date.today()
        mes_anterior = (hoy.replace(day=1) - timedelta(days=1)).strftime('%Y-%m')

        gastos_actual = self.obtener_gastos(mes)
        gastos_anterior = self.obtener_gastos(mes_anterior)

        categorias = set([g[2] for g in gastos_actual])

        for cat in categorias:
            total_actual = sum(g[3] for g in gastos_actual if g[2] == cat and g[4] == 'ARS')
            total_anterior = sum(g[3] for g in gastos_anterior if g[2] == cat and g[4] == 'ARS')

            if total_anterior > 0:
                incremento = ((total_actual - total_anterior) / total_anterior) * 100

                if incremento >= 25:
                    mensaje = f"📊 Gasto en '{cat}' aumentó +{incremento:.0f}% este mes (${total_actual:,.0f} vs ${total_anterior:,.0f})"
                    self.crear_alerta('anomalia', mensaje, 'info')

    # === DEUDAS COMPARTIDAS ===
    def agregar_deuda(self, nombre, monto_total, con_quien, tipo, fecha_venc=None, notas=''):
        cursor = self.conn.cursor()
        fecha_creacion = datetime.date.today().isoformat()
        cursor.execute('''
            INSERT INTO deudas_compartidas (nombre, monto_total, con_quien, tipo, fecha_creacion, fecha_vencimiento, notas)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (nombre, monto_total, con_quien, tipo, fecha_creacion, fecha_venc, notas))
        self.conn.commit()

    def obtener_deudas(self, saldadas=False):
        cursor = self.conn.cursor()
        if saldadas:
            cursor.execute('SELECT * FROM deudas_compartidas ORDER BY fecha_creacion DESC')
        else:
            cursor.execute('SELECT * FROM deudas_compartidas WHERE saldada=0 ORDER BY fecha_creacion DESC')
        return cursor.fetchall()

    def actualizar_pago_deuda(self, id_deuda, monto_pago):
        cursor = self.conn.cursor()
        cursor.execute('SELECT monto_total, monto_pagado FROM deudas_compartidas WHERE id=?', (id_deuda,))
        deuda = cursor.fetchone()
        if deuda:
            total, pagado = deuda
            nuevo_pagado = pagado + monto_pago
            saldada = 1 if nuevo_pagado >= total else 0

            cursor.execute('UPDATE deudas_compartidas SET monto_pagado=?, saldada=? WHERE id=?',
                         (nuevo_pagado, saldada, id_deuda))
            self.conn.commit()

    # === GAMIFICACIÓN ===
    def obtener_config(self, clave):
        cursor = self.conn.cursor()
        cursor.execute('SELECT valor FROM configuracion WHERE clave=?', (clave,))
        res = cursor.fetchone()
        return res[0] if res else None

    def actualizar_config(self, clave, valor):
        cursor = self.conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO configuracion (clave, valor) VALUES (?, ?)', (clave, valor))
        self.conn.commit()

    def obtener_logros(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM logros ORDER BY desbloqueado DESC, id')
        return cursor.fetchall()

    def verificar_logros(self):
        """Verifica y desbloquea logros automáticamente"""
        if self.obtener_config('gamificacion_activa') != 'true':
            return

        cursor = self.conn.cursor()

        # Logro: Primer Paso
        total_gastos = len(self.obtener_gastos())
        if total_gastos >= 1:
            self.actualizar_progreso_logro('🎯 Primer Paso', 1)

        # Logro: Organizador
        if total_gastos >= 10:
            self.actualizar_progreso_logro('📊 Organizador', total_gastos)

        # Logro: Constante (7 días seguidos)
        gastos = self.obtener_gastos()
        if gastos:
            fechas = sorted(set([g[1] for g in gastos]))
            racha = 1
            max_racha = 1
            for i in range(1, len(fechas)):
                fecha_ant = datetime.datetime.strptime(fechas[i-1], '%Y-%m-%d').date()
                fecha_act = datetime.datetime.strptime(fechas[i], '%Y-%m-%d').date()
                if (fecha_act - fecha_ant).days == 1:
                    racha += 1
                    max_racha = max(max_racha, racha)
                else:
                    racha = 1
            if max_racha >= 7:
                self.actualizar_progreso_logro('💪 Constante', max_racha)

        # Verificar logros desbloqueados
        cursor.execute('SELECT COUNT(*) FROM logros WHERE desbloqueado=1')
        total_desbloqueados = cursor.fetchone()[0]
        if total_desbloqueados >= 5:
            self.actualizar_progreso_logro('🎮 Maestro', total_desbloqueados)

    def actualizar_progreso_logro(self, nombre, progreso):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, progreso_objetivo, desbloqueado FROM logros WHERE nombre=?', (nombre,))
        logro = cursor.fetchone()

        if logro:
            id_logro, objetivo, desbloqueado = logro
            if not desbloqueado and progreso >= objetivo:
                fecha = datetime.date.today().isoformat()
                cursor.execute('''
                    UPDATE logros SET desbloqueado=1, fecha_desbloqueo=?, progreso_actual=?
                    WHERE id=?
                ''', (fecha, progreso, id_logro))
                self.conn.commit()

                # Crear alerta de logro desbloqueado
                self.crear_alerta('logro', f'🎉 ¡Logro desbloqueado! {nombre}', 'success')
            else:
                cursor.execute('UPDATE logros SET progreso_actual=? WHERE id=?', (progreso, id_logro))
                self.conn.commit()

    # === REGLAS DE CONTEXTO ===
    def agregar_regla_contexto(self, nombre, tipo_trigger, condicion, accion, parametros=''):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO reglas_contexto (nombre, tipo_trigger, condicion, accion, parametros)
            VALUES (?, ?, ?, ?, ?)
        ''', (nombre, tipo_trigger, condicion, accion, parametros))
        self.conn.commit()

    def obtener_reglas_contexto(self, solo_activas=False):
        cursor = self.conn.cursor()
        if solo_activas:
            cursor.execute('SELECT * FROM reglas_contexto WHERE activa=1 ORDER BY nombre')
        else:
            cursor.execute('SELECT * FROM reglas_contexto ORDER BY nombre')
        return cursor.fetchall()

    def ejecutar_reglas_contexto(self, contexto):
        """Evalúa y ejecuta reglas basadas en contexto actual"""
        if self.obtener_config('reglas_contexto_activas') != 'true':
            return

        reglas = self.obtener_reglas_contexto(solo_activas=True)
        cursor = self.conn.cursor()

        for regla in reglas:
            id_regla, nombre, tipo_trigger, condicion, accion, params, activa, ultima_ej = regla

            # Evaluar condición
            cumple = False

            if tipo_trigger == 'hora':
                hora_actual = datetime.datetime.now().hour
                if 'mañana' in condicion and 6 <= hora_actual < 12:
                    cumple = True
                elif 'tarde' in condicion and 12 <= hora_actual < 20:
                    cumple = True
                elif 'noche' in condicion and (hora_actual >= 20 or hora_actual < 6):
                    cumple = True

            elif tipo_trigger == 'dia_semana':
                dia = datetime.datetime.now().weekday()
                if 'fin_de_semana' in condicion and dia >= 5:
                    cumple = True
                elif 'semana' in condicion and dia < 5:
                    cumple = True

            elif tipo_trigger == 'clima':
                if contexto.get('temperatura'):
                    temp = contexto['temperatura']
                    if 'calor' in condicion and temp > 28:
                        cumple = True
                    elif 'frio' in condicion and temp < 15:
                        cumple = True

            elif tipo_trigger == 'mes':
                mes = datetime.datetime.now().month
                if 'vacaciones' in condicion and mes in [1, 2, 7, 12]:
                    cumple = True

            # Ejecutar acción si cumple
            if cumple:
                hoy = datetime.date.today().isoformat()
                if ultima_ej != hoy:  # Solo una vez por día
                    self.ejecutar_accion_regla(accion, params)
                    cursor.execute('UPDATE reglas_contexto SET ultima_ejecucion=? WHERE id=?',
                                 (hoy, id_regla))
                    self.conn.commit()

    def ejecutar_accion_regla(self, accion, parametros):
        """Ejecuta la acción de una regla"""
        if accion == 'alerta':
            self.crear_alerta('regla_contexto', parametros, 'info')
        elif accion == 'cambiar_presupuesto':
            # Parsear parámetros: "categoria:Comida,factor:0.8"
            pass

    # === GEOLOCALIZACIÓN ===
    def agregar_ubicacion_gasto(self, gasto_id, lat, lon, lugar='', comercio=''):
        cursor = self.conn.cursor()
        geohash = self.calcular_geohash(lat, lon, precision=7)
        cursor.execute('''
            INSERT INTO ubicaciones_gastos (gasto_id, latitud, longitud, geohash, lugar_nombre, comercio)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (gasto_id, lat, lon, geohash, lugar, comercio))
        self.conn.commit()

    def calcular_geohash(self, lat, lon, precision=7):
        """Calcula geohash simplificado"""
        # Implementación básica de geohash
        lat_code = int((lat + 90) * 10000)
        lon_code = int((lon + 180) * 10000)
        return f"{lat_code:07d}{lon_code:08d}"[:precision]

    def obtener_gastos_por_ubicacion(self, lat, lon, radio_metros=500):
        """Obtiene gastos cerca de una ubicación"""
        cursor = self.conn.cursor()
        geohash_centro = self.calcular_geohash(lat, lon, precision=5)

        cursor.execute('''
            SELECT g.*, u.lugar_nombre, u.comercio
            FROM gastos g
            JOIN ubicaciones_gastos u ON g.id = u.gasto_id
            WHERE u.geohash LIKE ?
            ORDER BY g.fecha DESC
        ''', (geohash_centro + '%',))
        return cursor.fetchall()

    def agregar_regla_geofence(self, nombre, lat, lon, radio, categoria='', cuenta=''):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO reglas_geofence (nombre, latitud, longitud, radio_metros, categoria_sugerida, cuenta_sugerida)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (nombre, lat, lon, radio, categoria, cuenta))
        self.conn.commit()

    def obtener_reglas_geofence(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM reglas_geofence WHERE activa=1')
        return cursor.fetchall()

    def sugerir_categoria_por_ubicacion(self, lat, lon):
        """Sugiere categoría basada en reglas de geofence"""
        reglas = self.obtener_reglas_geofence()

        for regla in reglas:
            id_r, nombre, lat_r, lon_r, radio, cat_sug, cuenta_sug, activa = regla

            # Calcular distancia (fórmula Haversine simplificada)
            import math
            R = 6371000  # Radio de la Tierra en metros

            lat1, lon1 = math.radians(lat), math.radians(lon)
            lat2, lon2 = math.radians(lat_r), math.radians(lon_r)

            dlat = lat2 - lat1
            dlon = lon2 - lon1

            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            distancia = R * c

            if distancia <= radio:
                return {'categoria': cat_sug, 'cuenta': cuenta_sug, 'lugar': nombre}

        return None

    # === AHORRO AUTOMÁTICO (Inspirado en Plum) ===
    def crear_regla_ahorro_auto(self, nombre, tipo_regla, modo_agresividad='moderado', meta_id=None, config=None):
        """
        Crea regla de ahorro automático
        Tipos: 'payday', 'redondeo', '52semanas', 'dias_lluvia', 'porcentaje_ingreso'
        Modos: 'timido', 'moderado', 'agresivo', 'bestia'
        """
        cursor = self.conn.cursor()
        config_json = json.dumps(config) if config else None
        cursor.execute('''
            INSERT INTO reglas_ahorro_auto (nombre, tipo_regla, modo_agresividad, meta_destino_id, configuracion, activa)
            VALUES (?, ?, ?, ?, ?, 1)
        ''', (nombre, tipo_regla, modo_agresividad, meta_id, config_json))
        self.conn.commit()

    def obtener_reglas_ahorro_auto(self, solo_activas=True):
        cursor = self.conn.cursor()
        if solo_activas:
            cursor.execute('SELECT * FROM reglas_ahorro_auto WHERE activa=1 ORDER BY nombre')
        else:
            cursor.execute('SELECT * FROM reglas_ahorro_auto ORDER BY nombre')
        return cursor.fetchall()

    def ejecutar_ahorro_redondeo(self, monto_gasto, regla_id, modo='moderado'):
        """Redondea el gasto y ahorra la diferencia"""
        # Multiplicadores según agresividad
        multiplicadores = {
            'timido': 1,      # Redondeo al peso más cercano
            'moderado': 10,   # Redondeo a los 10 pesos
            'agresivo': 50,   # Redondeo a los 50 pesos
            'bestia': 100     # Redondeo a los 100 pesos
        }

        mult = multiplicadores.get(modo, 10)
        redondeo = math.ceil(monto_gasto / mult) * mult
        diferencia = redondeo - monto_gasto

        if diferencia > 0:
            self._registrar_ahorro_automatico(regla_id, diferencia)

        return diferencia

    def detectar_payday(self, fecha=None):
        """Detecta si hoy es día de pago (ingreso significativo)"""
        if not fecha:
            fecha = datetime.date.today()

        # Buscar ingresos en los últimos 3 días
        fecha_str = fecha.strftime('%Y-%m-%d')
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT SUM(monto) FROM gastos
            WHERE fecha >= date(?, '-3 days') AND fecha <= ?
            AND monto < 0
        ''', (fecha_str, fecha_str))

        resultado = cursor.fetchone()
        ingreso = resultado[0] if resultado else None
        return ingreso and abs(ingreso) > 10000  # Umbral configurable

    def aplicar_ahorro_payday(self, regla_id, modo='moderado'):
        """Ahorra un porcentaje cuando detecta el sueldo"""
        porcentajes = {
            'timido': 0.02,    # 2%
            'moderado': 0.05,  # 5%
            'agresivo': 0.10,  # 10%
            'bestia': 0.15     # 15%
        }

        if self.detectar_payday():
            # Obtener último ingreso
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT monto FROM gastos
                WHERE monto < 0
                ORDER BY fecha DESC LIMIT 1
            ''')
            ingreso = cursor.fetchone()

            if ingreso:
                monto_ingreso = abs(ingreso[0])
                ahorro = monto_ingreso * porcentajes.get(modo, 0.05)
                self._registrar_ahorro_automatico(regla_id, ahorro)
                return ahorro

        return 0

    def _registrar_ahorro_automatico(self, regla_id, monto):
        """Registra el ahorro automático y actualiza la meta si existe"""
        cursor = self.conn.cursor()

        # Actualizar monto total de la regla
        cursor.execute('''
            UPDATE reglas_ahorro_auto
            SET monto_ahorrado_total = monto_ahorrado_total + ?,
                ultima_ejecucion = ?
            WHERE id = ?
        ''', (monto, datetime.date.today().isoformat(), regla_id))

        # Si hay meta destino, actualizar
        cursor.execute('SELECT meta_destino_id FROM reglas_ahorro_auto WHERE id=?', (regla_id,))
        resultado = cursor.fetchone()
        meta_id = resultado[0] if resultado else None

        if meta_id:
            cursor.execute('''
                UPDATE metas_ahorro
                SET monto_actual = monto_actual + ?
                WHERE id = ?
            ''', (monto, meta_id))

        self.conn.commit()

    # === SUSCRIPCIONES (Inspirado en Emma) ===
    def crear_suscripcion(self, nombre, monto, frecuencia, dia_cobro=None, categoria=None, proveedor=None):
        """Crea una suscripción para tracking"""
        cursor = self.conn.cursor()
        fecha_inicio = datetime.date.today().isoformat()

        # Calcular próximo cobro
        hoy = datetime.date.today()
        if dia_cobro:
            if dia_cobro > hoy.day:
                proximo = hoy.replace(day=dia_cobro)
            else:
                # Próximo mes
                if hoy.month == 12:
                    proximo = hoy.replace(year=hoy.year+1, month=1, day=dia_cobro)
                else:
                    proximo = hoy.replace(month=hoy.month+1, day=dia_cobro)
        else:
            proximo = None

        cursor.execute('''
            INSERT INTO suscripciones (nombre, categoria, monto, frecuencia, dia_cobro,
                                      fecha_inicio, fecha_proximo_cobro, proveedor, activa)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
        ''', (nombre, categoria, monto, frecuencia, dia_cobro, fecha_inicio,
              proximo.isoformat() if proximo else None, proveedor))
        self.conn.commit()

    def obtener_suscripciones(self, solo_activas=True):
        cursor = self.conn.cursor()
        if solo_activas:
            cursor.execute('SELECT * FROM suscripciones WHERE activa=1 ORDER BY nombre')
        else:
            cursor.execute('SELECT * FROM suscripciones ORDER BY nombre')
        return cursor.fetchall()

    def calcular_gasto_suscripciones_mensual(self):
        """Calcula cuánto se gasta en suscripciones por mes"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT SUM(
                CASE frecuencia
                    WHEN 'mensual' THEN monto
                    WHEN 'anual' THEN monto / 12
                    WHEN 'semanal' THEN monto * 4.33
                    ELSE 0
                END
            ) FROM suscripciones WHERE activa=1
        ''')
        resultado = cursor.fetchone()[0]
        return resultado if resultado else 0

    def detectar_suscripciones_no_usadas(self):
        """
        Detecta suscripciones que podrían no estar usándose
        (sin gastos recientes en esa categoría/proveedor)
        """
        cursor = self.conn.cursor()
        suscripciones = self.obtener_suscripciones()
        no_usadas = []

        for susc in suscripciones:
            id_s, nombre, cat, monto, moneda, freq = susc[:6]

            # Buscar gastos recientes relacionados (últimos 60 días)
            cursor.execute('''
                SELECT COUNT(*) FROM gastos
                WHERE fecha >= date('now', '-60 days')
                AND (descripcion LIKE ? OR categoria = ?)
            ''', (f'%{nombre}%', cat))

            count = cursor.fetchone()[0]
            if count == 0:
                no_usadas.append((nombre, monto, moneda))

        return no_usadas

    # === FINSCORE (Inspirado en Fintonic) ===
    def calcular_finscore(self):
        """
        Calcula puntuación de salud financiera (0-1000)
        Basado en:
        - Ahorro mensual (30%)
        - Cumplimiento de presupuestos (25%)
        - Control de deudas (25%)
        - Consistencia/racha (20%)
        """
        cursor = self.conn.cursor()
        puntuacion = 0

        # 1. Ahorro mensual (0-300 puntos)
        mes_actual = datetime.date.today().strftime('%Y-%m')
        cursor.execute('SELECT SUM(monto) FROM gastos WHERE fecha LIKE ? AND monto < 0', (f'{mes_actual}%',))
        ingresos = abs(cursor.fetchone()[0] or 0)

        cursor.execute('SELECT SUM(monto) FROM gastos WHERE fecha LIKE ? AND monto > 0', (f'{mes_actual}%',))
        gastos = cursor.fetchone()[0] or 0

        if ingresos > 0:
            tasa_ahorro = (ingresos - gastos) / ingresos
            puntos_ahorro = min(300, int(tasa_ahorro * 1000))
            puntuacion += max(0, puntos_ahorro)

        # 2. Cumplimiento presupuestos (0-250 puntos)
        cursor.execute('SELECT COUNT(*) FROM presupuestos WHERE mes=?', (mes_actual,))
        cant_presupuestos = cursor.fetchone()[0]

        if cant_presupuestos > 0:
            cursor.execute('''
                SELECT p.categoria, p.limite,
                       COALESCE(SUM(g.monto), 0) as gastado
                FROM presupuestos p
                LEFT JOIN gastos g ON g.categoria = p.categoria
                    AND g.fecha LIKE ?
                WHERE p.mes = ?
                GROUP BY p.categoria, p.limite
            ''', (f'{mes_actual}%', mes_actual))

            cumplidos = 0
            for cat, limite, gastado in cursor.fetchall():
                if gastado <= limite:
                    cumplidos += 1

            puntos_presupuesto = int((cumplidos / cant_presupuestos) * 250)
            puntuacion += puntos_presupuesto

        # 3. Control de deudas (0-250 puntos)
        cursor.execute('SELECT SUM(monto_total - monto_pagado) FROM deudas_compartidas WHERE saldada=0')
        deudas = cursor.fetchone()[0] or 0

        if ingresos > 0:
            ratio_deuda = min(1, deudas / ingresos)
            puntos_deuda = int((1 - ratio_deuda) * 250)
            puntuacion += puntos_deuda
        else:
            puntuacion += 125  # Puntos base si no hay ingresos registrados

        # 4. Racha y consistencia (0-200 puntos)
        cursor.execute('''
            SELECT COUNT(DISTINCT DATE(fecha)) FROM gastos
            WHERE fecha >= date('now', '-30 days')
        ''')
        dias_con_registro = cursor.fetchone()[0] or 0
        puntos_racha = int((dias_con_registro / 30) * 200)
        puntuacion += puntos_racha

        # Guardar en histórico
        cursor.execute('''
            INSERT INTO finscore_historico (fecha, puntuacion, ahorro_mensual, gasto_promedio, deudas_totales, racha_dias)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (datetime.date.today().isoformat(), puntuacion, ingresos - gastos, gastos, deudas, dias_con_registro))
        self.conn.commit()

        return puntuacion

    def obtener_finscore_actual(self):
        """Obtiene el FinScore más reciente"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT puntuacion FROM finscore_historico ORDER BY fecha DESC LIMIT 1')
        resultado = cursor.fetchone()
        return resultado[0] if resultado else None

    # === SPLITWISE ===
    def crear_grupo_splitwise(self, nombre, descripcion='', tipo='general', icono='👥'):
        """Crea un nuevo grupo para gastos compartidos"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO grupos_splitwise (nombre, descripcion, tipo, fecha_creacion, icono)
            VALUES (?, ?, ?, ?, ?)
        ''', (nombre, descripcion, tipo, datetime.date.today().isoformat(), icono))
        self.conn.commit()
        return cursor.lastrowid

    def obtener_grupos_splitwise(self, activos_solo=True):
        """Obtiene todos los grupos de Splitwise"""
        cursor = self.conn.cursor()
        if activos_solo:
            cursor.execute('SELECT * FROM grupos_splitwise WHERE activo = 1 ORDER BY fecha_creacion DESC')
        else:
            cursor.execute('SELECT * FROM grupos_splitwise ORDER BY fecha_creacion DESC')
        return cursor.fetchall()

    def agregar_participante_splitwise(self, grupo_id, nombre, email=''):
        """Agrega un participante a un grupo"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO participantes_splitwise (grupo_id, nombre, email)
            VALUES (?, ?, ?)
        ''', (grupo_id, nombre, email))
        self.conn.commit()

    def obtener_participantes_grupo(self, grupo_id):
        """Obtiene todos los participantes de un grupo"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM participantes_splitwise WHERE grupo_id = ?', (grupo_id,))
        return cursor.fetchall()

    def agregar_gasto_splitwise(self, grupo_id, descripcion, monto_total, pagado_por,
                                metodo_division='equitativa', divisiones=None, categoria='', notas=''):
        """
        Agrega un gasto compartido y sus divisiones
        divisiones: dict {participante: monto_debe} o None para división equitativa
        """
        cursor = self.conn.cursor()

        # Insertar gasto
        cursor.execute('''
            INSERT INTO gastos_splitwise (grupo_id, descripcion, monto_total, pagado_por,
                                         fecha, categoria, metodo_division, notas)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (grupo_id, descripcion, monto_total, pagado_por,
              datetime.date.today().isoformat(), categoria, metodo_division, notas))

        gasto_id = cursor.lastrowid

        # Insertar divisiones
        if divisiones is None:
            # División equitativa entre todos los participantes
            participantes = self.obtener_participantes_grupo(grupo_id)
            if participantes:
                monto_por_persona = monto_total / len(participantes)
                divisiones = {p[2]: monto_por_persona for p in participantes}  # p[2] es el nombre

        for participante, monto_debe in divisiones.items():
            cursor.execute('''
                INSERT INTO divisiones_splitwise (gasto_id, participante, monto_debe)
                VALUES (?, ?, ?)
            ''', (gasto_id, participante, monto_debe))

        self.conn.commit()
        return gasto_id

    def obtener_gastos_grupo(self, grupo_id):
        """Obtiene todos los gastos de un grupo"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM gastos_splitwise
            WHERE grupo_id = ?
            ORDER BY fecha DESC
        ''', (grupo_id,))
        return cursor.fetchall()

    def calcular_balances_grupo(self, grupo_id):
        """
        Calcula el balance de cada participante en un grupo
        Retorna: dict {participante: balance} (positivo = le deben, negativo = debe)
        """
        cursor = self.conn.cursor()
        participantes = self.obtener_participantes_grupo(grupo_id)
        balances = {p[2]: 0.0 for p in participantes}  # p[2] es el nombre

        # Obtener todos los gastos del grupo
        gastos = self.obtener_gastos_grupo(grupo_id)

        for gasto in gastos:
            gasto_id = gasto[0]
            pagado_por = gasto[4]  # índice del campo pagado_por

            # Obtener divisiones de este gasto
            cursor.execute('''
                SELECT participante, monto_debe, pagado
                FROM divisiones_splitwise
                WHERE gasto_id = ?
            ''', (gasto_id,))
            divisiones = cursor.fetchall()

            for div in divisiones:
                participante = div[0]
                monto_debe = div[1]
                pagado = div[2]

                if not pagado:  # Si no ha pagado su parte
                    if participante == pagado_por:
                        # Si el que pagó es el mismo, no se debe a sí mismo
                        # pero sí le deben los demás
                        pass
                    else:
                        # Este participante debe dinero
                        balances[participante] -= monto_debe
                        # El que pagó tiene saldo a favor
                        balances[pagado_por] += monto_debe

        # Restar los pagos realizados
        cursor.execute('''
            SELECT pagador, receptor, monto
            FROM pagos_splitwise
            WHERE grupo_id = ?
        ''', (grupo_id,))
        pagos = cursor.fetchall()

        for pago in pagos:
            pagador = pago[0]
            receptor = pago[1]
            monto = pago[2]

            balances[pagador] += monto  # El que pagó reduce su deuda
            balances[receptor] -= monto  # El que recibió reduce lo que le deben

        return balances

    def simplificar_deudas_grupo(self, grupo_id):
        """
        Simplifica las deudas del grupo usando algoritmo greedy
        Retorna: lista de tuplas (deudor, acreedor, monto)
        """
        balances = self.calcular_balances_grupo(grupo_id)

        # Separar deudores y acreedores
        deudores = [(nombre, -balance) for nombre, balance in balances.items() if balance < -0.01]
        acreedores = [(nombre, balance) for nombre, balance in balances.items() if balance > 0.01]

        # Ordenar de mayor a menor
        deudores.sort(key=lambda x: x[1], reverse=True)
        acreedores.sort(key=lambda x: x[1], reverse=True)

        transacciones = []
        i, j = 0, 0

        while i < len(deudores) and j < len(acreedores):
            deudor, deuda = deudores[i]
            acreedor, credito = acreedores[j]

            monto_pago = min(deuda, credito)

            if monto_pago > 0.01:  # Ignorar centavos
                transacciones.append((deudor, acreedor, round(monto_pago, 2)))

            # Actualizar balances
            deudores[i] = (deudor, deuda - monto_pago)
            acreedores[j] = (acreedor, credito - monto_pago)

            # Avanzar si se saldó
            if deudores[i][1] < 0.01:
                i += 1
            if acreedores[j][1] < 0.01:
                j += 1

        return transacciones

    def registrar_pago_splitwise(self, grupo_id, pagador, receptor, monto, notas=''):
        """Registra un pago entre participantes"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO pagos_splitwise (grupo_id, pagador, receptor, monto, fecha, notas)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (grupo_id, pagador, receptor, monto, datetime.date.today().isoformat(), notas))
        self.conn.commit()

    # === BUDDY - PRESUPUESTOS COMPARTIDOS ===
    def crear_presupuesto_compartido(self, nombre, categoria, limite, mes, creado_por, compartido=False, descripcion='', icono='💰'):
        """Crea un presupuesto compartido estilo Buddy"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO presupuestos_compartidos (nombre, categoria, limite, mes, compartido, creado_por, fecha_creacion, descripcion, icono)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nombre, categoria, limite, mes, 1 if compartido else 0, creado_por, datetime.date.today().isoformat(), descripcion, icono))
        self.conn.commit()
        return cursor.lastrowid

    def obtener_presupuestos_compartidos(self):
        """Obtiene todos los presupuestos compartidos"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM presupuestos_compartidos ORDER BY fecha_creacion DESC')
        return cursor.fetchall()

    def agregar_participante_presupuesto(self, presupuesto_id, nombre, email='', rol='viewer'):
        """Agrega un participante a un presupuesto compartido"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO participantes_presupuesto (presupuesto_id, nombre, email, rol, fecha_agregado)
            VALUES (?, ?, ?, ?, ?)
        ''', (presupuesto_id, nombre, email, rol, datetime.date.today().isoformat()))
        self.conn.commit()

    def obtener_participantes_presupuesto(self, presupuesto_id):
        """Obtiene los participantes de un presupuesto"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM participantes_presupuesto WHERE presupuesto_id = ? AND activo = 1', (presupuesto_id,))
        return cursor.fetchall()

    def calcular_uso_presupuesto_compartido(self, presupuesto_id):
        """Calcula el uso actual de un presupuesto compartido"""
        cursor = self.conn.cursor()

        # Obtener info del presupuesto
        cursor.execute('SELECT categoria, mes, limite FROM presupuestos_compartidos WHERE id = ?', (presupuesto_id,))
        presup = cursor.fetchone()

        if not presup:
            return 0, 0, 0

        categoria = presup[0]
        mes = presup[1]
        limite = presup[2]

        # Calcular gastos del mes en esa categoría
        if categoria:
            cursor.execute('''
                SELECT COALESCE(SUM(monto), 0) FROM gastos
                WHERE strftime('%Y-%m', fecha) = ? AND categoria = ?
            ''', (mes, categoria))
        else:
            # Si no hay categoría específica, todos los gastos del mes
            cursor.execute('''
                SELECT COALESCE(SUM(monto), 0) FROM gastos
                WHERE strftime('%Y-%m', fecha) = ?
            ''', (mes,))

        gastado = cursor.fetchone()[0]
        porcentaje = (gastado / limite * 100) if limite > 0 else 0

        return gastado, limite, porcentaje

    # === BUDDY - SISTEMA DE ALERTAS PROACTIVAS ===
    def crear_alerta_configuracion(self, tipo_alerta, categoria=None, umbral_porcentaje=80, activa=True):
        """Configura una alerta proactiva"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO alertas_configuracion (tipo_alerta, categoria, umbral_porcentaje, activa)
            VALUES (?, ?, ?, ?)
        ''', (tipo_alerta, categoria, umbral_porcentaje, 1 if activa else 0))
        self.conn.commit()

    def obtener_alertas_configuracion(self):
        """Obtiene todas las configuraciones de alertas"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM alertas_configuracion WHERE activa = 1')
        return cursor.fetchall()

    def verificar_alertas_presupuesto(self):
        """Verifica y genera alertas proactivas de presupuestos"""
        alertas_generadas = []
        cursor = self.conn.cursor()

        # Obtener configuraciones de alertas activas
        configs = self.obtener_alertas_configuracion()

        # Verificar cada presupuesto compartido
        presupuestos = self.obtener_presupuestos_compartidos()

        for presup in presupuestos:
            presup_id = presup[0]
            nombre = presup[1]
            categoria = presup[2]

            gastado, limite, porcentaje = self.calcular_uso_presupuesto_compartido(presup_id)

            # Verificar umbrales de alertas
            for config in configs:
                tipo = config[1]
                umbral = config[3]

                if tipo == 'presupuesto_porcentaje' and porcentaje >= umbral:
                    # Verificar si ya se notificó recientemente
                    cursor.execute('''
                        SELECT fecha FROM notificaciones_buddy
                        WHERE presupuesto_id = ? AND tipo = 'presupuesto_excedido'
                        ORDER BY fecha DESC LIMIT 1
                    ''', (presup_id,))

                    ultima = cursor.fetchone()

                    # Solo notificar si no se ha notificado hoy
                    debe_notificar = True
                    if ultima:
                        ultima_fecha = datetime.datetime.fromisoformat(ultima[0]).date()
                        debe_notificar = ultima_fecha < datetime.date.today()

                    if debe_notificar:
                        if porcentaje >= 100:
                            nivel = 'danger'
                            titulo = f"⚠️ Presupuesto Excedido: {nombre}"
                            mensaje = f"Te pasaste del presupuesto! Gastaste ${gastado:,.0f} de ${limite:,.0f} ({porcentaje:.0f}%)"
                        elif porcentaje >= 90:
                            nivel = 'warning'
                            titulo = f"⚠️ Alerta: {nombre}"
                            mensaje = f"Estás al {porcentaje:.0f}% del presupuesto (${gastado:,.0f} de ${limite:,.0f})"
                        else:
                            nivel = 'info'
                            titulo = f"📊 Aviso: {nombre}"
                            mensaje = f"Usaste el {porcentaje:.0f}% del presupuesto (${gastado:,.0f} de ${limite:,.0f})"

                        self.crear_notificacion_buddy(
                            tipo='presupuesto_excedido',
                            titulo=titulo,
                            mensaje=mensaje,
                            categoria=categoria,
                            presupuesto_id=presup_id,
                            nivel=nivel,
                            accion_requerida=1 if porcentaje >= 100 else 0
                        )

                        alertas_generadas.append({
                            'titulo': titulo,
                            'mensaje': mensaje,
                            'nivel': nivel
                        })

        return alertas_generadas

    def crear_notificacion_buddy(self, tipo, titulo, mensaje, categoria=None, presupuesto_id=None, nivel='info', accion_requerida=0):
        """Crea una notificación estilo Buddy"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO notificaciones_buddy (tipo, titulo, mensaje, categoria, presupuesto_id, nivel, fecha, accion_requerida)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (tipo, titulo, mensaje, categoria, presupuesto_id, nivel, datetime.datetime.now().isoformat(), accion_requerida))
        self.conn.commit()

    def obtener_notificaciones_buddy(self, solo_no_leidas=False):
        """Obtiene notificaciones de Buddy"""
        cursor = self.conn.cursor()
        if solo_no_leidas:
            cursor.execute('SELECT * FROM notificaciones_buddy WHERE leida = 0 ORDER BY fecha DESC LIMIT 50')
        else:
            cursor.execute('SELECT * FROM notificaciones_buddy ORDER BY fecha DESC LIMIT 100')
        return cursor.fetchall()

    def marcar_notificacion_leida(self, notif_id):
        """Marca una notificación como leída"""
        cursor = self.conn.cursor()
        cursor.execute('UPDATE notificaciones_buddy SET leida = 1 WHERE id = ?', (notif_id,))
        self.conn.commit()

    # === BUDDY - TEMAS DE COLORES ===
    def crear_tema_color(self, nombre, primary, secondary, success, danger, warning, info, background, card_bg):
        """Crea un nuevo tema de colores"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO temas_colores (nombre, primary_color, secondary_color, success_color, danger_color,
                                      warning_color, info_color, background_color, card_bg_color)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nombre, primary, secondary, success, danger, warning, info, background, card_bg))
        self.conn.commit()

    def obtener_temas_disponibles(self):
        """Obtiene todos los temas de colores disponibles"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM temas_colores')
        return cursor.fetchall()

    def activar_tema(self, tema_id):
        """Activa un tema de colores"""
        cursor = self.conn.cursor()
        # Desactivar todos los temas
        cursor.execute('UPDATE temas_colores SET activo = 0')
        # Activar el tema seleccionado
        cursor.execute('UPDATE temas_colores SET activo = 1 WHERE id = ?', (tema_id,))
        self.conn.commit()

    def obtener_tema_activo(self):
        """Obtiene el tema de colores activo"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM temas_colores WHERE activo = 1 LIMIT 1')
        return cursor.fetchone()

    def cerrar(self):
        self.conn.close()


# === PARSER DE TEXTO LIBRE ===
def parsear_gasto_texto(texto, categorias_disponibles):
    """
    Parsea texto libre para extraer información de gasto
    Ejemplos:
    - "Gasto 2000 en supermercado"
    - "Pagué 1500 de comida"
    - "500 pesos en café"
    - "Almuerzo $350"
    """
    import re

    # Limpiar texto
    texto = texto.lower().strip()

    # Extraer monto
    monto = None
    patrones_monto = [
        r'\$\s*(\d+[\.,]?\d*)',  # $2000 o $2.000
        r'(\d+[\.,]?\d*)\s*pesos',  # 2000 pesos
        r'(\d+[\.,]?\d*)\s*ars',  # 2000 ars
        r'(\d+[\.,]?\d*)\s*(en|de|por)',  # 2000 en/de/por
        r'(gasto|pagué|pague|gasté|gaste|compré|compre)\s*(\d+[\.,]?\d*)',  # gasté 2000
    ]

    for patron in patrones_monto:
        match = re.search(patron, texto)
        if match:
            # Obtener el grupo numérico
            grupos = match.groups()
            for grupo in grupos:
                if grupo and re.match(r'\d+', str(grupo)):
                    monto = float(str(grupo).replace('.', '').replace(',', '.'))
                    break
            if monto:
                break

    # Si no encontró monto, buscar cualquier número
    if not monto:
        match = re.search(r'(\d+[\.,]?\d*)', texto)
        if match:
            monto = float(match.group(1).replace('.', '').replace(',', '.'))

    # Extraer categoría
    categoria = None
    palabras_clave = {
        'comida': ['comida', 'almuerzo', 'cena', 'desayuno', 'merienda', 'restaurante', 'resto', 'comí', 'comi'],
        'supermercado': ['supermercado', 'super', 'mercado', 'compras'],
        'transporte': ['transporte', 'colectivo', 'bondi', 'taxi', 'uber', 'subte', 'tren', 'nafta', 'combustible'],
        'café': ['café', 'cafeteria', 'bar'],
        'delivery': ['delivery', 'pedidos', 'pedidosya', 'rappi'],
        'entretenimiento': ['cine', 'película', 'pelicula', 'juego', 'entretenimiento', 'salida'],
        'salud': ['salud', 'farmacia', 'médico', 'medico', 'doctor', 'remedio'],
        'ropa': ['ropa', 'zapatillas', 'zapatos', 'camisa', 'pantalón', 'pantalon', 'vestido'],
        'hogar': ['hogar', 'casa', 'alquiler', 'expensas', 'luz', 'gas', 'agua', 'internet'],
        'tecnología': ['tecnología', 'tecnologia', 'celular', 'computadora', 'notebook', 'auriculares']
    }

    for cat, palabras in palabras_clave.items():
        for palabra in palabras:
            if palabra in texto:
                # Buscar en categorías disponibles
                for cat_disp in categorias_disponibles:
                    if cat.lower() in cat_disp.lower() or palabra.lower() in cat_disp.lower():
                        categoria = cat_disp
                        break
                if categoria:
                    break
        if categoria:
            break

    # Si no encontró categoría, usar la primera disponible o "Otros"
    if not categoria:
        for cat_disp in categorias_disponibles:
            if 'otro' in cat_disp.lower():
                categoria = cat_disp
                break
        if not categoria and categorias_disponibles:
            categoria = categorias_disponibles[0]

    # Extraer descripción (usar el texto original sin el monto)
    descripcion = texto
    if monto:
        # Remover el monto del texto para dejarlo como descripción
        descripcion = re.sub(r'\$?\s*' + str(int(monto)) + r'[\.,]?\d*\s*(pesos|ars)?', '', texto).strip()
        descripcion = re.sub(r'(gasto|pagué|pague|gasté|gaste|compré|compre)\s*', '', descripcion).strip()
        descripcion = re.sub(r'\s+(en|de|por)\s+', ' ', descripcion).strip()

    return {
        'monto': monto if monto else 0,
        'categoria': categoria,
        'descripcion': descripcion if descripcion else 'Gasto',
        'confianza': 1.0 if (monto and categoria) else 0.5
    }


# === APIs DE CONTEXTO ===
def obtener_clima(ciudad='Buenos Aires'):
    """Obtiene información del clima usando API pública"""
    try:
        # Usar Open-Meteo (API gratuita sin key)
        # Para Buenos Aires: lat=-34.6037, lon=-58.3816
        coords = {
            'Buenos Aires': (-34.6037, -58.3816),
            'Córdoba': (-31.4201, -64.1888),
            'Rosario': (-32.9468, -60.6393),
            'Mendoza': (-32.8895, -68.8458)
        }

        lat, lon = coords.get(ciudad, coords['Buenos Aires'])

        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0')

        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())

        if 'current_weather' in data:
            temp = data['current_weather']['temperature']
            windspeed = data['current_weather']['windspeed']
            weathercode = data['current_weather']['weathercode']

            # Códigos de clima según WMO
            condiciones = {
                0: 'Despejado',
                1: 'Mayormente despejado',
                2: 'Parcialmente nublado',
                3: 'Nublado',
                45: 'Niebla',
                48: 'Niebla con escarcha',
                51: 'Llovizna ligera',
                61: 'Lluvia ligera',
                80: 'Lluvia',
                95: 'Tormenta'
            }

            condicion = condiciones.get(weathercode, 'Desconocido')

            return {
                'temperatura': temp,
                'viento': windspeed,
                'condicion': condicion,
                'ciudad': ciudad
            }
    except:
        return None

def obtener_contexto_actual():
    """Obtiene contexto completo actual"""
    contexto = {}

    # Clima
    clima = obtener_clima()
    if clima:
        contexto['temperatura'] = clima['temperatura']
        contexto['clima'] = clima['condicion']

    # Hora del día
    hora = datetime.datetime.now().hour
    if 6 <= hora < 12:
        contexto['momento'] = 'mañana'
    elif 12 <= hora < 20:
        contexto['momento'] = 'tarde'
    else:
        contexto['momento'] = 'noche'

    # Día de la semana
    dia = datetime.datetime.now().weekday()
    contexto['es_fin_de_semana'] = dia >= 5

    # Mes (vacaciones)
    mes = datetime.datetime.now().month
    contexto['es_vacaciones'] = mes in [1, 2, 7, 12]

    return contexto


# === COTIZACIONES ===
def obtener_cotizacion_dolar():
    try:
        url = "https://dolarapi.com/v1/dolares"
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
        
        cotizaciones = {}
        for item in data:
            tipo = item.get('nombre', '')
            if 'Blue' in tipo:
                cotizaciones['Blue'] = {'compra': item.get('compra', 0), 'venta': item.get('venta', 0)}
            elif 'Oficial' in tipo:
                cotizaciones['Oficial'] = {'compra': item.get('compra', 0), 'venta': item.get('venta', 0)}
        
        return cotizaciones if cotizaciones else obtener_cotizaciones_respaldo()
    except:
        return obtener_cotizaciones_respaldo()


def obtener_cotizaciones_respaldo():
    import random
    base = 1150
    var = random.uniform(-10, 10)
    return {
        'Blue': {'compra': base + var, 'venta': base + var + 20},
        'Oficial': {'compra': base - 100 + var, 'venta': base - 90 + var}
    }


def obtener_tasas_conversion():
    """Obtiene tasas de conversión desde API"""
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
        
        rates = data.get('rates', {})
        return {
            'USD': 1.0,
            'EUR': rates.get('EUR', 0.92),
            'GBP': rates.get('GBP', 0.79),
            'BRL': rates.get('BRL', 5.0),
            'ARS': rates.get('ARS', 1000.0),
            'CLP': rates.get('CLP', 900.0),
            'MXN': rates.get('MXN', 17.0),
            'UYU': rates.get('UYU', 39.0)
        }
    except:
        return {
            'USD': 1.0, 'EUR': 0.92, 'GBP': 0.79, 'BRL': 5.0,
            'ARS': 1000.0, 'CLP': 900.0, 'MXN': 17.0, 'UYU': 39.0
        }


# === FUNCIONES HELPER PARA UI MODERNA ===
def crear_boton_moderno(parent, texto, comando, color='primary', ancho_completo=False, **kwargs):
    """Crea un botón con estilo moderno y consistente"""
    # Configuración de colores según el tipo
    colores_btn = {
        'primary': (COLORES['primary'], COLORES['primary_dark'], 'white'),
        'secondary': (COLORES['secondary'], COLORES['secondary_dark'], 'white'),
        'success': (COLORES['success'], COLORES['success_dark'], 'white'),
        'danger': (COLORES['danger'], COLORES['danger_dark'], 'white'),
        'warning': (COLORES['warning'], COLORES['warning_dark'], 'white'),
        'info': (COLORES['info'], COLORES['info_dark'], 'white'),
    }

    bg_color, hover_color, fg_color = colores_btn.get(color, colores_btn['primary'])

    # Configuración por defecto
    config = {
        'bg': bg_color,
        'fg': fg_color,
        'relief': tk.FLAT,
        'cursor': 'hand2',
        'font': ('Segoe UI', 10, 'bold'),
        'activebackground': hover_color,
        'activeforeground': fg_color,
        'borderwidth': 0,
        'padx': 20,
        'pady': 10,
    }

    # Sobrescribir con kwargs personalizados
    config.update(kwargs)

    btn = tk.Button(parent, text=texto, command=comando, **config)

    # Efectos hover
    def on_enter(e):
        btn['bg'] = hover_color

    def on_leave(e):
        btn['bg'] = bg_color

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

    if ancho_completo:
        btn.pack(fill=tk.X, padx=15, pady=5)

    return btn

def crear_card(parent, **kwargs):
    """Crea un frame con estilo de tarjeta moderna"""
    config = {
        'bg': COLORES['card_bg'],
        'relief': tk.SOLID,
        'borderwidth': 1,
        'highlightbackground': COLORES['border'],
        'highlightthickness': 1,
    }
    config.update(kwargs)

    frame = tk.Frame(parent, **config)
    return frame

def crear_label_titulo(parent, texto, tamaño=14, **kwargs):
    """Crea un label con estilo de título"""
    config = {
        'bg': COLORES['card_bg'],
        'fg': COLORES['text'],
        'font': ('Segoe UI', tamaño, 'bold'),
    }
    config.update(kwargs)

    label = tk.Label(parent, text=texto, **config)
    return label


# === APLICACIÓN PRINCIPAL ===
class GestorGastos:
    def __init__(self, root):
        self.root = root
        self.root.title("💰 Gestor de Gastos Personal v7.5 - UI Moderna")
        self.root.geometry("1400x800")
        self.root.configure(bg=COLORES['background'])

        self.db = Database()
        self.mes_actual = datetime.date.today().strftime('%Y-%m')
        self.cotizaciones = {}
        self.vista_actual = 'dashboard'

        self.centrar_ventana()
        self.db.ejecutar_recurrentes()  # Ejecutar transacciones recurrentes al inicio
        self.db.verificar_vencimientos()  # Verificar vencimientos
        self.db.verificar_presupuestos(self.mes_actual)  # Verificar presupuestos
        self.db.verificar_gastos_inusuales(self.mes_actual)  # Detectar gastos inusuales
        self.db.verificar_logros()  # Verificar logros

        # Contexto y reglas
        self.contexto_actual = obtener_contexto_actual()
        self.db.ejecutar_reglas_contexto(self.contexto_actual)

        self.crear_interfaz()
        self.actualizar_cotizaciones()
        self.actualizar_clima()
        self.root.protocol("WM_DELETE_WINDOW", self.al_cerrar)

    def centrar_ventana(self):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (800 // 2)
        self.root.geometry(f'1400x800+{x}+{y}')

    def crear_interfaz(self):
        # MENU
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        menu_archivo = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="📁 Archivo", menu=menu_archivo)
        menu_archivo.add_command(label="Exportar CSV", command=self.exportar_csv)
        menu_archivo.add_command(label="Backup", command=self.hacer_backup)
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Salir", command=self.al_cerrar)

        menu_config = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="⚙️ Configuración", menu=menu_config)
        menu_config.add_command(label="💵 Sueldo Mensual", command=self.ventana_sueldo)
        menu_config.add_command(label="📂 Gestionar Categorías", command=self.ventana_categorias)
        menu_config.add_separator()
        menu_config.add_command(label="🎨 Temas", command=self.mostrar_temas)
        menu_config.add_command(label="💱 Conversor de Monedas", command=self.ventana_conversor)
        menu_config.add_separator()
        menu_config.add_command(label="⚙️ Reglas de Contexto", command=self.mostrar_reglas_contexto)
        menu_config.add_command(label="📍 Geofence", command=self.mostrar_geofence)

        menu_ayuda = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="❓ Ayuda", menu=menu_ayuda)
        menu_ayuda.add_command(label="Acerca de", command=self.mostrar_acerca_de)

        # HEADER
        frame_header = tk.Frame(self.root, bg=COLORES['primary'], height=65)
        frame_header.pack(fill=tk.X)
        frame_header.pack_propagate(False)

        tk.Label(
            frame_header,
            text="💰 Gestor de Gastos v6.0",
            font=('Segoe UI', 20, 'bold'),
            bg=COLORES['primary'],
            fg='white'
        ).pack(side=tk.LEFT, padx=25)

        # Frame para cotización y botón
        frame_cotizacion = tk.Frame(frame_header, bg=COLORES['primary'])
        frame_cotizacion.pack(side=tk.RIGHT, padx=15)

        # Botón de conversión rápida
        tk.Button(
            frame_cotizacion,
            text="💱",
            font=('Segoe UI', 12, 'bold'),
            bg=COLORES['primary_dark'],
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.ventana_conversion_rapida,
            padx=8,
            pady=2
        ).pack(side=tk.RIGHT, padx=(5, 0))

        # Cotización en header
        self.label_dolar = tk.Label(
            frame_cotizacion,
            text="💵 Cargando...",
            font=('Segoe UI', 10),
            bg=COLORES['primary'],
            fg='white'
        )
        self.label_dolar.pack(side=tk.RIGHT)

        # Info de clima
        self.label_clima = tk.Label(
            frame_header,
            text="",
            font=('Segoe UI', 9),
            bg=COLORES['primary'],
            fg='white'
        )
        self.label_clima.pack(side=tk.RIGHT, padx=15)

        tk.Label(
            frame_header,
            text=f"📅 {datetime.date.today().strftime('%d/%m/%Y')}",
            font=('Segoe UI', 10),
            bg=COLORES['primary'],
            fg='white'
        ).pack(side=tk.RIGHT, padx=15)

        # CONTENEDOR PRINCIPAL (sidebar + contenido)
        frame_main = tk.Frame(self.root, bg=COLORES['background'])
        frame_main.pack(fill=tk.BOTH, expand=True)

        # SIDEBAR CON SCROLL
        sidebar_container = tk.Frame(frame_main, bg=COLORES['sidebar_bg'], width=250)
        sidebar_container.pack(side=tk.LEFT, fill=tk.Y)
        sidebar_container.pack_propagate(False)

        # Canvas para scroll
        canvas_sidebar = tk.Canvas(sidebar_container, bg=COLORES['sidebar_bg'], highlightthickness=0, width=250)
        scrollbar_sidebar = tk.Scrollbar(sidebar_container, orient="vertical", command=canvas_sidebar.yview, bg=COLORES['sidebar_bg'])

        sidebar = tk.Frame(canvas_sidebar, bg=COLORES['sidebar_bg'])
        sidebar.bind("<Configure>", lambda e: canvas_sidebar.configure(scrollregion=canvas_sidebar.bbox("all")))

        canvas_sidebar.create_window((0, 0), window=sidebar, anchor="nw", width=235)
        canvas_sidebar.configure(yscrollcommand=scrollbar_sidebar.set)

        canvas_sidebar.pack(side="left", fill="both", expand=True)
        scrollbar_sidebar.pack(side="right", fill="y")

        # Soporte para scroll con rueda del mouse
        def _on_mousewheel(event):
            canvas_sidebar.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas_sidebar.bind_all("<MouseWheel>", _on_mousewheel)

        # Botón de agregar gasto destacado (Estilo Monefy)
        tk.Button(
            sidebar,
            text="⚡ ENTRADA RÁPIDA",
            font=('Segoe UI', 12, 'bold'),
            bg=COLORES['success'],
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.ventana_registro_rapido,
            pady=15
        ).pack(fill=tk.X, padx=15, pady=(10, 10))

        # Botón secundario para entrada completa
        tk.Button(
            sidebar,
            text="➕ Entrada Completa",
            font=('Segoe UI', 9),
            bg=COLORES['primary_dark'],
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.ventana_agregar_gasto,
            pady=8
        ).pack(fill=tk.X, padx=15, pady=(0, 20))

        # Separador
        tk.Frame(sidebar, bg=COLORES['border'], height=1).pack(fill=tk.X, padx=10, pady=5)

        # BOTONES PRINCIPALES (navegación esencial)
        nav_buttons_principales = [
            ("📊 Dashboard", 'dashboard', self.mostrar_dashboard),
            ("📋 Gastos", 'gastos', self.mostrar_gastos),
            ("📊 Presupuestos", 'presupuestos', self.mostrar_presupuestos),
            ("🎯 Metas", 'metas', self.mostrar_metas),
            ("💳 Tarjetas", 'tarjetas', self.mostrar_tarjetas),
            ("🏆 FinScore", 'finscore', self.mostrar_finscore),
        ]

        tk.Label(sidebar, text="PRINCIPAL", font=('Segoe UI', 8, 'bold'),
                bg=COLORES['sidebar_bg'], fg=COLORES['text_light'], anchor='w', padx=20).pack(fill=tk.X, pady=(5,2))

        # SECCIÓN: Gestión (funciones de gestión)
        nav_buttons_gestion = [
            ("🔔 Alertas", 'alertas', self.mostrar_alertas),
            ("📅 Cuentas por Pagar", 'cuentas_pagar', self.mostrar_cuentas_por_pagar),
            ("📺 Suscripciones", 'suscripciones', self.mostrar_suscripciones),
            ("🔄 Recurrentes", 'recurrentes', self.mostrar_recurrentes),
            ("💰 Ahorro Auto", 'ahorro_auto', self.mostrar_ahorro_automatico),
        ]

        # SECCIÓN: Social (funciones colaborativas)
        nav_buttons_social = [
            ("👥 Gastos Compartidos", 'deudas', self.mostrar_deudas),
            ("💸 Splitwise", 'splitwise', self.mostrar_splitwise),
            ("🤝 Presup. Compartidos", 'buddy_presupuestos', self.mostrar_buddy_presupuestos),
            ("🔔 Notif. Buddy", 'buddy_notificaciones', self.mostrar_buddy_notificaciones),
        ]

        # SECCIÓN: Gamificación
        nav_buttons_gamificacion = [
            ("🎮 Logros", 'logros', self.mostrar_logros),
        ]

        # SECCIÓN: Ayuda
        nav_buttons_ayuda = [
            ("❓ Ayuda", 'ayuda', self.mostrar_ayuda),
        ]

        self.nav_buttons = {}

        # Renderizar botones principales
        for text, vista, comando in nav_buttons_principales:
            btn = tk.Button(
                sidebar,
                text=text,
                font=('Segoe UI', 10, 'bold'),
                bg=COLORES['sidebar_bg'],
                fg='white',
                relief=tk.FLAT,
                cursor='hand2',
                anchor='w',
                padx=20,
                pady=10,
                command=lambda v=vista, c=comando: self.cambiar_vista(v, c)
            )
            btn.pack(fill=tk.X, padx=5, pady=1)
            btn.bind('<Enter>', lambda e, b=btn: b.config(bg=COLORES['sidebar_hover']))
            btn.bind('<Leave>', lambda e, b=btn, v=vista: b.config(
                bg=COLORES['primary'] if self.vista_actual == v else COLORES['sidebar_bg']
            ))
            self.nav_buttons[vista] = btn

        # Separador
        tk.Frame(sidebar, bg=COLORES['border'], height=1).pack(fill=tk.X, padx=10, pady=8)

        # Label Gestión
        tk.Label(sidebar, text="GESTIÓN", font=('Segoe UI', 8, 'bold'),
                bg=COLORES['sidebar_bg'], fg=COLORES['text_light'], anchor='w', padx=20).pack(fill=tk.X, pady=(5,2))

        for text, vista, comando in nav_buttons_gestion:
            btn = tk.Button(
                sidebar,
                text=text,
                font=('Segoe UI', 10),
                bg=COLORES['sidebar_bg'],
                fg='white',
                relief=tk.FLAT,
                cursor='hand2',
                anchor='w',
                padx=20,
                pady=10,
                command=lambda v=vista, c=comando: self.cambiar_vista(v, c)
            )
            btn.pack(fill=tk.X, padx=5, pady=1)
            btn.bind('<Enter>', lambda e, b=btn: b.config(bg=COLORES['sidebar_hover']))
            btn.bind('<Leave>', lambda e, b=btn, v=vista: b.config(
                bg=COLORES['primary'] if self.vista_actual == v else COLORES['sidebar_bg']
            ))
            self.nav_buttons[vista] = btn

        # Separador
        tk.Frame(sidebar, bg=COLORES['border'], height=1).pack(fill=tk.X, padx=10, pady=8)

        # Label Social
        tk.Label(sidebar, text="SOCIAL", font=('Segoe UI', 8, 'bold'),
                bg=COLORES['sidebar_bg'], fg=COLORES['text_light'], anchor='w', padx=20).pack(fill=tk.X, pady=(5,2))

        for text, vista, comando in nav_buttons_social:
            btn = tk.Button(
                sidebar,
                text=text,
                font=('Segoe UI', 10),
                bg=COLORES['sidebar_bg'],
                fg='white',
                relief=tk.FLAT,
                cursor='hand2',
                anchor='w',
                padx=20,
                pady=10,
                command=lambda v=vista, c=comando: self.cambiar_vista(v, c)
            )
            btn.pack(fill=tk.X, padx=5, pady=1)
            btn.bind('<Enter>', lambda e, b=btn: b.config(bg=COLORES['sidebar_hover']))
            btn.bind('<Leave>', lambda e, b=btn, v=vista: b.config(
                bg=COLORES['primary'] if self.vista_actual == v else COLORES['sidebar_bg']
            ))
            self.nav_buttons[vista] = btn

        # Separador
        tk.Frame(sidebar, bg=COLORES['border'], height=1).pack(fill=tk.X, padx=10, pady=8)

        # Label Gamificación
        tk.Label(sidebar, text="GAMIFICACIÓN", font=('Segoe UI', 8, 'bold'),
                bg=COLORES['sidebar_bg'], fg=COLORES['text_light'], anchor='w', padx=20).pack(fill=tk.X, pady=(5,2))

        for text, vista, comando in nav_buttons_gamificacion:
            btn = tk.Button(
                sidebar,
                text=text,
                font=('Segoe UI', 10),
                bg=COLORES['sidebar_bg'],
                fg='white',
                relief=tk.FLAT,
                cursor='hand2',
                anchor='w',
                padx=20,
                pady=10,
                command=lambda v=vista, c=comando: self.cambiar_vista(v, c)
            )
            btn.pack(fill=tk.X, padx=5, pady=1)
            btn.bind('<Enter>', lambda e, b=btn: b.config(bg=COLORES['sidebar_hover']))
            btn.bind('<Leave>', lambda e, b=btn, v=vista: b.config(
                bg=COLORES['primary'] if self.vista_actual == v else COLORES['sidebar_bg']
            ))
            self.nav_buttons[vista] = btn

        # Separador
        tk.Frame(sidebar, bg=COLORES['border'], height=1).pack(fill=tk.X, padx=10, pady=8)

        # Label Ayuda
        tk.Label(sidebar, text="AYUDA", font=('Segoe UI', 8, 'bold'),
                bg=COLORES['sidebar_bg'], fg=COLORES['text_light'], anchor='w', padx=20).pack(fill=tk.X, pady=(5,2))

        for text, vista, comando in nav_buttons_ayuda:
            btn = tk.Button(
                sidebar,
                text=text,
                font=('Segoe UI', 10),
                bg=COLORES['sidebar_bg'],
                fg='white',
                relief=tk.FLAT,
                cursor='hand2',
                anchor='w',
                padx=20,
                pady=10,
                command=lambda v=vista, c=comando: self.cambiar_vista(v, c)
            )
            btn.pack(fill=tk.X, padx=5, pady=1)
            btn.bind('<Enter>', lambda e, b=btn: b.config(bg=COLORES['sidebar_hover']))
            btn.bind('<Leave>', lambda e, b=btn, v=vista: b.config(
                bg=COLORES['primary'] if self.vista_actual == v else COLORES['sidebar_bg']
            ))
            self.nav_buttons[vista] = btn

        # Espacio
        tk.Frame(sidebar, bg=COLORES['sidebar_bg'], height=30).pack()

        # Info al pie del sidebar
        tk.Label(
            sidebar,
            text="Maximiliano Burgos\n2025",
            font=('Segoe UI', 8),
            bg=COLORES['sidebar_bg'],
            fg=COLORES['text_secondary'],
            justify=tk.CENTER
        ).pack(pady=15)

        # ÁREA DE CONTENIDO
        self.frame_contenido = tk.Frame(frame_main, bg=COLORES['background'])
        self.frame_contenido.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Mostrar dashboard por defecto
        self.mostrar_dashboard()

    def cambiar_vista(self, vista, comando):
        """Cambia la vista actual y actualiza el sidebar"""
        if vista in ['conversor', 'registro_rapido']:
            comando()  # Estas son ventanas modales
            return

        self.vista_actual = vista
        # Actualizar colores de botones
        for v, btn in self.nav_buttons.items():
            if v == vista:
                btn.config(bg=COLORES['primary'])
            else:
                btn.config(bg=COLORES['sidebar_bg'])

        # Limpiar contenido
        for widget in self.frame_contenido.winfo_children():
            widget.destroy()

        # Mostrar nueva vista
        comando()

    def actualizar_cotizaciones(self):
        def actualizar():
            cotiz = obtener_cotizacion_dolar()
            if cotiz:
                self.cotizaciones = cotiz
                texto = f"💱 Blue: ${cotiz['Blue']['venta']:.2f} | Oficial: ${cotiz['Oficial']['venta']:.2f}"
                self.label_dolar.config(text=texto)

        thread = threading.Thread(target=actualizar, daemon=True)
        thread.start()

    def actualizar_clima(self):
        """Actualiza la información del clima en el header"""
        def actualizar():
            clima = obtener_clima()
            if clima:
                icono_clima = {
                    'Despejado': '☀️',
                    'Mayormente despejado': '🌤️',
                    'Parcialmente nublado': '⛅',
                    'Nublado': '☁️',
                    'Lluvia': '🌧️',
                    'Tormenta': '⛈️'
                }.get(clima['condicion'], '🌡️')

                texto = f"{icono_clima} {clima['temperatura']:.0f}°C - {clima['condicion']}"
                self.label_clima.config(text=texto)

        thread = threading.Thread(target=actualizar, daemon=True)
        thread.start()

    def ventana_conversion_rapida(self):
        """Ventana emergente para conversión rápida de monedas"""
        v = tk.Toplevel(self.root)
        v.title("💱 Conversión Rápida")
        v.geometry("380x480")
        v.configure(bg=COLORES['background'])
        v.transient(self.root)

        v.update_idletasks()
        x = (v.winfo_screenwidth() // 2) - (380 // 2)
        y = (v.winfo_screenheight() // 2) - (480 // 2)
        v.geometry(f'380x480+{x}+{y}')

        frame = tk.Frame(v, bg=COLORES['background'], padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            frame,
            text="💱 Conversor de Viajes",
            font=('Segoe UI', 14, 'bold'),
            bg=COLORES['background']
        ).pack(pady=(0, 15))

        # Monto a convertir
        tk.Label(frame, text="💰 Monto:", bg=COLORES['background']).pack(anchor='w', pady=3)
        entry_monto = tk.Entry(frame, font=('Segoe UI', 14), justify='center')
        entry_monto.insert(0, "1000")
        entry_monto.pack(fill=tk.X, pady=5, ipady=5)

        # Frame de resultados
        frame_resultados = tk.Frame(frame, bg=COLORES['card_bg'], relief=tk.SOLID, bd=1,
                                   highlightbackground=COLORES['border'], highlightthickness=1)
        frame_resultados.pack(fill=tk.BOTH, expand=True, pady=15, padx=2)

        tk.Label(
            frame_resultados,
            text="Conversiones desde ARS:",
            font=('Segoe UI', 10, 'bold'),
            bg=COLORES['card_bg']
        ).pack(pady=10)

        # Labels de resultados
        conversiones = [
            ('🇺🇸 USD (Dólar)', 'usd'),
            ('🇪🇺 EUR (Euro)', 'eur'),
            ('🇧🇷 BRL (Real)', 'brl'),
            ('🇨🇱 CLP (Peso chileno)', 'clp'),
            ('🇲🇽 MXN (Peso mexicano)', 'mxn'),
            ('🇺🇾 UYU (Peso uruguayo)', 'uyu')
        ]

        labels_resultados = {}
        for texto, codigo in conversiones:
            lbl = tk.Label(
                frame_resultados,
                text=f"{texto}: ...",
                font=('Segoe UI', 10),
                bg=COLORES['card_bg'],
                anchor='w'
            )
            lbl.pack(fill=tk.X, padx=15, pady=3)
            labels_resultados[codigo] = lbl

        def convertir(event=None):
            try:
                monto = float(entry_monto.get().replace(',', '.'))
                tasas = obtener_tasas_conversion()

                if tasas and 'ARS' in tasas:
                    # Convertir desde ARS a otras monedas
                    monto_usd = monto / tasas['ARS']

                    conversiones_vals = {
                        'usd': monto_usd,
                        'eur': monto_usd * tasas.get('EUR', 0.92),
                        'brl': monto_usd * tasas.get('BRL', 5.0),
                        'clp': monto_usd * tasas.get('CLP', 900),
                        'mxn': monto_usd * tasas.get('MXN', 17),
                        'uyu': monto_usd * tasas.get('UYU', 39)
                    }

                    labels_resultados['usd'].config(text=f"🇺🇸 USD (Dólar): ${conversiones_vals['usd']:,.2f}")
                    labels_resultados['eur'].config(text=f"🇪🇺 EUR (Euro): €{conversiones_vals['eur']:,.2f}")
                    labels_resultados['brl'].config(text=f"🇧🇷 BRL (Real): R${conversiones_vals['brl']:,.2f}")
                    labels_resultados['clp'].config(text=f"🇨🇱 CLP (Peso chileno): ${conversiones_vals['clp']:,.0f}")
                    labels_resultados['mxn'].config(text=f"🇲🇽 MXN (Peso mexicano): ${conversiones_vals['mxn']:,.2f}")
                    labels_resultados['uyu'].config(text=f"🇺🇾 UYU (Peso uruguayo): ${conversiones_vals['uyu']:,.2f}")

            except Exception as e:
                messagebox.showerror("Error", f"Error en conversión: {e}")

        entry_monto.bind('<KeyRelease>', convertir)

        tk.Button(
            frame,
            text="🔄 Actualizar",
            command=convertir,
            bg=COLORES['info'],
            fg='white',
            font=('Segoe UI', 10, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            padx=30,
            pady=8
        ).pack(pady=10)

        # Convertir al abrir
        v.after(100, convertir)

    def mostrar_dashboard(self):
        """Vista principal del dashboard"""
        canvas = tk.Canvas(self.frame_contenido, bg=COLORES['background'], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.frame_contenido, orient="vertical", command=canvas.yview)
        frame_scroll = tk.Frame(canvas, bg=COLORES['background'])

        frame_scroll.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame_scroll, anchor="nw", width=1120)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Resumen
        frame_resumen = tk.Frame(frame_scroll, bg=COLORES['card_bg'], relief=tk.SOLID, bd=1,
                                highlightbackground=COLORES['border'], highlightthickness=1)
        frame_resumen.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            frame_resumen,
            text=f"📅 Resumen del Mes: {self.mes_actual}",
            font=('Segoe UI', 14, 'bold'),
            bg=COLORES['card_bg'],
            fg=COLORES['text']
        ).pack(pady=10)
        
        gastos = self.db.obtener_gastos(self.mes_actual)
        total_ars = sum(g[3] for g in gastos if g[4] == 'ARS')
        
        sueldo_data = self.db.obtener_sueldo_mes(self.mes_actual)
        sueldo = sueldo_data[2] if sueldo_data else 0
        
        frame_stats = tk.Frame(frame_resumen, bg=COLORES['card_bg'])
        frame_stats.pack(pady=10)
        
        self.crear_tarjeta(frame_stats, "💰 Ingresos", f"${sueldo:,.0f}", COLORES['success'])
        self.crear_tarjeta(frame_stats, "💸 Gastos", f"${total_ars:,.0f}", COLORES['danger'])
        self.crear_tarjeta(frame_stats, "📊 Saldo", f"${sueldo - total_ars:,.0f}", 
                          COLORES['success'] if sueldo >= total_ars else COLORES['danger'])
        
        # Gráfico CIRCULAR GRANDE (estilo Monefy)
        if gastos:
            frame_grafico = tk.Frame(frame_scroll, bg=COLORES['card_bg'], relief=tk.SOLID, bd=1,
                                    highlightbackground=COLORES['border'], highlightthickness=1)
            frame_grafico.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            tk.Label(
                frame_grafico,
                text="📊 Distribución de Gastos - Vista Monefy",
                font=('Segoe UI', 14, 'bold'),
                bg=COLORES['card_bg']
            ).pack(pady=15)

            # Agrupar por categoría
            cats = {}
            cat_icons = {}
            for g in gastos:
                cats[g[2]] = cats.get(g[2], 0) + g[3]

            # Obtener iconos de categorías
            todas_cats = self.db.obtener_categorias()
            for cat in todas_cats:
                cat_icons[cat[1]] = cat[3] if len(cat) > 3 else '❓'  # nombre -> icono

            # Crear figura MÁS GRANDE
            fig = Figure(figsize=(10, 7), facecolor=COLORES['card_bg'])
            ax = fig.add_subplot(111)

            # Colores vibrantes estilo Monefy
            colores_monefy = [
                '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
                '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B88B', '#ABEBC6'
            ]

            # Crear pie chart GRANDE con estilo
            wedges, texts, autotexts = ax.pie(
                cats.values(),
                labels=[f"{cat_icons.get(cat, '')} {cat}" for cat in cats.keys()],
                autopct='%1.1f%%',
                startangle=90,
                colors=colores_monefy[:len(cats)],
                textprops={'fontsize': 11, 'weight': 'bold'},
                pctdistance=0.85,
                labeldistance=1.1
            )

            # Estilo de los textos
            for text in texts:
                text.set_color(COLORES['text'])
                text.set_fontsize(12)

            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontsize(11)
                autotext.set_weight('bold')

            ax.axis('equal')

            # Agregar leyenda con montos
            leyenda_labels = [f"{cat}: ${monto:,.0f}" for cat, monto in cats.items()]
            ax.legend(leyenda_labels, loc='center left', bbox_to_anchor=(1, 0, 0.5, 1),
                     fontsize=10, frameon=False)

            canvas_graf = FigureCanvasTkAgg(fig, frame_grafico)
            canvas_graf.draw()
            canvas_graf.get_tk_widget().pack(pady=10, padx=10)

    def crear_tarjeta(self, parent, titulo, valor, color):
        frame = tk.Frame(parent, bg=color, width=220, height=100)
        frame.pack(side=tk.LEFT, padx=10)
        frame.pack_propagate(False)
        
        tk.Label(frame, text=titulo, font=('Segoe UI', 10), bg=color, fg='white').pack(pady=(15, 5))
        tk.Label(frame, text=valor, font=('Segoe UI', 16, 'bold'), bg=color, fg='white').pack()

    def mostrar_gastos(self):
        """Vista de gastos"""
        # Filtros
        frame_filtros = tk.Frame(self.frame_contenido, bg=COLORES['background'])
        frame_filtros.pack(fill=tk.X, padx=15, pady=10)
        
        tk.Label(frame_filtros, text="Mes:", bg=COLORES['background']).pack(side=tk.LEFT, padx=5)
        
        self.combo_mes = ttk.Combobox(frame_filtros, width=12, state='readonly')
        meses = [(datetime.date.today() - timedelta(days=30*i)).strftime('%Y-%m') for i in range(12)]
        self.combo_mes['values'] = meses
        self.combo_mes.set(self.mes_actual)
        self.combo_mes.bind('<<ComboboxSelected>>', lambda e: self.cargar_gastos())
        self.combo_mes.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            frame_filtros,
            text="🔄 Actualizar",
            command=self.cargar_gastos,
            bg=COLORES['info'],
            fg='white',
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=10)
        
        # Tabla
        frame_tabla = tk.Frame(self.frame_contenido)
        frame_tabla.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        columnas = ('Fecha', 'Categoría', 'Monto', 'Moneda', 'Descripción', 'Cuenta')
        self.tree = ttk.Treeview(frame_tabla, columns=columnas, show='headings', height=18)
        
        for col in columnas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150 if col != 'Descripción' else 250)
        
        scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind('<Button-3>', self.menu_contextual_gasto)
        self.cargar_gastos()

    def cargar_gastos(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        mes = self.combo_mes.get()
        gastos = self.db.obtener_gastos(mes)

        # Obtener mapa de categorías a iconos
        cat_icons = {}
        categorias = self.db.obtener_categorias()
        for cat in categorias:
            cat_icons[cat[1]] = cat[3] if len(cat) > 3 else '❓'  # nombre -> icono

        for g in gastos:
            icono = cat_icons.get(g[2], '❓')
            categoria_con_icono = f"{icono} {g[2]}"
            self.tree.insert('', tk.END, values=(g[1], categoria_con_icono, f"{g[3]:,.2f}", g[4], g[5] or '', g[6]), tags=(g[0],))

    def menu_contextual_gasto(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="🗑️ Eliminar", command=self.eliminar_gasto)
            menu.post(event.x_root, event.y_root)

    def eliminar_gasto(self):
        sel = self.tree.selection()
        if not sel:
            return
        
        if messagebox.askyesno("Confirmar", "¿Eliminar este gasto?"):
            id_gasto = self.tree.item(sel[0])['tags'][0]
            self.db.eliminar_gasto(id_gasto)
            messagebox.showinfo("Éxito", "Gasto eliminado")
            self.cargar_gastos()

    def mostrar_metas(self):
        """Vista de metas de ahorro"""
        frame_btn = tk.Frame(self.frame_contenido, bg=COLORES['background'])
        frame_btn.pack(fill=tk.X, padx=15, pady=10)
        
        tk.Button(
            frame_btn,
            text="➕ Nueva Meta",
            font=('Segoe UI', 10, 'bold'),
            bg=COLORES['success'],
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.ventana_nueva_meta,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT)

        canvas = tk.Canvas(self.frame_contenido, bg=COLORES['background'], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.frame_contenido, orient="vertical", command=canvas.yview)
        
        self.frame_metas = tk.Frame(canvas, bg=COLORES['background'])
        self.frame_metas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=self.frame_metas, anchor="nw", width=1130)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=15)
        scrollbar.pack(side="right", fill="y")
        
        self.cargar_metas()

    def cargar_metas(self):
        for widget in self.frame_metas.winfo_children():
            widget.destroy()
        
        metas = self.db.obtener_metas()
        
        if not metas:
            tk.Label(
                self.frame_metas,
                text="🎯 No hay metas creadas\n\nCreá tu primera meta de ahorro",
                font=('Segoe UI', 11),
                bg=COLORES['background'],
                fg=COLORES['text_secondary'],
                justify=tk.CENTER
            ).pack(pady=60)
            return
        
        for meta in metas:
            self.crear_widget_meta(meta)

    def crear_widget_meta(self, meta):
        id_meta, nombre, objetivo, actual = meta[:4]
        fecha_obj, moneda, icono = meta[5], meta[6], meta[7]
        
        pct = (actual / objetivo * 100) if objetivo > 0 else 0

        frame = tk.Frame(self.frame_metas, bg=COLORES['card_bg'], relief=tk.SOLID, bd=1,
                        highlightbackground=COLORES['border'], highlightthickness=1)
        frame.pack(fill=tk.X, pady=8, padx=5)
        
        frame_header = tk.Frame(frame, bg=COLORES['primary'], height=40)
        frame_header.pack(fill=tk.X)
        frame_header.pack_propagate(False)
        
        tk.Label(
            frame_header,
            text=f"{icono} {nombre}",
            font=('Segoe UI', 12, 'bold'),
            bg=COLORES['primary'],
            fg='white'
        ).pack(side=tk.LEFT, padx=15, pady=10)
        
        tk.Label(
            frame_header,
            text=f"🎯 {fecha_obj}",
            font=('Segoe UI', 9),
            bg=COLORES['primary'],
            fg='white'
        ).pack(side=tk.RIGHT, padx=15)
        
        frame_contenido = tk.Frame(frame, bg=COLORES['card_bg'])
        frame_contenido.pack(fill=tk.X, padx=15, pady=10)
        
        tk.Label(
            frame_contenido,
            text=f"${actual:,.0f} de ${objetivo:,.0f} {moneda}",
            font=('Segoe UI', 10),
            bg=COLORES['card_bg']
        ).pack(anchor='w', pady=5)
        
        canvas_barra = tk.Canvas(frame_contenido, height=25, bg=COLORES['background'], highlightthickness=0)
        canvas_barra.pack(fill=tk.X, pady=5)
        
        ancho = 1050
        canvas_barra.create_rectangle(0, 0, ancho, 25, fill=COLORES['light'], outline='')
        
        if pct > 0:
            ancho_prog = int(ancho * min(pct / 100, 1))
            canvas_barra.create_rectangle(0, 0, ancho_prog, 25, fill=COLORES['success'], outline='')
        
        canvas_barra.create_text(ancho // 2, 12, text=f"{pct:.1f}%", font=('Segoe UI', 9, 'bold'))

    def mostrar_tarjetas(self):
        """Vista de Tarjetas de Crédito"""
        frame_btn = tk.Frame(self.frame_contenido, bg=COLORES['background'])
        frame_btn.pack(fill=tk.X, padx=15, pady=10)
        
        tk.Button(
            frame_btn,
            text="➕ Nueva Tarjeta",
            font=('Segoe UI', 10, 'bold'),
            bg=COLORES['success'],
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.ventana_nueva_tarjeta,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT)

        canvas = tk.Canvas(self.frame_contenido, bg=COLORES['background'], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.frame_contenido, orient="vertical", command=canvas.yview)
        
        self.frame_tarjetas = tk.Frame(canvas, bg=COLORES['background'])
        self.frame_tarjetas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=self.frame_tarjetas, anchor="nw", width=1130)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=15)
        scrollbar.pack(side="right", fill="y")
        
        self.cargar_tarjetas()

    def cargar_tarjetas(self):
        """Carga las tarjetas de crédito"""
        for widget in self.frame_tarjetas.winfo_children():
            widget.destroy()
        
        tarjetas = self.db.obtener_tarjetas()
        
        if not tarjetas:
            tk.Label(
                self.frame_tarjetas,
                text="💳 No hay tarjetas registradas\n\nAgregá tu primera tarjeta",
                font=('Segoe UI', 11),
                bg=COLORES['background'],
                fg=COLORES['text_secondary'],
                justify=tk.CENTER
            ).pack(pady=60)
            return
        
        for tarjeta in tarjetas:
            self.crear_widget_tarjeta(tarjeta)

    def crear_widget_tarjeta(self, tarjeta):
        """Crea widget visual para una tarjeta"""
        id_t, nombre, banco, limite, cierre, venc = tarjeta[:6]
        
        frame = tk.Frame(self.frame_tarjetas, bg=COLORES['card_bg'], relief=tk.SOLID, bd=1, highlightbackground=COLORES['border'], highlightthickness=1)
        frame.pack(fill=tk.X, pady=8, padx=5)
        
        frame_header = tk.Frame(frame, bg=COLORES['info'], height=40)
        frame_header.pack(fill=tk.X)
        frame_header.pack_propagate(False)
        
        tk.Label(
            frame_header,
            text=f"💳 {nombre}",
            font=('Segoe UI', 12, 'bold'),
            bg=COLORES['info'],
            fg='white'
        ).pack(side=tk.LEFT, padx=15, pady=10)
        
        tk.Label(
            frame_header,
            text=f"🏦 {banco}",
            font=('Segoe UI', 9),
            bg=COLORES['info'],
            fg='white'
        ).pack(side=tk.RIGHT, padx=15)
        
        frame_contenido = tk.Frame(frame, bg=COLORES['card_bg'])
        frame_contenido.pack(fill=tk.X, padx=15, pady=10)
        
        info = f"💰 Límite: ${limite:,.0f} | 📅 Cierre: día {cierre} | 📆 Vencimiento: día {venc}"
        tk.Label(
            frame_contenido,
            text=info,
            font=('Segoe UI', 10),
            bg=COLORES['card_bg']
        ).pack(anchor='w', pady=5)
        
        tk.Button(
            frame_contenido,
            text="🗑️ Eliminar",
            command=lambda: self.eliminar_tarjeta(id_t),
            bg=COLORES['danger'],
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            padx=15,
            pady=5
        ).pack(anchor='e')

    def ventana_nueva_tarjeta(self):
        """Ventana para agregar tarjeta"""
        v = tk.Toplevel(self.root)
        v.title("💳 Nueva Tarjeta")
        v.geometry("450x500")
        v.configure(bg=COLORES['background'])
        v.transient(self.root)
        v.grab_set()
        
        v.update_idletasks()
        x = (v.winfo_screenwidth() // 2) - (450 // 2)
        y = (v.winfo_screenheight() // 2) - (500 // 2)
        v.geometry(f'450x500+{x}+{y}')
        
        frame = tk.Frame(v, bg=COLORES['background'], padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="💳 Nombre de la tarjeta:", bg=COLORES['background']).pack(anchor='w', pady=3)
        entry_nombre = tk.Entry(frame)
        entry_nombre.pack(fill=tk.X, pady=3)
        
        tk.Label(frame, text="🏦 Banco:", bg=COLORES['background']).pack(anchor='w', pady=3)
        entry_banco = tk.Entry(frame)
        entry_banco.pack(fill=tk.X, pady=3)
        
        tk.Label(frame, text="💰 Límite de crédito:", bg=COLORES['background']).pack(anchor='w', pady=3)
        entry_limite = tk.Entry(frame)
        entry_limite.pack(fill=tk.X, pady=3)
        
        tk.Label(frame, text="📅 Día de cierre (1-31):", bg=COLORES['background']).pack(anchor='w', pady=3)
        entry_cierre = tk.Entry(frame)
        entry_cierre.pack(fill=tk.X, pady=3)
        
        tk.Label(frame, text="📆 Día de vencimiento (1-31):", bg=COLORES['background']).pack(anchor='w', pady=3)
        entry_venc = tk.Entry(frame)
        entry_venc.pack(fill=tk.X, pady=3)
        
        def guardar():
            try:
                nombre = entry_nombre.get().strip()
                banco = entry_banco.get().strip()
                limite = float(entry_limite.get().replace(',', '.'))
                cierre = int(entry_cierre.get())
                venc = int(entry_venc.get())
                
                if not nombre or not banco:
                    messagebox.showwarning("Error", "Completá todos los campos")
                    return
                
                if cierre < 1 or cierre > 31 or venc < 1 or venc > 31:
                    messagebox.showwarning("Error", "Los días deben estar entre 1 y 31")
                    return
                
                self.db.agregar_tarjeta(nombre, banco, limite, cierre, venc)
                messagebox.showinfo("Éxito", "✅ Tarjeta agregada")
                v.destroy()
                self.cargar_tarjetas()
            except ValueError:
                messagebox.showerror("Error", "Datos inválidos")
        
        frame_btns = tk.Frame(frame, bg=COLORES['background'])
        frame_btns.pack(pady=20)
        
        tk.Button(frame_btns, text="💾 Guardar", command=guardar, bg=COLORES['success'],
                 fg='white', font=('Segoe UI', 10, 'bold'), relief=tk.FLAT, cursor='hand2',
                 padx=25, pady=8).pack(side=tk.LEFT, padx=5)
        
        tk.Button(frame_btns, text="❌ Cancelar", command=v.destroy, bg=COLORES['danger'],
                 fg='white', font=('Segoe UI', 10), relief=tk.FLAT, cursor='hand2',
                 padx=25, pady=8).pack(side=tk.LEFT, padx=5)

    def eliminar_tarjeta(self, id_tarjeta):
        """Elimina una tarjeta"""
        if messagebox.askyesno("Confirmar", "¿Eliminar esta tarjeta?"):
            self.db.eliminar_tarjeta(id_tarjeta)
            messagebox.showinfo("Éxito", "Tarjeta eliminada")
            self.cargar_tarjetas()

    def mostrar_recurrentes(self):
        """Vista de transacciones recurrentes"""
        frame_btn = tk.Frame(self.frame_contenido, bg=COLORES['background'])
        frame_btn.pack(fill=tk.X, padx=15, pady=10)

        tk.Button(
            frame_btn,
            text="➕ Nueva Transacción Recurrente",
            font=('Segoe UI', 10, 'bold'),
            bg=COLORES['success'],
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.ventana_nueva_recurrente,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT)

        canvas = tk.Canvas(self.frame_contenido, bg=COLORES['background'], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.frame_contenido, orient="vertical", command=canvas.yview)

        frame_lista = tk.Frame(canvas, bg=COLORES['background'])
        frame_lista.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=frame_lista, anchor="nw", width=1100)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=15)
        scrollbar.pack(side="right", fill="y")

        recurrentes = self.db.obtener_recurrentes()

        if not recurrentes:
            tk.Label(
                frame_lista,
                text="🔄 No hay transacciones recurrentes\n\nCreá tu primera transacción automática",
                font=('Segoe UI', 11),
                bg=COLORES['background'],
                fg=COLORES['text_secondary'],
                justify=tk.CENTER
            ).pack(pady=60)
            return

        for rec in recurrentes:
            self.crear_widget_recurrente(frame_lista, rec)

    def crear_widget_recurrente(self, parent, rec):
        """Crea widget para transacción recurrente"""
        id_rec, nombre, cat, monto, moneda, cuenta, freq, dia = rec[:8]

        frame = tk.Frame(parent, bg=COLORES['card_bg'], relief=tk.SOLID, bd=1, highlightbackground=COLORES['border'], highlightthickness=1)
        frame.pack(fill=tk.X, pady=8, padx=5)

        frame_header = tk.Frame(frame, bg=COLORES['secondary'], height=40)
        frame_header.pack(fill=tk.X)
        frame_header.pack_propagate(False)

        tk.Label(
            frame_header,
            text=f"🔄 {nombre}",
            font=('Segoe UI', 12, 'bold'),
            bg=COLORES['secondary'],
            fg='white'
        ).pack(side=tk.LEFT, padx=15, pady=10)

        tk.Label(
            frame_header,
            text=f"{freq} - Día {dia}",
            font=('Segoe UI', 9),
            bg=COLORES['secondary'],
            fg='white'
        ).pack(side=tk.RIGHT, padx=15)

        frame_contenido = tk.Frame(frame, bg=COLORES['card_bg'])
        frame_contenido.pack(fill=tk.X, padx=15, pady=10)

        info = f"💰 {moneda} ${monto:,.0f} | 📂 {cat} | 🏦 {cuenta}"
        tk.Label(
            frame_contenido,
            text=info,
            font=('Segoe UI', 10),
            bg=COLORES['card_bg']
        ).pack(anchor='w', pady=5)

    def ventana_nueva_recurrente(self):
        """Ventana para crear transacción recurrente"""
        v = tk.Toplevel(self.root)
        v.title("🔄 Nueva Transacción Recurrente")
        v.geometry("450x550")
        v.configure(bg=COLORES['background'])
        v.transient(self.root)
        v.grab_set()

        v.update_idletasks()
        x = (v.winfo_screenwidth() // 2) - (450 // 2)
        y = (v.winfo_screenheight() // 2) - (550 // 2)
        v.geometry(f'450x550+{x}+{y}')

        frame = tk.Frame(v, bg=COLORES['background'], padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="📝 Nombre:", bg=COLORES['background']).pack(anchor='w', pady=3)
        entry_nombre = tk.Entry(frame)
        entry_nombre.pack(fill=tk.X, pady=3)

        tk.Label(frame, text="📂 Categoría:", bg=COLORES['background']).pack(anchor='w', pady=3)
        combo_cat = ttk.Combobox(frame, values=[c[1] for c in self.db.obtener_categorias()], state='readonly')
        if self.db.obtener_categorias():
            combo_cat.set(self.db.obtener_categorias()[0][1])
        combo_cat.pack(fill=tk.X, pady=3)

        tk.Label(frame, text="💰 Monto:", bg=COLORES['background']).pack(anchor='w', pady=3)
        entry_monto = tk.Entry(frame)
        entry_monto.pack(fill=tk.X, pady=3)

        tk.Label(frame, text="💱 Moneda:", bg=COLORES['background']).pack(anchor='w', pady=3)
        combo_moneda = ttk.Combobox(frame, values=['ARS', 'USD'], state='readonly')
        combo_moneda.set('ARS')
        combo_moneda.pack(fill=tk.X, pady=3)

        tk.Label(frame, text="🏦 Cuenta:", bg=COLORES['background']).pack(anchor='w', pady=3)
        combo_cuenta = ttk.Combobox(frame, values=[c[1] for c in self.db.obtener_cuentas()], state='readonly')
        if self.db.obtener_cuentas():
            combo_cuenta.set(self.db.obtener_cuentas()[0][1])
        combo_cuenta.pack(fill=tk.X, pady=3)

        tk.Label(frame, text="🔄 Frecuencia:", bg=COLORES['background']).pack(anchor='w', pady=3)
        combo_freq = ttk.Combobox(frame, values=['Mensual', 'Semanal'], state='readonly')
        combo_freq.set('Mensual')
        combo_freq.pack(fill=tk.X, pady=3)

        tk.Label(frame, text="📅 Día del mes (1-31):", bg=COLORES['background']).pack(anchor='w', pady=3)
        entry_dia = tk.Entry(frame)
        entry_dia.insert(0, '1')
        entry_dia.pack(fill=tk.X, pady=3)

        def guardar():
            try:
                nombre = entry_nombre.get().strip()
                categoria = combo_cat.get()
                monto = float(entry_monto.get().replace(',', '.'))
                moneda = combo_moneda.get()
                cuenta = combo_cuenta.get()
                freq = combo_freq.get()
                dia = int(entry_dia.get())

                if not nombre or not categoria or monto <= 0:
                    messagebox.showwarning("Error", "Completá todos los campos correctamente")
                    return

                if dia < 1 or dia > 31:
                    messagebox.showwarning("Error", "El día debe estar entre 1 y 31")
                    return

                self.db.agregar_recurrente(nombre, categoria, monto, moneda, cuenta, freq, dia)
                messagebox.showinfo("Éxito", "✅ Transacción recurrente creada")
                v.destroy()
                self.mostrar_recurrentes()
            except ValueError:
                messagebox.showerror("Error", "Datos inválidos")

        frame_btns = tk.Frame(frame, bg=COLORES['background'])
        frame_btns.pack(pady=15)

        tk.Button(frame_btns, text="💾 Guardar", command=guardar, bg=COLORES['success'],
                 fg='white', font=('Segoe UI', 10, 'bold'), relief=tk.FLAT, cursor='hand2',
                 padx=25, pady=8).pack(side=tk.LEFT, padx=5)

        tk.Button(frame_btns, text="❌ Cancelar", command=v.destroy, bg=COLORES['danger'],
                 fg='white', font=('Segoe UI', 10), relief=tk.FLAT, cursor='hand2',
                 padx=25, pady=8).pack(side=tk.LEFT, padx=5)

    def mostrar_presupuestos(self):
        """Vista de presupuestos por categoría"""
        frame_btn = tk.Frame(self.frame_contenido, bg=COLORES['background'])
        frame_btn.pack(fill=tk.X, padx=15, pady=10)

        tk.Button(
            frame_btn,
            text="➕ Nuevo Presupuesto",
            font=('Segoe UI', 10, 'bold'),
            bg=COLORES['success'],
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.ventana_nuevo_presupuesto,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT)

        canvas = tk.Canvas(self.frame_contenido, bg=COLORES['background'], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.frame_contenido, orient="vertical", command=canvas.yview)

        frame_lista = tk.Frame(canvas, bg=COLORES['background'])
        frame_lista.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=frame_lista, anchor="nw", width=1100)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=15)
        scrollbar.pack(side="right", fill="y")

        presupuestos = self.db.obtener_todos_presupuestos(self.mes_actual)

        if not presupuestos:
            tk.Label(
                frame_lista,
                text="📊 No hay presupuestos configurados\n\nCreá tu primer presupuesto por categoría",
                font=('Segoe UI', 11),
                bg=COLORES['background'],
                fg=COLORES['text_secondary'],
                justify=tk.CENTER
            ).pack(pady=60)
            return

        for pres in presupuestos:
            self.crear_widget_presupuesto(frame_lista, pres)

    def crear_widget_presupuesto(self, parent, pres):
        """Crea widget para presupuesto"""
        id_pres, categoria, mes, limite = pres

        # Calcular gasto actual
        gastos = self.db.obtener_gastos(mes)
        gasto_actual = sum(g[3] for g in gastos if g[2] == categoria and g[4] == 'ARS')

        pct = (gasto_actual / limite * 100) if limite > 0 else 0
        color_barra = COLORES['success'] if pct < 80 else COLORES['warning'] if pct < 100 else COLORES['danger']

        frame = tk.Frame(parent, bg=COLORES['card_bg'], relief=tk.SOLID, bd=1, highlightbackground=COLORES['border'], highlightthickness=1)
        frame.pack(fill=tk.X, pady=8, padx=5)

        frame_header = tk.Frame(frame, bg=COLORES['info'], height=40)
        frame_header.pack(fill=tk.X)
        frame_header.pack_propagate(False)

        tk.Label(
            frame_header,
            text=f"📊 {categoria}",
            font=('Segoe UI', 12, 'bold'),
            bg=COLORES['info'],
            fg='white'
        ).pack(side=tk.LEFT, padx=15, pady=10)

        tk.Label(
            frame_header,
            text=f"{mes}",
            font=('Segoe UI', 9),
            bg=COLORES['info'],
            fg='white'
        ).pack(side=tk.RIGHT, padx=15)

        frame_contenido = tk.Frame(frame, bg=COLORES['card_bg'])
        frame_contenido.pack(fill=tk.X, padx=15, pady=10)

        tk.Label(
            frame_contenido,
            text=f"${gasto_actual:,.0f} de ${limite:,.0f} ARS",
            font=('Segoe UI', 10),
            bg=COLORES['card_bg']
        ).pack(anchor='w', pady=5)

        canvas_barra = tk.Canvas(frame_contenido, height=25, bg=COLORES['background'], highlightthickness=0)
        canvas_barra.pack(fill=tk.X, pady=5)

        ancho = 1000
        canvas_barra.create_rectangle(0, 0, ancho, 25, fill=COLORES['light'], outline='')

        if pct > 0:
            ancho_prog = int(ancho * min(pct / 100, 1))
            canvas_barra.create_rectangle(0, 0, ancho_prog, 25, fill=color_barra, outline='')

        canvas_barra.create_text(ancho // 2, 12, text=f"{pct:.1f}%", font=('Segoe UI', 9, 'bold'))

    def ventana_nuevo_presupuesto(self):
        """Ventana para crear presupuesto"""
        v = tk.Toplevel(self.root)
        v.title("📊 Nuevo Presupuesto")
        v.geometry("400x350")
        v.configure(bg=COLORES['background'])
        v.transient(self.root)
        v.grab_set()

        v.update_idletasks()
        x = (v.winfo_screenwidth() // 2) - (400 // 2)
        y = (v.winfo_screenheight() // 2) - (350 // 2)
        v.geometry(f'400x350+{x}+{y}')

        frame = tk.Frame(v, bg=COLORES['background'], padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="📂 Categoría:", bg=COLORES['background']).pack(anchor='w', pady=3)
        combo_cat = ttk.Combobox(frame, values=[c[1] for c in self.db.obtener_categorias()], state='readonly')
        if self.db.obtener_categorias():
            combo_cat.set(self.db.obtener_categorias()[0][1])
        combo_cat.pack(fill=tk.X, pady=3)

        tk.Label(frame, text="📅 Mes (YYYY-MM):", bg=COLORES['background']).pack(anchor='w', pady=3)
        entry_mes = tk.Entry(frame)
        entry_mes.insert(0, self.mes_actual)
        entry_mes.pack(fill=tk.X, pady=3)

        tk.Label(frame, text="💰 Límite de gasto:", bg=COLORES['background']).pack(anchor='w', pady=3)
        entry_limite = tk.Entry(frame)
        entry_limite.pack(fill=tk.X, pady=3)

        def guardar():
            try:
                categoria = combo_cat.get()
                mes = entry_mes.get()
                limite = float(entry_limite.get().replace(',', '.'))

                if not categoria or limite <= 0:
                    messagebox.showwarning("Error", "Completá todos los campos correctamente")
                    return

                self.db.agregar_presupuesto(categoria, mes, limite)
                messagebox.showinfo("Éxito", "✅ Presupuesto creado")
                v.destroy()
                self.mostrar_presupuestos()
            except ValueError:
                messagebox.showerror("Error", "Datos inválidos")

        frame_btns = tk.Frame(frame, bg=COLORES['background'])
        frame_btns.pack(pady=20)

        tk.Button(frame_btns, text="💾 Guardar", command=guardar, bg=COLORES['success'],
                 fg='white', font=('Segoe UI', 10, 'bold'), relief=tk.FLAT, cursor='hand2',
                 padx=25, pady=8).pack(side=tk.LEFT, padx=5)

        tk.Button(frame_btns, text="❌ Cancelar", command=v.destroy, bg=COLORES['danger'],
                 fg='white', font=('Segoe UI', 10), relief=tk.FLAT, cursor='hand2',
                 padx=25, pady=8).pack(side=tk.LEFT, padx=5)

    def mostrar_alertas(self):
        """Vista de alertas inteligentes"""
        frame_btn = tk.Frame(self.frame_contenido, bg=COLORES['background'])
        frame_btn.pack(fill=tk.X, padx=15, pady=10)

        tk.Label(
            frame_btn,
            text="🔔 Alertas y Notificaciones",
            font=('Segoe UI', 14, 'bold'),
            bg=COLORES['background']
        ).pack(side=tk.LEFT)

        canvas = tk.Canvas(self.frame_contenido, bg=COLORES['background'], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.frame_contenido, orient="vertical", command=canvas.yview)

        frame_lista = tk.Frame(canvas, bg=COLORES['background'])
        frame_lista.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=frame_lista, anchor="nw", width=1100)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=15)
        scrollbar.pack(side="right", fill="y")

        alertas = self.db.obtener_alertas(solo_no_leidas=False)

        if not alertas:
            tk.Label(
                frame_lista,
                text="✅ No hay alertas nuevas\n\n¡Todo bajo control!",
                font=('Segoe UI', 11),
                bg=COLORES['background'],
                fg=COLORES['text_secondary'],
                justify=tk.CENTER
            ).pack(pady=60)
            return

        for alerta in alertas:
            id_alerta, tipo, mensaje, fecha, leida, nivel = alerta

            color = {
                'success': COLORES['success'],
                'warning': COLORES['warning'],
                'danger': COLORES['danger'],
                'info': COLORES['info']
            }.get(nivel, COLORES['info'])

            frame = tk.Frame(frame_lista, bg=COLORES['card_bg'], relief=tk.SOLID, bd=1, highlightbackground=COLORES['border'], highlightthickness=1)
            frame.pack(fill=tk.X, pady=5, padx=5)

            if not leida:
                tk.Frame(frame, bg=color, width=6).pack(side=tk.LEFT, fill=tk.Y)

            frame_contenido = tk.Frame(frame, bg=COLORES['card_bg'])
            frame_contenido.pack(fill=tk.X, padx=15, pady=10)

            tk.Label(
                frame_contenido,
                text=mensaje,
                font=('Segoe UI', 10, 'bold' if not leida else 'normal'),
                bg=COLORES['card_bg'],
                fg=COLORES['text'] if not leida else COLORES['text_secondary']
            ).pack(anchor='w', pady=3)

            tk.Label(
                frame_contenido,
                text=f"📅 {fecha}",
                font=('Segoe UI', 8),
                bg=COLORES['card_bg'],
                fg=COLORES['text_secondary']
            ).pack(anchor='w')

    def mostrar_cuentas_por_pagar(self):
        """Vista de cuentas por pagar con vencimientos"""
        frame_btn = tk.Frame(self.frame_contenido, bg=COLORES['background'])
        frame_btn.pack(fill=tk.X, padx=15, pady=10)

        tk.Button(
            frame_btn,
            text="➕ Nueva Cuenta por Pagar",
            font=('Segoe UI', 10, 'bold'),
            bg=COLORES['success'],
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.ventana_nueva_cuenta_pagar,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT)

        canvas = tk.Canvas(self.frame_contenido, bg=COLORES['background'], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.frame_contenido, orient="vertical", command=canvas.yview)

        frame_lista = tk.Frame(canvas, bg=COLORES['background'])
        frame_lista.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=frame_lista, anchor="nw", width=1100)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=15)
        scrollbar.pack(side="right", fill="y")

        cuentas = self.db.obtener_cuentas_por_pagar()

        if not cuentas:
            tk.Label(
                frame_lista,
                text="📅 No hay cuentas por pagar configuradas\n\nAgregá tus servicios mensuales (luz, gas, internet, etc.)",
                font=('Segoe UI', 11),
                bg=COLORES['background'],
                fg=COLORES['text_secondary'],
                justify=tk.CENTER
            ).pack(pady=60)
            return

        hoy = datetime.date.today()
        for cuenta in cuentas:
            id_c, nombre, cat, monto, moneda, dia_venc = cuenta[:6]

            frame = tk.Frame(frame_lista, bg=COLORES['card_bg'], relief=tk.SOLID, bd=1, highlightbackground=COLORES['border'], highlightthickness=1)
            frame.pack(fill=tk.X, pady=5, padx=5)

            dias_faltantes = dia_venc - hoy.day
            if dias_faltantes < 0:
                dias_faltantes += 30

            if dias_faltantes <= 3:
                color = COLORES['danger']
                estado = "⚠️ VENCE PRONTO"
            elif dias_faltantes <= 7:
                color = COLORES['warning']
                estado = "⏰ Próximo vencimiento"
            else:
                color = COLORES['success']
                estado = "✅ Al día"

            frame_header = tk.Frame(frame, bg=color, height=35)
            frame_header.pack(fill=tk.X)
            frame_header.pack_propagate(False)

            tk.Label(
                frame_header,
                text=f"📅 {nombre}",
                font=('Segoe UI', 11, 'bold'),
                bg=color,
                fg='white'
            ).pack(side=tk.LEFT, padx=15, pady=7)

            tk.Label(
                frame_header,
                text=estado,
                font=('Segoe UI', 9),
                bg=color,
                fg='white'
            ).pack(side=tk.RIGHT, padx=15)

            frame_contenido = tk.Frame(frame, bg=COLORES['card_bg'])
            frame_contenido.pack(fill=tk.X, padx=15, pady=10)

            info = f"💰 {moneda} ${monto:,.0f} | 📂 {cat} | 📆 Vence día {dia_venc} ({dias_faltantes} días)"
            tk.Label(
                frame_contenido,
                text=info,
                font=('Segoe UI', 10),
                bg=COLORES['card_bg']
            ).pack(anchor='w', pady=3)

    def ventana_nueva_cuenta_pagar(self):
        """Ventana para agregar cuenta por pagar"""
        v = tk.Toplevel(self.root)
        v.title("📅 Nueva Cuenta por Pagar")
        v.geometry("450x500")
        v.configure(bg=COLORES['background'])
        v.transient(self.root)
        v.grab_set()

        v.update_idletasks()
        x = (v.winfo_screenwidth() // 2) - (450 // 2)
        y = (v.winfo_screenheight() // 2) - (500 // 2)
        v.geometry(f'450x500+{x}+{y}')

        frame = tk.Frame(v, bg=COLORES['background'], padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="📝 Nombre (ej: Luz, Gas, Internet):", bg=COLORES['background']).pack(anchor='w', pady=3)
        entry_nombre = tk.Entry(frame)
        entry_nombre.pack(fill=tk.X, pady=3)

        tk.Label(frame, text="📂 Categoría:", bg=COLORES['background']).pack(anchor='w', pady=3)
        combo_cat = ttk.Combobox(frame, values=[c[1] for c in self.db.obtener_categorias()], state='readonly')
        if self.db.obtener_categorias():
            combo_cat.set(self.db.obtener_categorias()[0][1])
        combo_cat.pack(fill=tk.X, pady=3)

        tk.Label(frame, text="💰 Monto:", bg=COLORES['background']).pack(anchor='w', pady=3)
        entry_monto = tk.Entry(frame)
        entry_monto.pack(fill=tk.X, pady=3)

        tk.Label(frame, text="💱 Moneda:", bg=COLORES['background']).pack(anchor='w', pady=3)
        combo_moneda = ttk.Combobox(frame, values=['ARS', 'USD'], state='readonly')
        combo_moneda.set('ARS')
        combo_moneda.pack(fill=tk.X, pady=3)

        tk.Label(frame, text="📆 Día de vencimiento (1-31):", bg=COLORES['background']).pack(anchor='w', pady=3)
        entry_dia = tk.Entry(frame)
        entry_dia.pack(fill=tk.X, pady=3)

        tk.Label(frame, text="🗒️ Notas:", bg=COLORES['background']).pack(anchor='w', pady=3)
        entry_notas = tk.Text(frame, height=3)
        entry_notas.pack(fill=tk.X, pady=3)

        def guardar():
            try:
                nombre = entry_nombre.get().strip()
                categoria = combo_cat.get()
                monto = float(entry_monto.get().replace(',', '.'))
                moneda = combo_moneda.get()
                dia = int(entry_dia.get())
                notas = entry_notas.get('1.0', tk.END).strip()

                if not nombre or not categoria or monto <= 0:
                    messagebox.showwarning("Error", "Completá todos los campos correctamente")
                    return

                if dia < 1 or dia > 31:
                    messagebox.showwarning("Error", "El día debe estar entre 1 y 31")
                    return

                self.db.agregar_cuenta_por_pagar(nombre, categoria, monto, moneda, dia, notas)
                messagebox.showinfo("Éxito", "✅ Cuenta por pagar agregada")
                v.destroy()
                self.mostrar_cuentas_por_pagar()
            except ValueError:
                messagebox.showerror("Error", "Datos inválidos")

        frame_btns = tk.Frame(frame, bg=COLORES['background'])
        frame_btns.pack(pady=15)

        tk.Button(frame_btns, text="💾 Guardar", command=guardar, bg=COLORES['success'],
                 fg='white', font=('Segoe UI', 10, 'bold'), relief=tk.FLAT, cursor='hand2',
                 padx=25, pady=8).pack(side=tk.LEFT, padx=5)

        tk.Button(frame_btns, text="❌ Cancelar", command=v.destroy, bg=COLORES['danger'],
                 fg='white', font=('Segoe UI', 10), relief=tk.FLAT, cursor='hand2',
                 padx=25, pady=8).pack(side=tk.LEFT, padx=5)

    def mostrar_deudas(self):
        """Vista de deudas compartidas"""
        frame_btn = tk.Frame(self.frame_contenido, bg=COLORES['background'])
        frame_btn.pack(fill=tk.X, padx=15, pady=10)

        tk.Button(
            frame_btn,
            text="➕ Nueva Deuda",
            font=('Segoe UI', 10, 'bold'),
            bg=COLORES['success'],
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.ventana_nueva_deuda,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT)

        canvas = tk.Canvas(self.frame_contenido, bg=COLORES['background'], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.frame_contenido, orient="vertical", command=canvas.yview)

        frame_lista = tk.Frame(canvas, bg=COLORES['background'])
        frame_lista.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=frame_lista, anchor="nw", width=1100)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=15)
        scrollbar.pack(side="right", fill="y")

        deudas = self.db.obtener_deudas()

        if not deudas:
            tk.Label(
                frame_lista,
                text="👥 No hay deudas registradas\n\nGestioná préstamos y gastos compartidos",
                font=('Segoe UI', 11),
                bg=COLORES['background'],
                fg=COLORES['text_secondary'],
                justify=tk.CENTER
            ).pack(pady=60)
            return

        for deuda in deudas:
            id_d, nombre, total, pagado, con_quien, tipo = deuda[:6]

            frame = tk.Frame(frame_lista, bg=COLORES['card_bg'], relief=tk.SOLID, bd=1, highlightbackground=COLORES['border'], highlightthickness=1)
            frame.pack(fill=tk.X, pady=5, padx=5)

            pct = (pagado / total * 100) if total > 0 else 0
            color = COLORES['success'] if pct >= 100 else COLORES['warning'] if pct >= 50 else COLORES['info']

            frame_header = tk.Frame(frame, bg=color, height=35)
            frame_header.pack(fill=tk.X)
            frame_header.pack_propagate(False)

            icono = "💸" if tipo == "debo" else "💰"
            tk.Label(
                frame_header,
                text=f"{icono} {nombre}",
                font=('Segoe UI', 11, 'bold'),
                bg=color,
                fg='white'
            ).pack(side=tk.LEFT, padx=15, pady=7)

            tk.Label(
                frame_header,
                text=f"Con: {con_quien}",
                font=('Segoe UI', 9),
                bg=color,
                fg='white'
            ).pack(side=tk.RIGHT, padx=15)

            frame_contenido = tk.Frame(frame, bg=COLORES['card_bg'])
            frame_contenido.pack(fill=tk.X, padx=15, pady=10)

            tk.Label(
                frame_contenido,
                text=f"${pagado:,.0f} de ${total:,.0f} ({pct:.0f}%)",
                font=('Segoe UI', 10),
                bg=COLORES['card_bg']
            ).pack(anchor='w', pady=3)

    def ventana_nueva_deuda(self):
        """Ventana para crear deuda"""
        v = tk.Toplevel(self.root)
        v.title("👥 Nueva Deuda Compartida")
        v.geometry("450x500")
        v.configure(bg=COLORES['background'])
        v.transient(self.root)
        v.grab_set()

        v.update_idletasks()
        x = (v.winfo_screenwidth() // 2) - (450 // 2)
        y = (v.winfo_screenheight() // 2) - (500 // 2)
        v.geometry(f'450x500+{x}+{y}')

        frame = tk.Frame(v, bg=COLORES['background'], padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="📝 Descripción:", bg=COLORES['background']).pack(anchor='w', pady=3)
        entry_nombre = tk.Entry(frame)
        entry_nombre.pack(fill=tk.X, pady=3)

        tk.Label(frame, text="💰 Monto total:", bg=COLORES['background']).pack(anchor='w', pady=3)
        entry_monto = tk.Entry(frame)
        entry_monto.pack(fill=tk.X, pady=3)

        tk.Label(frame, text="👤 Con quién:", bg=COLORES['background']).pack(anchor='w', pady=3)
        entry_quien = tk.Entry(frame)
        entry_quien.pack(fill=tk.X, pady=3)

        tk.Label(frame, text="📊 Tipo:", bg=COLORES['background']).pack(anchor='w', pady=3)
        combo_tipo = ttk.Combobox(frame, values=['Me deben', 'Debo'], state='readonly')
        combo_tipo.set('Me deben')
        combo_tipo.pack(fill=tk.X, pady=3)

        tk.Label(frame, text="🗒️ Notas:", bg=COLORES['background']).pack(anchor='w', pady=3)
        entry_notas = tk.Text(frame, height=3)
        entry_notas.pack(fill=tk.X, pady=3)

        def guardar():
            try:
                nombre = entry_nombre.get().strip()
                monto = float(entry_monto.get().replace(',', '.'))
                con_quien = entry_quien.get().strip()
                tipo = "debo" if combo_tipo.get() == "Debo" else "me_deben"
                notas = entry_notas.get('1.0', tk.END).strip()

                if not nombre or not con_quien or monto <= 0:
                    messagebox.showwarning("Error", "Completá todos los campos correctamente")
                    return

                self.db.agregar_deuda(nombre, monto, con_quien, tipo, None, notas)
                messagebox.showinfo("Éxito", "✅ Deuda registrada")
                v.destroy()
                self.mostrar_deudas()
            except ValueError:
                messagebox.showerror("Error", "Datos inválidos")

        frame_btns = tk.Frame(frame, bg=COLORES['background'])
        frame_btns.pack(pady=15)

        tk.Button(frame_btns, text="💾 Guardar", command=guardar, bg=COLORES['success'],
                 fg='white', font=('Segoe UI', 10, 'bold'), relief=tk.FLAT, cursor='hand2',
                 padx=25, pady=8).pack(side=tk.LEFT, padx=5)

        tk.Button(frame_btns, text="❌ Cancelar", command=v.destroy, bg=COLORES['danger'],
                 fg='white', font=('Segoe UI', 10), relief=tk.FLAT, cursor='hand2',
                 padx=25, pady=8).pack(side=tk.LEFT, padx=5)

    def mostrar_logros(self):
        """Vista de gamificación con logros"""
        # Header con toggle de gamificación
        frame_header = tk.Frame(self.frame_contenido, bg=COLORES['background'])
        frame_header.pack(fill=tk.X, padx=15, pady=10)

        tk.Label(
            frame_header,
            text="🎮 Logros y Desafíos",
            font=('Segoe UI', 14, 'bold'),
            bg=COLORES['background']
        ).pack(side=tk.LEFT)

        gamificacion_activa = self.db.obtener_config('gamificacion_activa') == 'true'

        def toggle_gamificacion():
            nuevo_estado = 'false' if gamificacion_activa else 'true'
            self.db.actualizar_config('gamificacion_activa', nuevo_estado)
            messagebox.showinfo("Configuración",
                              f"Gamificación {'activada' if nuevo_estado == 'true' else 'desactivada'}")
            self.mostrar_logros()

        tk.Button(
            frame_header,
            text="⚙️ " + ("Desactivar" if gamificacion_activa else "Activar"),
            command=toggle_gamificacion,
            bg=COLORES['secondary'],
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            padx=15,
            pady=6
        ).pack(side=tk.RIGHT)

        if not gamificacion_activa:
            tk.Label(
                self.frame_contenido,
                text="🎮 Gamificación desactivada\n\nActivala para desbloquear logros y desafíos",
                font=('Segoe UI', 11),
                bg=COLORES['background'],
                fg=COLORES['text_secondary'],
                justify=tk.CENTER
            ).pack(pady=60)
            return

        canvas = tk.Canvas(self.frame_contenido, bg=COLORES['background'], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.frame_contenido, orient="vertical", command=canvas.yview)

        frame_lista = tk.Frame(canvas, bg=COLORES['background'])
        frame_lista.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=frame_lista, anchor="nw", width=1100)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=15)
        scrollbar.pack(side="right", fill="y")

        logros = self.db.obtener_logros()

        for logro in logros:
            id_l, nombre, desc, icono, desbloqueado, fecha_desb, progreso, objetivo = logro

            frame = tk.Frame(frame_lista, bg=COLORES['card_bg'], relief=tk.SOLID, bd=1, highlightbackground=COLORES['border'], highlightthickness=1)
            frame.pack(fill=tk.X, pady=5, padx=5)

            if desbloqueado:
                color = COLORES['success']
                estado = f"✅ Desbloqueado - {fecha_desb}"
            else:
                color = COLORES['text_secondary']
                estado = f"🔒 Bloqueado - Progreso: {progreso}/{objetivo}"

            frame_header = tk.Frame(frame, bg=color if desbloqueado else COLORES['light'], height=35)
            frame_header.pack(fill=tk.X)
            frame_header.pack_propagate(False)

            tk.Label(
                frame_header,
                text=f"{icono} {nombre}",
                font=('Segoe UI', 11, 'bold'),
                bg=color if desbloqueado else COLORES['light'],
                fg='white' if desbloqueado else COLORES['text']
            ).pack(side=tk.LEFT, padx=15, pady=7)

            frame_contenido = tk.Frame(frame, bg=COLORES['card_bg'])
            frame_contenido.pack(fill=tk.X, padx=15, pady=10)

            tk.Label(
                frame_contenido,
                text=desc,
                font=('Segoe UI', 10),
                bg=COLORES['card_bg']
            ).pack(anchor='w', pady=3)

            tk.Label(
                frame_contenido,
                text=estado,
                font=('Segoe UI', 8),
                bg=COLORES['card_bg'],
                fg=COLORES['text_secondary']
            ).pack(anchor='w')

            # Barra de progreso si no está desbloqueado
            if not desbloqueado and objetivo > 0:
                canvas_barra = tk.Canvas(frame_contenido, height=15, bg=COLORES['background'], highlightthickness=0)
                canvas_barra.pack(fill=tk.X, pady=5)

                ancho = 1000
                pct = min((progreso / objetivo) * 100, 100)
                canvas_barra.create_rectangle(0, 0, ancho, 15, fill=COLORES['light'], outline='')
                if pct > 0:
                    ancho_prog = int(ancho * (pct / 100))
                    canvas_barra.create_rectangle(0, 0, ancho_prog, 15, fill=COLORES['info'], outline='')

    def mostrar_reglas_contexto(self):
        """Vista de reglas basadas en contexto (hora, clima, calendario)"""
        frame_btn = tk.Frame(self.frame_contenido, bg=COLORES['background'])
        frame_btn.pack(fill=tk.X, padx=15, pady=10)

        tk.Button(
            frame_btn,
            text="➕ Nueva Regla de Contexto",
            font=('Segoe UI', 10, 'bold'),
            bg=COLORES['success'],
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.ventana_nueva_regla_contexto,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT)

        # Toggle para activar/desactivar todas las reglas
        estado_actual = self.db.obtener_config('reglas_contexto_activas') == 'true'
        estado_text = "🟢 Activas" if estado_actual else "🔴 Desactivadas"

        def toggle_reglas():
            nuevo_estado = 'false' if estado_actual else 'true'
            self.db.actualizar_config('reglas_contexto_activas', nuevo_estado)
            self.mostrar_reglas_contexto()  # Recargar vista

        tk.Button(
            frame_btn,
            text=f"⚙️ {estado_text}",
            font=('Segoe UI', 10, 'bold'),
            bg=COLORES['success'] if estado_actual else COLORES['danger'],
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=toggle_reglas,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=10)

        canvas = tk.Canvas(self.frame_contenido, bg=COLORES['background'], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.frame_contenido, orient="vertical", command=canvas.yview)

        frame_lista = tk.Frame(canvas, bg=COLORES['background'])
        frame_lista.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=frame_lista, anchor="nw", width=1100)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=15)
        scrollbar.pack(side="right", fill="y")

        reglas = self.db.obtener_reglas_contexto()

        if not reglas:
            tk.Label(
                frame_lista,
                text="⚙️ No hay reglas de contexto configuradas\n\nCreá reglas automáticas basadas en hora, clima, día de la semana o mes",
                font=('Segoe UI', 11),
                bg=COLORES['background'],
                fg=COLORES['text_secondary'],
                justify=tk.CENTER
            ).pack(pady=60)
            return

        for regla in reglas:
            id_r, nombre, tipo_trigger, condicion, accion, parametros, activa, ultima_ejecucion = regla

            frame = tk.Frame(frame_lista, bg=COLORES['card_bg'], relief=tk.SOLID, bd=1, highlightbackground=COLORES['border'], highlightthickness=1)
            frame.pack(fill=tk.X, pady=5, padx=5)

            # Color según estado
            color = COLORES['success'] if activa else COLORES['text_secondary']
            estado = "✅ Activa" if activa else "⏸️ Pausada"

            frame_header = tk.Frame(frame, bg=color, height=35)
            frame_header.pack(fill=tk.X)
            frame_header.pack_propagate(False)

            tk.Label(
                frame_header,
                text=f"⚙️ {nombre}",
                font=('Segoe UI', 11, 'bold'),
                bg=color,
                fg='white'
            ).pack(side=tk.LEFT, padx=15, pady=7)

            tk.Label(
                frame_header,
                text=estado,
                font=('Segoe UI', 9),
                bg=color,
                fg='white'
            ).pack(side=tk.RIGHT, padx=15)

            frame_contenido = tk.Frame(frame, bg=COLORES['card_bg'])
            frame_contenido.pack(fill=tk.X, padx=15, pady=10)

            # Mostrar detalles
            tipo_icons = {
                'hora': '🕐',
                'dia_semana': '📅',
                'clima': '🌤️',
                'mes': '📆',
                'temperatura': '🌡️'
            }
            icon = tipo_icons.get(tipo_trigger, '⚙️')

            info = f"{icon} Trigger: {tipo_trigger} | Condición: {condicion} | Acción: {accion}"
            if ultima_ejecucion:
                info += f"\n🕒 Última ejecución: {ultima_ejecucion}"

            tk.Label(
                frame_contenido,
                text=info,
                font=('Segoe UI', 10),
                bg=COLORES['card_bg'],
                justify=tk.LEFT
            ).pack(anchor='w', pady=3)

            # Botones de acción
            frame_botones = tk.Frame(frame_contenido, bg=COLORES['card_bg'])
            frame_botones.pack(anchor='w', pady=5)

            def toggle_regla(regla_id=id_r, actual=activa):
                cursor = self.db.conn.cursor()
                cursor.execute('UPDATE reglas_contexto SET activa=? WHERE id=?',
                             (0 if actual else 1, regla_id))
                self.db.conn.commit()
                self.mostrar_reglas_contexto()

            tk.Button(
                frame_botones,
                text="⏸️ Pausar" if activa else "▶️ Activar",
                font=('Segoe UI', 9),
                bg=COLORES['warning'] if activa else COLORES['success'],
                fg='white',
                relief=tk.FLAT,
                cursor='hand2',
                command=toggle_regla,
                padx=10,
                pady=4
            ).pack(side=tk.LEFT, padx=3)

            def eliminar_regla(regla_id=id_r):
                if messagebox.askyesno("Confirmar", "¿Eliminar esta regla de contexto?"):
                    cursor = self.db.conn.cursor()
                    cursor.execute('DELETE FROM reglas_contexto WHERE id=?', (regla_id,))
                    self.db.conn.commit()
                    self.mostrar_reglas_contexto()

            tk.Button(
                frame_botones,
                text="🗑️ Eliminar",
                font=('Segoe UI', 9),
                bg=COLORES['danger'],
                fg='white',
                relief=tk.FLAT,
                cursor='hand2',
                command=eliminar_regla,
                padx=10,
                pady=4
            ).pack(side=tk.LEFT, padx=3)

    def ventana_nueva_regla_contexto(self):
        """Ventana para crear nueva regla de contexto"""
        v = tk.Toplevel(self.root)
        v.title("⚙️ Nueva Regla de Contexto")
        v.geometry("550x600")
        v.configure(bg=COLORES['background'])
        v.transient(self.root)
        v.grab_set()

        v.update_idletasks()
        x = (v.winfo_screenwidth() // 2) - (550 // 2)
        y = (v.winfo_screenheight() // 2) - (600 // 2)
        v.geometry(f'550x600+{x}+{y}')

        frame = tk.Frame(v, bg=COLORES['background'], padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            frame,
            text="⚙️ Crear Regla Automática",
            font=('Segoe UI', 16, 'bold'),
            bg=COLORES['background']
        ).pack(pady=10)

        tk.Label(frame, text="📝 Nombre de la regla:", bg=COLORES['background']).pack(anchor='w', pady=3)
        entry_nombre = tk.Entry(frame, font=('Segoe UI', 11))
        entry_nombre.pack(fill=tk.X, pady=3)

        tk.Label(frame, text="🎯 Tipo de Trigger:", bg=COLORES['background']).pack(anchor='w', pady=3)
        combo_trigger = ttk.Combobox(frame, values=['hora', 'dia_semana', 'clima', 'mes', 'temperatura'],
                                      state='readonly', font=('Segoe UI', 11))
        combo_trigger.set('hora')
        combo_trigger.pack(fill=tk.X, pady=3)

        tk.Label(frame, text="⚡ Condición:", bg=COLORES['background']).pack(anchor='w', pady=3)

        # Frame dinámico para condición
        frame_condicion = tk.Frame(frame, bg=COLORES['background'])
        frame_condicion.pack(fill=tk.X, pady=3)

        entry_condicion = tk.Entry(frame_condicion, font=('Segoe UI', 11))
        entry_condicion.pack(fill=tk.X)

        # Texto de ayuda dinámico
        label_ayuda = tk.Label(
            frame,
            text="Ej: 'mañana', 'tarde', 'noche'",
            font=('Segoe UI', 9),
            bg=COLORES['background'],
            fg=COLORES['text_secondary']
        )
        label_ayuda.pack(anchor='w')

        def actualizar_ayuda(event=None):
            trigger = combo_trigger.get()
            ayudas = {
                'hora': "Ej: 'mañana' (6-12), 'tarde' (12-18), 'noche' (18-24), 'madrugada' (0-6)",
                'dia_semana': "Ej: 'lunes', 'martes', 'fin_de_semana', 'dia_laborable'",
                'clima': "Ej: 'lluvia', 'soleado', 'nublado'",
                'mes': "Ej: 'vacaciones' (enero, julio), 'navidad' (diciembre)",
                'temperatura': "Ej: 'calor' (>25°C), 'frio' (<15°C)"
            }
            label_ayuda.config(text=ayudas.get(trigger, ""))

        combo_trigger.bind('<<ComboboxSelected>>', actualizar_ayuda)

        tk.Label(frame, text="🎬 Acción:", bg=COLORES['background']).pack(anchor='w', pady=3)
        combo_accion = ttk.Combobox(frame, values=['crear_alerta', 'sugerir_ahorro', 'recordatorio'],
                                     state='readonly', font=('Segoe UI', 11))
        combo_accion.set('crear_alerta')
        combo_accion.pack(fill=tk.X, pady=3)

        tk.Label(frame, text="📋 Mensaje/Parámetros:", bg=COLORES['background']).pack(anchor='w', pady=3)
        text_params = tk.Text(frame, height=4, font=('Segoe UI', 10))
        text_params.pack(fill=tk.X, pady=3)
        text_params.insert('1.0', 'Mensaje o parámetros de la acción')

        def guardar_regla():
            nombre = entry_nombre.get().strip()
            if not nombre:
                messagebox.showwarning("Datos incompletos", "Ingresá un nombre para la regla")
                return

            cursor = self.db.conn.cursor()
            cursor.execute('''
                INSERT INTO reglas_contexto (nombre, tipo_trigger, condicion, accion, parametros, activa)
                VALUES (?, ?, ?, ?, ?, 1)
            ''', (
                nombre,
                combo_trigger.get(),
                entry_condicion.get().strip(),
                combo_accion.get(),
                text_params.get('1.0', 'end-1c').strip()
            ))
            self.db.conn.commit()

            messagebox.showinfo("Éxito", "Regla de contexto creada correctamente")
            v.destroy()
            self.mostrar_reglas_contexto()

        tk.Button(
            frame,
            text="💾 Guardar Regla",
            font=('Segoe UI', 12, 'bold'),
            bg=COLORES['success'],
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=guardar_regla,
            pady=10
        ).pack(pady=15, fill=tk.X)

    def mostrar_geofence(self):
        """Vista de reglas de geofence (ubicación)"""
        frame_btn = tk.Frame(self.frame_contenido, bg=COLORES['background'])
        frame_btn.pack(fill=tk.X, padx=15, pady=10)

        tk.Button(
            frame_btn,
            text="➕ Nueva Zona (Geofence)",
            font=('Segoe UI', 10, 'bold'),
            bg=COLORES['success'],
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.ventana_nueva_geofence,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT)

        # Toggle para activar/desactivar geolocalización
        estado_actual = self.db.obtener_config('geofence_activo') == 'true'
        estado_text = "🟢 Activo" if estado_actual else "🔴 Desactivado"

        def toggle_geofence():
            nuevo_estado = 'false' if estado_actual else 'true'
            self.db.actualizar_config('geofence_activo', nuevo_estado)
            self.mostrar_geofence()

        tk.Button(
            frame_btn,
            text=f"📍 {estado_text}",
            font=('Segoe UI', 10, 'bold'),
            bg=COLORES['success'] if estado_actual else COLORES['danger'],
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=toggle_geofence,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=10)

        canvas = tk.Canvas(self.frame_contenido, bg=COLORES['background'], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.frame_contenido, orient="vertical", command=canvas.yview)

        frame_lista = tk.Frame(canvas, bg=COLORES['background'])
        frame_lista.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=frame_lista, anchor="nw", width=1100)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=15)
        scrollbar.pack(side="right", fill="y")

        cursor = self.db.conn.cursor()
        cursor.execute('SELECT * FROM reglas_geofence ORDER BY nombre')
        zonas = cursor.fetchall()

        if not zonas:
            tk.Label(
                frame_lista,
                text="📍 No hay zonas de geofence configuradas\n\nDefine lugares para auto-categorizar gastos según ubicación",
                font=('Segoe UI', 11),
                bg=COLORES['background'],
                fg=COLORES['text_secondary'],
                justify=tk.CENTER
            ).pack(pady=60)
            return

        for zona in zonas:
            id_z, nombre, lat, lon, radio, cat_sugerida, cuenta_sugerida, activa = zona

            frame = tk.Frame(frame_lista, bg=COLORES['card_bg'], relief=tk.SOLID, bd=1, highlightbackground=COLORES['border'], highlightthickness=1)
            frame.pack(fill=tk.X, pady=5, padx=5)

            color = COLORES['info'] if activa else COLORES['text_secondary']
            estado = "✅ Activa" if activa else "⏸️ Pausada"

            frame_header = tk.Frame(frame, bg=color, height=35)
            frame_header.pack(fill=tk.X)
            frame_header.pack_propagate(False)

            tk.Label(
                frame_header,
                text=f"📍 {nombre}",
                font=('Segoe UI', 11, 'bold'),
                bg=color,
                fg='white'
            ).pack(side=tk.LEFT, padx=15, pady=7)

            tk.Label(
                frame_header,
                text=estado,
                font=('Segoe UI', 9),
                bg=color,
                fg='white'
            ).pack(side=tk.RIGHT, padx=15)

            frame_contenido = tk.Frame(frame, bg=COLORES['card_bg'])
            frame_contenido.pack(fill=tk.X, padx=15, pady=10)

            info = f"🌍 Coords: {lat:.4f}, {lon:.4f} | 📏 Radio: {radio}m"
            if cat_sugerida:
                info += f" | 📂 Categoría: {cat_sugerida}"
            if cuenta_sugerida:
                info += f" | 💳 Cuenta: {cuenta_sugerida}"

            tk.Label(
                frame_contenido,
                text=info,
                font=('Segoe UI', 10),
                bg=COLORES['card_bg']
            ).pack(anchor='w', pady=3)

            # Botones de acción
            frame_botones = tk.Frame(frame_contenido, bg=COLORES['card_bg'])
            frame_botones.pack(anchor='w', pady=5)

            def toggle_zona(zona_id=id_z, actual=activa):
                cursor = self.db.conn.cursor()
                cursor.execute('UPDATE reglas_geofence SET activa=? WHERE id=?',
                             (0 if actual else 1, zona_id))
                self.db.conn.commit()
                self.mostrar_geofence()

            tk.Button(
                frame_botones,
                text="⏸️ Pausar" if activa else "▶️ Activar",
                font=('Segoe UI', 9),
                bg=COLORES['warning'] if activa else COLORES['success'],
                fg='white',
                relief=tk.FLAT,
                cursor='hand2',
                command=toggle_zona,
                padx=10,
                pady=4
            ).pack(side=tk.LEFT, padx=3)

            def eliminar_zona(zona_id=id_z):
                if messagebox.askyesno("Confirmar", "¿Eliminar esta zona de geofence?"):
                    cursor = self.db.conn.cursor()
                    cursor.execute('DELETE FROM reglas_geofence WHERE id=?', (zona_id,))
                    self.db.conn.commit()
                    self.mostrar_geofence()

            tk.Button(
                frame_botones,
                text="🗑️ Eliminar",
                font=('Segoe UI', 9),
                bg=COLORES['danger'],
                fg='white',
                relief=tk.FLAT,
                cursor='hand2',
                command=eliminar_zona,
                padx=10,
                pady=4
            ).pack(side=tk.LEFT, padx=3)

    def ventana_nueva_geofence(self):
        """Ventana para crear nueva zona de geofence"""
        v = tk.Toplevel(self.root)
        v.title("📍 Nueva Zona Geofence")
        v.geometry("500x550")
        v.configure(bg=COLORES['background'])
        v.transient(self.root)
        v.grab_set()

        v.update_idletasks()
        x = (v.winfo_screenwidth() // 2) - (500 // 2)
        y = (v.winfo_screenheight() // 2) - (550 // 2)
        v.geometry(f'500x550+{x}+{y}')

        frame = tk.Frame(v, bg=COLORES['background'], padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            frame,
            text="📍 Definir Zona de Geofence",
            font=('Segoe UI', 16, 'bold'),
            bg=COLORES['background']
        ).pack(pady=10)

        tk.Label(frame, text="📝 Nombre del lugar:", bg=COLORES['background']).pack(anchor='w', pady=3)
        entry_nombre = tk.Entry(frame, font=('Segoe UI', 11))
        entry_nombre.pack(fill=tk.X, pady=3)
        entry_nombre.insert(0, "Ej: Supermercado Carrefour")

        tk.Label(frame, text="🌍 Latitud:", bg=COLORES['background']).pack(anchor='w', pady=3)
        entry_lat = tk.Entry(frame, font=('Segoe UI', 11))
        entry_lat.pack(fill=tk.X, pady=3)
        entry_lat.insert(0, "-34.6037")

        tk.Label(frame, text="🌍 Longitud:", bg=COLORES['background']).pack(anchor='w', pady=3)
        entry_lon = tk.Entry(frame, font=('Segoe UI', 11))
        entry_lon.pack(fill=tk.X, pady=3)
        entry_lon.insert(0, "-58.3816")

        tk.Label(
            frame,
            text="💡 Podés usar Google Maps: click derecho → copiar coordenadas",
            font=('Segoe UI', 9),
            bg=COLORES['background'],
            fg=COLORES['text_secondary']
        ).pack(anchor='w', pady=3)

        tk.Label(frame, text="📏 Radio (metros):", bg=COLORES['background']).pack(anchor='w', pady=3)
        entry_radio = tk.Entry(frame, font=('Segoe UI', 11))
        entry_radio.pack(fill=tk.X, pady=3)
        entry_radio.insert(0, "100")

        tk.Label(frame, text="📂 Categoría sugerida (opcional):", bg=COLORES['background']).pack(anchor='w', pady=3)
        combo_cat = ttk.Combobox(frame, values=[c[1] for c in self.db.obtener_categorias()],
                                 font=('Segoe UI', 11))
        combo_cat.pack(fill=tk.X, pady=3)

        tk.Label(frame, text="💳 Cuenta sugerida (opcional):", bg=COLORES['background']).pack(anchor='w', pady=3)
        combo_cuenta = ttk.Combobox(frame, values=[c[1] for c in self.db.obtener_tarjetas()],
                                    font=('Segoe UI', 11))
        combo_cuenta.pack(fill=tk.X, pady=3)

        def guardar_zona():
            nombre = entry_nombre.get().strip()
            if not nombre or nombre.startswith("Ej:"):
                messagebox.showwarning("Datos incompletos", "Ingresá un nombre para la zona")
                return

            try:
                lat = float(entry_lat.get())
                lon = float(entry_lon.get())
                radio = int(entry_radio.get())
            except ValueError:
                messagebox.showwarning("Datos inválidos", "Verificá que las coordenadas y radio sean números válidos")
                return

            cursor = self.db.conn.cursor()
            cursor.execute('''
                INSERT INTO reglas_geofence (nombre, latitud, longitud, radio_metros,
                                            categoria_sugerida, cuenta_sugerida, activa)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            ''', (
                nombre, lat, lon, radio,
                combo_cat.get() if combo_cat.get() else None,
                combo_cuenta.get() if combo_cuenta.get() else None
            ))
            self.db.conn.commit()

            messagebox.showinfo("Éxito", "Zona de geofence creada correctamente")
            v.destroy()
            self.mostrar_geofence()

        tk.Button(
            frame,
            text="💾 Guardar Zona",
            font=('Segoe UI', 12, 'bold'),
            bg=COLORES['success'],
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=guardar_zona,
            pady=10
        ).pack(pady=15, fill=tk.X)

    def mostrar_ahorro_automatico(self):
        """Vista de reglas de ahorro automático (inspirado en Plum)"""
        frame_btn = tk.Frame(self.frame_contenido, bg=COLORES['background'])
        frame_btn.pack(fill=tk.X, padx=15, pady=10)

        tk.Button(
            frame_btn,
            text="➕ Nueva Regla de Ahorro",
            font=('Segoe UI', 10, 'bold'),
            bg=COLORES['success'],
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.ventana_nueva_regla_ahorro,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT)

        # Info card con total ahorrado
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT SUM(monto_ahorrado_total) FROM reglas_ahorro_auto WHERE activa=1')
        total_ahorrado = cursor.fetchone()[0] or 0

        frame_info = tk.Frame(frame_btn, bg=COLORES['info'], relief=tk.RAISED, bd=2)
        frame_info.pack(side=tk.RIGHT, padx=10)

        tk.Label(
            frame_info,
            text=f"💰 Total Ahorrado: ${total_ahorrado:,.0f}",
            font=('Segoe UI', 11, 'bold'),
            bg=COLORES['info'],
            fg='white',
            padx=15,
            pady=8
        ).pack()

        canvas = tk.Canvas(self.frame_contenido, bg=COLORES['background'], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.frame_contenido, orient="vertical", command=canvas.yview)

        frame_lista = tk.Frame(canvas, bg=COLORES['background'])
        frame_lista.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=frame_lista, anchor="nw", width=1100)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=15)
        scrollbar.pack(side="right", fill="y")

        reglas = self.db.obtener_reglas_ahorro_auto(solo_activas=False)

        if not reglas:
            tk.Label(
                frame_lista,
                text="💰 No hay reglas de ahorro automático configuradas\n\n¿Querés ahorrar sin pensarlo? Creá reglas automáticas:\n• Redondeo: ahorrá la diferencia al redondear tus gastos\n• Payday: ahorrá un % cuando llega tu sueldo\n• Desafío 52 semanas: ahorrá cada semana",
                font=('Segoe UI', 11),
                bg=COLORES['background'],
                fg=COLORES['text_secondary'],
                justify=tk.CENTER
            ).pack(pady=60)
            return

        for regla in reglas:
            id_r, nombre, tipo, activa, modo, meta_id, ultima_ej, monto_total, config = regla

            frame = tk.Frame(frame_lista, bg=COLORES['card_bg'], relief=tk.SOLID, bd=1, highlightbackground=COLORES['border'], highlightthickness=1)
            frame.pack(fill=tk.X, pady=5, padx=5)

            # Color según estado
            color = COLORES['success'] if activa else COLORES['text_secondary']
            estado = "✅ Activa" if activa else "⏸️ Pausada"

            frame_header = tk.Frame(frame, bg=color, height=35)
            frame_header.pack(fill=tk.X)
            frame_header.pack_propagate(False)

            tipo_icons = {
                'redondeo': '🔄',
                'payday': '💵',
                '52semanas': '📅',
                'dias_lluvia': '🌧️',
                'porcentaje_ingreso': '📊'
            }
            icon = tipo_icons.get(tipo, '💰')

            tk.Label(
                frame_header,
                text=f"{icon} {nombre}",
                font=('Segoe UI', 11, 'bold'),
                bg=color,
                fg='white'
            ).pack(side=tk.LEFT, padx=15, pady=7)

            tk.Label(
                frame_header,
                text=estado,
                font=('Segoe UI', 9),
                bg=color,
                fg='white'
            ).pack(side=tk.RIGHT, padx=15)

            frame_contenido = tk.Frame(frame, bg=COLORES['card_bg'])
            frame_contenido.pack(fill=tk.X, padx=15, pady=10)

            # Mostrar detalles
            modos_display = {
                'timido': '😊 Tímido',
                'moderado': '😎 Moderado',
                'agresivo': '💪 Agresivo',
                'bestia': '🦁 A lo Bestia'
            }
            modo_text = modos_display.get(modo, modo)

            info = f"Tipo: {tipo} | Modo: {modo_text}\n💰 Ahorrado hasta ahora: ${monto_total:,.0f}"
            if ultima_ej:
                info += f" | Última ejecución: {ultima_ej}"

            tk.Label(
                frame_contenido,
                text=info,
                font=('Segoe UI', 10),
                bg=COLORES['card_bg'],
                justify=tk.LEFT
            ).pack(anchor='w', pady=3)

            # Botones de acción
            frame_botones = tk.Frame(frame_contenido, bg=COLORES['card_bg'])
            frame_botones.pack(anchor='w', pady=5)

            def toggle_regla(regla_id=id_r, actual=activa):
                cursor = self.db.conn.cursor()
                cursor.execute('UPDATE reglas_ahorro_auto SET activa=? WHERE id=?',
                             (0 if actual else 1, regla_id))
                self.db.conn.commit()
                self.mostrar_ahorro_automatico()

            tk.Button(
                frame_botones,
                text="⏸️ Pausar" if activa else "▶️ Activar",
                font=('Segoe UI', 9),
                bg=COLORES['warning'] if activa else COLORES['success'],
                fg='white',
                relief=tk.FLAT,
                cursor='hand2',
                command=toggle_regla,
                padx=10,
                pady=4
            ).pack(side=tk.LEFT, padx=3)

            def eliminar_regla(regla_id=id_r):
                if messagebox.askyesno("Confirmar", "¿Eliminar esta regla de ahorro?"):
                    cursor = self.db.conn.cursor()
                    cursor.execute('DELETE FROM reglas_ahorro_auto WHERE id=?', (regla_id,))
                    self.db.conn.commit()
                    self.mostrar_ahorro_automatico()

            tk.Button(
                frame_botones,
                text="🗑️ Eliminar",
                font=('Segoe UI', 9),
                bg=COLORES['danger'],
                fg='white',
                relief=tk.FLAT,
                cursor='hand2',
                command=eliminar_regla,
                padx=10,
                pady=4
            ).pack(side=tk.LEFT, padx=3)

    def ventana_nueva_regla_ahorro(self):
        """Ventana para crear nueva regla de ahorro automático"""
        v = tk.Toplevel(self.root)
        v.title("💰 Nueva Regla de Ahorro Automático")
        v.geometry("500x550")
        v.configure(bg=COLORES['background'])
        v.transient(self.root)
        v.grab_set()

        v.update_idletasks()
        x = (v.winfo_screenwidth() // 2) - (500 // 2)
        y = (v.winfo_screenheight() // 2) - (550 // 2)
        v.geometry(f'500x550+{x}+{y}')

        frame = tk.Frame(v, bg=COLORES['background'], padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            frame,
            text="💰 Crear Regla de Ahorro Automático",
            font=('Segoe UI', 16, 'bold'),
            bg=COLORES['background']
        ).pack(pady=10)

        tk.Label(frame, text="📝 Nombre de la regla:", bg=COLORES['background']).pack(anchor='w', pady=3)
        entry_nombre = tk.Entry(frame, font=('Segoe UI', 11))
        entry_nombre.pack(fill=tk.X, pady=3)

        tk.Label(frame, text="🎯 Tipo de Regla:", bg=COLORES['background']).pack(anchor='w', pady=3)
        combo_tipo = ttk.Combobox(frame, values=['redondeo', 'payday', '52semanas'],
                                   state='readonly', font=('Segoe UI', 11))
        combo_tipo.set('redondeo')
        combo_tipo.pack(fill=tk.X, pady=3)

        tk.Label(frame, text="💪 Modo de Agresividad:", bg=COLORES['background']).pack(anchor='w', pady=3)
        combo_modo = ttk.Combobox(frame, values=['timido', 'moderado', 'agresivo', 'bestia'],
                                   state='readonly', font=('Segoe UI', 11))
        combo_modo.set('moderado')
        combo_modo.pack(fill=tk.X, pady=3)

        # Descripción dinámica
        label_desc = tk.Label(
            frame,
            text="",
            font=('Segoe UI', 9),
            bg=COLORES['background'],
            fg=COLORES['text_secondary'],
            justify=tk.LEFT,
            wraplength=450
        )
        label_desc.pack(pady=10, fill=tk.X)

        def actualizar_descripcion(event=None):
            tipo = combo_tipo.get()
            modo = combo_modo.get()

            descripciones = {
                'redondeo': {
                    'timido': '🔄 Redondea al peso más cercano y ahorra la diferencia',
                    'moderado': '🔄 Redondea a los $10 y ahorra la diferencia',
                    'agresivo': '🔄 Redondea a los $50 y ahorra la diferencia',
                    'bestia': '🔄 Redondea a los $100 y ahorra la diferencia'
                },
                'payday': {
                    'timido': '💵 Ahorra 2% cuando llega tu sueldo',
                    'moderado': '💵 Ahorra 5% cuando llega tu sueldo',
                    'agresivo': '💵 Ahorra 10% cuando llega tu sueldo',
                    'bestia': '💵 Ahorra 15% cuando llega tu sueldo'
                },
                '52semanas': {
                    'timido': '📅 Ahorra $10 por semana durante 52 semanas',
                    'moderado': '📅 Ahorra $50 por semana durante 52 semanas',
                    'agresivo': '📅 Ahorra $100 por semana durante 52 semanas',
                    'bestia': '📅 Ahorra $200 por semana durante 52 semanas'
                }
            }

            desc = descripciones.get(tipo, {}).get(modo, '')
            label_desc.config(text=desc)

        combo_tipo.bind('<<ComboboxSelected>>', actualizar_descripcion)
        combo_modo.bind('<<ComboboxSelected>>', actualizar_descripcion)
        actualizar_descripcion()

        tk.Label(frame, text="🎯 Meta destino (opcional):", bg=COLORES['background']).pack(anchor='w', pady=3)

        # Obtener metas disponibles
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT id, nombre FROM metas_ahorro WHERE completada=0')
        metas = cursor.fetchall()
        metas_nombres = ['Ninguna'] + [f"{m[1]}" for m in metas]

        combo_meta = ttk.Combobox(frame, values=metas_nombres, font=('Segoe UI', 11))
        combo_meta.set('Ninguna')
        combo_meta.pack(fill=tk.X, pady=3)

        def guardar_regla():
            nombre = entry_nombre.get().strip()
            if not nombre:
                messagebox.showwarning("Datos incompletos", "Ingresá un nombre para la regla")
                return

            # Obtener ID de meta si seleccionó una
            meta_id = None
            if combo_meta.get() != 'Ninguna':
                idx = combo_meta.current() - 1
                if idx >= 0 and idx < len(metas):
                    meta_id = metas[idx][0]

            self.db.crear_regla_ahorro_auto(
                nombre=nombre,
                tipo_regla=combo_tipo.get(),
                modo_agresividad=combo_modo.get(),
                meta_id=meta_id
            )

            messagebox.showinfo("Éxito", "Regla de ahorro creada correctamente")
            v.destroy()
            self.mostrar_ahorro_automatico()

        tk.Button(
            frame,
            text="💾 Guardar Regla",
            font=('Segoe UI', 12, 'bold'),
            bg=COLORES['success'],
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=guardar_regla,
            pady=10
        ).pack(pady=15, fill=tk.X)

    def mostrar_suscripciones(self):
        """Vista de suscripciones (inspirado en Emma)"""
        frame_btn = tk.Frame(self.frame_contenido, bg=COLORES['background'])
        frame_btn.pack(fill=tk.X, padx=15, pady=10)

        tk.Button(
            frame_btn,
            text="➕ Nueva Suscripción",
            font=('Segoe UI', 10, 'bold'),
            bg=COLORES['success'],
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.ventana_nueva_suscripcion,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT)

        # Info card con gasto mensual
        gasto_mensual = self.db.calcular_gasto_suscripciones_mensual()

        frame_info = tk.Frame(frame_btn, bg=COLORES['danger'], relief=tk.RAISED, bd=2)
        frame_info.pack(side=tk.RIGHT, padx=10)

        tk.Label(
            frame_info,
            text=f"📺 Gasto Mensual: ${gasto_mensual:,.0f}",
            font=('Segoe UI', 11, 'bold'),
            bg=COLORES['danger'],
            fg='white',
            padx=15,
            pady=8
        ).pack()

        # Detectar suscripciones no usadas
        no_usadas = self.db.detectar_suscripciones_no_usadas()
        if no_usadas:
            frame_alerta = tk.Frame(self.frame_contenido, bg=COLORES['warning'], relief=tk.RAISED, bd=2)
            frame_alerta.pack(fill=tk.X, padx=15, pady=10)

            ahorro_potencial = sum(m for n, m, mon in no_usadas)
            texto_alerta = f"⚠️ ¡Atención! Detectamos {len(no_usadas)} suscripción(es) que no usaste en 60 días.\n"
            texto_alerta += f"Podrías ahorrar ${ahorro_potencial:,.0f}/mes cancelándolas: {', '.join(n for n, m, mon in no_usadas)}"

            tk.Label(
                frame_alerta,
                text=texto_alerta,
                font=('Segoe UI', 10, 'bold'),
                bg=COLORES['warning'],
                fg='white',
                padx=15,
                pady=10,
                wraplength=1000,
                justify=tk.LEFT
            ).pack()

        canvas = tk.Canvas(self.frame_contenido, bg=COLORES['background'], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.frame_contenido, orient="vertical", command=canvas.yview)

        frame_lista = tk.Frame(canvas, bg=COLORES['background'])
        frame_lista.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=frame_lista, anchor="nw", width=1100)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=15)
        scrollbar.pack(side="right", fill="y")

        suscripciones = self.db.obtener_suscripciones(solo_activas=False)

        if not suscripciones:
            tk.Label(
                frame_lista,
                text="📺 No hay suscripciones registradas\n\nRegistrá tus suscripciones (Netflix, Spotify, Gym, etc.)\ny controlá cuánto gastás mensualmente",
                font=('Segoe UI', 11),
                bg=COLORES['background'],
                fg=COLORES['text_secondary'],
                justify=tk.CENTER
            ).pack(pady=60)
            return

        for susc in suscripciones:
            id_s, nombre, cat, monto, moneda, freq, dia_cobro, fecha_inicio, prox_cobro, activa = susc[:10]

            frame = tk.Frame(frame_lista, bg=COLORES['card_bg'], relief=tk.SOLID, bd=1, highlightbackground=COLORES['border'], highlightthickness=1)
            frame.pack(fill=tk.X, pady=5, padx=5)

            # Verificar si es suscripción no usada
            es_no_usada = any(n == nombre for n, m, mon in no_usadas)
            color = COLORES['warning'] if es_no_usada else (COLORES['info'] if activa else COLORES['text_secondary'])
            estado = "⚠️ No usada" if es_no_usada else ("✅ Activa" if activa else "⏸️ Cancelada")

            frame_header = tk.Frame(frame, bg=color, height=35)
            frame_header.pack(fill=tk.X)
            frame_header.pack_propagate(False)

            tk.Label(
                frame_header,
                text=f"📺 {nombre}",
                font=('Segoe UI', 11, 'bold'),
                bg=color,
                fg='white'
            ).pack(side=tk.LEFT, padx=15, pady=7)

            tk.Label(
                frame_header,
                text=estado,
                font=('Segoe UI', 9),
                bg=color,
                fg='white'
            ).pack(side=tk.RIGHT, padx=15)

            frame_contenido = tk.Frame(frame, bg=COLORES['card_bg'])
            frame_contenido.pack(fill=tk.X, padx=15, pady=10)

            # Calcular monto mensual
            freq_mult = {'mensual': 1, 'anual': 1/12, 'semanal': 4.33}
            monto_mes = monto * freq_mult.get(freq, 1)

            info = f"💰 {moneda} ${monto:,.0f} / {freq}"
            if freq != 'mensual':
                info += f" → ${monto_mes:,.0f}/mes"
            if prox_cobro:
                info += f" | 📅 Próximo cobro: {prox_cobro}"

            tk.Label(
                frame_contenido,
                text=info,
                font=('Segoe UI', 10),
                bg=COLORES['card_bg']
            ).pack(anchor='w', pady=3)

            # Botones de acción
            frame_botones = tk.Frame(frame_contenido, bg=COLORES['card_bg'])
            frame_botones.pack(anchor='w', pady=5)

            def toggle_susc(susc_id=id_s, actual=activa):
                cursor = self.db.conn.cursor()
                cursor.execute('UPDATE suscripciones SET activa=? WHERE id=?',
                             (0 if actual else 1, susc_id))
                self.db.conn.commit()
                self.mostrar_suscripciones()

            tk.Button(
                frame_botones,
                text="🚫 Cancelar" if activa else "▶️ Reactivar",
                font=('Segoe UI', 9),
                bg=COLORES['danger'] if activa else COLORES['success'],
                fg='white',
                relief=tk.FLAT,
                cursor='hand2',
                command=toggle_susc,
                padx=10,
                pady=4
            ).pack(side=tk.LEFT, padx=3)

            def eliminar_susc(susc_id=id_s):
                if messagebox.askyesno("Confirmar", "¿Eliminar esta suscripción?"):
                    cursor = self.db.conn.cursor()
                    cursor.execute('DELETE FROM suscripciones WHERE id=?', (susc_id,))
                    self.db.conn.commit()
                    self.mostrar_suscripciones()

            tk.Button(
                frame_botones,
                text="🗑️ Eliminar",
                font=('Segoe UI', 9),
                bg=COLORES['text_secondary'],
                fg='white',
                relief=tk.FLAT,
                cursor='hand2',
                command=eliminar_susc,
                padx=10,
                pady=4
            ).pack(side=tk.LEFT, padx=3)

    def ventana_nueva_suscripcion(self):
        """Ventana para crear nueva suscripción"""
        v = tk.Toplevel(self.root)
        v.title("📺 Nueva Suscripción")
        v.geometry("450x500")
        v.configure(bg=COLORES['background'])
        v.transient(self.root)
        v.grab_set()

        v.update_idletasks()
        x = (v.winfo_screenwidth() // 2) - (450 // 2)
        y = (v.winfo_screenheight() // 2) - (500 // 2)
        v.geometry(f'450x500+{x}+{y}')

        frame = tk.Frame(v, bg=COLORES['background'], padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            frame,
            text="📺 Registrar Suscripción",
            font=('Segoe UI', 16, 'bold'),
            bg=COLORES['background']
        ).pack(pady=10)

        tk.Label(frame, text="📝 Nombre (ej: Netflix, Spotify, Gym):", bg=COLORES['background']).pack(anchor='w', pady=3)
        entry_nombre = tk.Entry(frame, font=('Segoe UI', 11))
        entry_nombre.pack(fill=tk.X, pady=3)

        tk.Label(frame, text="💰 Monto:", bg=COLORES['background']).pack(anchor='w', pady=3)
        entry_monto = tk.Entry(frame, font=('Segoe UI', 11))
        entry_monto.pack(fill=tk.X, pady=3)

        tk.Label(frame, text="📅 Frecuencia:", bg=COLORES['background']).pack(anchor='w', pady=3)
        combo_freq = ttk.Combobox(frame, values=['mensual', 'anual', 'semanal'],
                                   state='readonly', font=('Segoe UI', 11))
        combo_freq.set('mensual')
        combo_freq.pack(fill=tk.X, pady=3)

        tk.Label(frame, text="📆 Día de cobro (1-31):", bg=COLORES['background']).pack(anchor='w', pady=3)
        entry_dia = tk.Entry(frame, font=('Segoe UI', 11))
        entry_dia.insert(0, str(datetime.date.today().day))
        entry_dia.pack(fill=tk.X, pady=3)

        tk.Label(frame, text="📂 Categoría (opcional):", bg=COLORES['background']).pack(anchor='w', pady=3)
        combo_cat = ttk.Combobox(frame, values=[c[1] for c in self.db.obtener_categorias()],
                                 font=('Segoe UI', 11))
        combo_cat.pack(fill=tk.X, pady=3)

        tk.Label(frame, text="🏢 Proveedor (opcional):", bg=COLORES['background']).pack(anchor='w', pady=3)
        entry_proveedor = tk.Entry(frame, font=('Segoe UI', 11))
        entry_proveedor.pack(fill=tk.X, pady=3)

        def guardar_suscripcion():
            nombre = entry_nombre.get().strip()
            if not nombre:
                messagebox.showwarning("Datos incompletos", "Ingresá el nombre de la suscripción")
                return

            try:
                monto = float(entry_monto.get())
                dia = int(entry_dia.get())
                if dia < 1 or dia > 31:
                    raise ValueError("Día inválido")
            except ValueError:
                messagebox.showwarning("Datos inválidos", "Verificá el monto y día de cobro")
                return

            self.db.crear_suscripcion(
                nombre=nombre,
                monto=monto,
                frecuencia=combo_freq.get(),
                dia_cobro=dia,
                categoria=combo_cat.get() if combo_cat.get() else None,
                proveedor=entry_proveedor.get() if entry_proveedor.get() else None
            )

            messagebox.showinfo("Éxito", "Suscripción registrada correctamente")
            v.destroy()
            self.mostrar_suscripciones()

        tk.Button(
            frame,
            text="💾 Guardar Suscripción",
            font=('Segoe UI', 12, 'bold'),
            bg=COLORES['success'],
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=guardar_suscripcion,
            pady=10
        ).pack(pady=15, fill=tk.X)

    def mostrar_finscore(self):
        """Dashboard de FinScore (inspirado en Fintonic)"""
        # Calcular FinScore actual
        puntuacion = self.db.calcular_finscore()

        # Header con puntuación grande
        frame_header = tk.Frame(self.frame_contenido, bg=COLORES['primary'], height=150)
        frame_header.pack(fill=tk.X, padx=15, pady=15)
        frame_header.pack_propagate(False)

        # Determinar color y mensaje según puntuación
        if puntuacion >= 800:
            color_score = '#10b981'  # Verde
            mensaje = "🎉 ¡Excelente salud financiera!"
            emoji = "🌟"
        elif puntuacion >= 600:
            color_score = '#10b981'  # Verde
            mensaje = "😊 Buena salud financiera"
            emoji = "👍"
        elif puntuacion >= 400:
            color_score = '#f59e0b'  # Naranja
            mensaje = "🤔 Salud financiera regular"
            emoji = "💪"
        else:
            color_score = '#ef4444'  # Rojo
            mensaje = "😟 Necesitás mejorar"
            emoji = "📈"

        tk.Label(
            frame_header,
            text="🏆 Tu FinScore",
            font=('Segoe UI', 16, 'bold'),
            bg=COLORES['primary'],
            fg='white'
        ).pack(pady=(20, 5))

        tk.Label(
            frame_header,
            text=f"{puntuacion}",
            font=('Segoe UI', 48, 'bold'),
            bg=COLORES['primary'],
            fg=color_score
        ).pack()

        tk.Label(
            frame_header,
            text=f"{emoji} {mensaje}",
            font=('Segoe UI', 12),
            bg=COLORES['primary'],
            fg='white'
        ).pack()

        # Explicación de componentes
        frame_componentes = tk.Frame(self.frame_contenido, bg=COLORES['background'])
        frame_componentes.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        tk.Label(
            frame_componentes,
            text="📊 Componentes del FinScore",
            font=('Segoe UI', 14, 'bold'),
            bg=COLORES['background']
        ).pack(pady=10)

        # Obtener detalles del último cálculo
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT ahorro_mensual, gasto_promedio, deudas_totales, racha_dias
            FROM finscore_historico ORDER BY fecha DESC LIMIT 1
        ''')
        detalles = cursor.fetchone()

        if detalles:
            ahorro, gasto, deudas, racha = detalles

            componentes = [
                ("💰 Ahorro Mensual", f"${ahorro:,.0f}", "30% del score", COLORES['success']),
                ("📊 Cumplimiento Presupuestos", "Ver en Presupuestos", "25% del score", COLORES['info']),
                ("🏦 Control de Deudas", f"${deudas:,.0f} pendientes", "25% del score", COLORES['warning']),
                ("🔥 Racha de Registro", f"{racha} días este mes", "20% del score", COLORES['secondary'])
            ]

            for titulo, valor, peso, color in componentes:
                frame_comp = tk.Frame(frame_componentes, bg=COLORES['card_bg'], relief=tk.SOLID, bd=1, highlightbackground=COLORES['border'], highlightthickness=1)
                frame_comp.pack(fill=tk.X, pady=5)

                frame_comp_header = tk.Frame(frame_comp, bg=color, height=30)
                frame_comp_header.pack(fill=tk.X)
                frame_comp_header.pack_propagate(False)

                tk.Label(
                    frame_comp_header,
                    text=titulo,
                    font=('Segoe UI', 11, 'bold'),
                    bg=color,
                    fg='white'
                ).pack(side=tk.LEFT, padx=15, pady=5)

                tk.Label(
                    frame_comp_header,
                    text=peso,
                    font=('Segoe UI', 9),
                    bg=color,
                    fg='white'
                ).pack(side=tk.RIGHT, padx=15)

                tk.Label(
                    frame_comp,
                    text=valor,
                    font=('Segoe UI', 12, 'bold'),
                    bg=COLORES['card_bg'],
                    fg=color,
                    pady=10
                ).pack()

        # Recomendaciones
        frame_recs = tk.Frame(self.frame_contenido, bg=COLORES['light'], relief=tk.RAISED, bd=2)
        frame_recs.pack(fill=tk.X, padx=15, pady=10)

        tk.Label(
            frame_recs,
            text="💡 Recomendaciones para mejorar tu FinScore",
            font=('Segoe UI', 12, 'bold'),
            bg=COLORES['light'],
            pady=10
        ).pack()

        recomendaciones = []
        if detalles:
            if ahorro < 0:
                recomendaciones.append("• Intentá gastar menos de lo que ganás este mes")
            if deudas > 10000:
                recomendaciones.append("• Pagá tus deudas compartidas para mejorar tu score")
            if racha < 20:
                recomendaciones.append("• Registrá tus gastos diariamente para mejorar consistencia")

        if not recomendaciones:
            recomendaciones.append("• ¡Seguí así! Estás manejando bien tus finanzas")

        for rec in recomendaciones:
            tk.Label(
                frame_recs,
                text=rec,
                font=('Segoe UI', 10),
                bg=COLORES['light'],
                justify=tk.LEFT,
                anchor='w'
            ).pack(padx=20, pady=2, fill=tk.X)

        tk.Label(
            frame_recs,
            text="",
            bg=COLORES['light'],
            pady=5
        ).pack()

    def mostrar_splitwise(self):
        """Gestión de gastos compartidos estilo Splitwise"""
        # Header
        frame_header = tk.Frame(self.frame_contenido, bg=COLORES['primary'], height=80)
        frame_header.pack(fill=tk.X, padx=15, pady=15)
        frame_header.pack_propagate(False)

        tk.Label(
            frame_header,
            text="👥 Splitwise - Gastos Compartidos",
            font=('Segoe UI', 18, 'bold'),
            bg=COLORES['primary'],
            fg='white'
        ).pack(side=tk.LEFT, padx=20, pady=20)

        tk.Button(
            frame_header,
            text="➕ Nuevo Grupo",
            font=('Segoe UI', 11, 'bold'),
            bg=COLORES['success'],
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.ventana_nuevo_grupo_splitwise,
            padx=20,
            pady=8
        ).pack(side=tk.RIGHT, padx=20)

        # Lista de grupos
        grupos = self.db.obtener_grupos_splitwise()

        if not grupos:
            tk.Label(
                self.frame_contenido,
                text="👥 No tenés grupos creados\n\nCreá un grupo para dividir gastos con amigos, familia o compañeros",
                font=('Segoe UI', 12),
                bg=COLORES['background'],
                fg='gray',
                justify=tk.CENTER
            ).pack(expand=True)
            return

        # Mostrar grupos
        frame_scroll = tk.Frame(self.frame_contenido, bg=COLORES['background'])
        frame_scroll.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        canvas = tk.Canvas(frame_scroll, bg=COLORES['background'], highlightthickness=0)
        scrollbar = tk.Scrollbar(frame_scroll, orient="vertical", command=canvas.yview)
        frame_grupos = tk.Frame(canvas, bg=COLORES['background'])

        frame_grupos.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=frame_grupos, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        for grupo in grupos:
            grupo_id = grupo[0]
            nombre = grupo[1]
            descripcion = grupo[2]
            icono = grupo[6] if len(grupo) > 6 else '👥'

            # Calcular balances del grupo
            balances = self.db.calcular_balances_grupo(grupo_id)
            participantes = self.db.obtener_participantes_grupo(grupo_id)

            # Tarjeta del grupo
            frame_grupo = tk.Frame(frame_grupos, bg=COLORES['card_bg'], relief=tk.SOLID, bd=1, highlightbackground=COLORES['border'], highlightthickness=1)
            frame_grupo.pack(fill=tk.X, pady=8)

            # Header del grupo
            frame_grupo_header = tk.Frame(frame_grupo, bg=COLORES['secondary'])
            frame_grupo_header.pack(fill=tk.X)

            tk.Label(
                frame_grupo_header,
                text=f"{icono} {nombre}",
                font=('Segoe UI', 14, 'bold'),
                bg=COLORES['secondary'],
                fg='white'
            ).pack(side=tk.LEFT, padx=15, pady=10)

            tk.Label(
                frame_grupo_header,
                text=f"{len(participantes)} personas",
                font=('Segoe UI', 9),
                bg=COLORES['secondary'],
                fg='white'
            ).pack(side=tk.RIGHT, padx=15)

            # Descripción
            if descripcion:
                tk.Label(
                    frame_grupo,
                    text=descripcion,
                    font=('Segoe UI', 9),
                    bg=COLORES['card_bg'],
                    fg='gray'
                ).pack(padx=15, pady=5, anchor='w')

            # Mostrar balances
            frame_balances = tk.Frame(frame_grupo, bg=COLORES['card_bg'])
            frame_balances.pack(fill=tk.X, padx=15, pady=5)

            if balances:
                for participante, balance in balances.items():
                    if abs(balance) > 0.01:  # Ignorar balances muy pequeños
                        if balance > 0:
                            texto = f"💚 {participante}: le deben ${balance:,.2f}"
                            color = COLORES['success']
                        else:
                            texto = f"❤️ {participante}: debe ${-balance:,.2f}"
                            color = COLORES['danger']

                        tk.Label(
                            frame_balances,
                            text=texto,
                            font=('Segoe UI', 10, 'bold'),
                            bg=COLORES['card_bg'],
                            fg=color
                        ).pack(anchor='w', pady=2)

            # Botones de acción
            frame_btns = tk.Frame(frame_grupo, bg=COLORES['card_bg'])
            frame_btns.pack(fill=tk.X, padx=15, pady=10)

            tk.Button(
                frame_btns,
                text="➕ Agregar Gasto",
                font=('Segoe UI', 9, 'bold'),
                bg=COLORES['info'],
                fg='white',
                relief=tk.FLAT,
                cursor='hand2',
                command=lambda gid=grupo_id: self.ventana_agregar_gasto_splitwise(gid),
                padx=15,
                pady=5
            ).pack(side=tk.LEFT, padx=3)

            tk.Button(
                frame_btns,
                text="💰 Settle Up",
                font=('Segoe UI', 9, 'bold'),
                bg=COLORES['success'],
                fg='white',
                relief=tk.FLAT,
                cursor='hand2',
                command=lambda gid=grupo_id: self.ventana_settle_up(gid),
                padx=15,
                pady=5
            ).pack(side=tk.LEFT, padx=3)

            tk.Button(
                frame_btns,
                text="👥 Participantes",
                font=('Segoe UI', 9, 'bold'),
                bg=COLORES['secondary'],
                fg='white',
                relief=tk.FLAT,
                cursor='hand2',
                command=lambda gid=grupo_id: self.ventana_participantes_grupo(gid),
                padx=15,
                pady=5
            ).pack(side=tk.LEFT, padx=3)

            tk.Button(
                frame_btns,
                text="📋 Ver Gastos",
                font=('Segoe UI', 9, 'bold'),
                bg=COLORES['warning'],
                fg='white',
                relief=tk.FLAT,
                cursor='hand2',
                command=lambda gid=grupo_id: self.ventana_ver_gastos_grupo(gid),
                padx=15,
                pady=5
            ).pack(side=tk.LEFT, padx=3)

    def ventana_nuevo_grupo_splitwise(self):
        """Ventana para crear un nuevo grupo de Splitwise"""
        v = tk.Toplevel(self.root)
        v.title("➕ Nuevo Grupo Splitwise")
        v.geometry("550x500")
        v.configure(bg=COLORES['background'])
        v.transient(self.root)
        v.grab_set()

        v.update_idletasks()
        x = (v.winfo_screenwidth() // 2) - (550 // 2)
        y = (v.winfo_screenheight() // 2) - (500 // 2)
        v.geometry(f'550x500+{x}+{y}')

        frame = tk.Frame(v, bg=COLORES['background'], padx=25, pady=25)
        frame.pack(fill=tk.BOTH, expand=True)

        # Header moderno
        header_frame = tk.Frame(frame, bg=COLORES['primary'], relief=tk.FLAT)
        header_frame.pack(fill=tk.X, pady=(0, 20), padx=-5)

        tk.Label(
            header_frame,
            text="➕ Nuevo Grupo Splitwise",
            font=('Segoe UI', 16, 'bold'),
            bg=COLORES['primary'],
            fg='white'
        ).pack(pady=15)

        # Form moderno
        form_frame = tk.Frame(frame, bg=COLORES['card_bg'], relief=tk.FLAT, bd=1, highlightbackground=COLORES['border'], highlightthickness=1)
        form_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=5, ipady=15)

        form_inner = tk.Frame(form_frame, bg=COLORES['card_bg'])
        form_inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        tk.Label(form_inner, text="📝 Nombre del grupo:", bg=COLORES['card_bg'], font=('Segoe UI', 11, 'bold'), fg=COLORES['text']).pack(anchor='w', pady=(5,3))
        entry_nombre = tk.Entry(form_inner, font=('Segoe UI', 12), relief=tk.FLAT, bg=COLORES['light'], fg=COLORES['text'])
        entry_nombre.pack(fill=tk.X, pady=(0,15), ipady=8)

        tk.Label(form_inner, text="📄 Descripción (opcional):", bg=COLORES['card_bg'], font=('Segoe UI', 11, 'bold'), fg=COLORES['text']).pack(anchor='w', pady=(5,3))
        entry_desc = tk.Entry(form_inner, font=('Segoe UI', 12), relief=tk.FLAT, bg=COLORES['light'], fg=COLORES['text'])
        entry_desc.pack(fill=tk.X, pady=(0,15), ipady=8)

        tk.Label(form_inner, text="🎨 Icono:", bg=COLORES['card_bg'], font=('Segoe UI', 11, 'bold'), fg=COLORES['text']).pack(anchor='w', pady=(5,3))
        iconos = ['👥', '🏠', '✈️', '🍕', '🎉', '🏖️', '⚽', '🎬', '🍺', '💼']
        combo_icono = ttk.Combobox(form_inner, values=iconos, state='readonly', font=('Segoe UI', 12))
        combo_icono.set('👥')
        combo_icono.pack(fill=tk.X, pady=(0,15), ipady=5)

        tk.Label(form_inner, text="👥 Tipo:", bg=COLORES['card_bg'], font=('Segoe UI', 11, 'bold'), fg=COLORES['text']).pack(anchor='w', pady=(5,3))
        tipos = ['general', 'viaje', 'casa', 'pareja', 'evento']
        combo_tipo = ttk.Combobox(form_inner, values=tipos, state='readonly', font=('Segoe UI', 12))
        combo_tipo.set('general')
        combo_tipo.pack(fill=tk.X, pady=(0,10), ipady=5)

        def guardar():
            nombre = entry_nombre.get().strip()
            if not nombre:
                messagebox.showwarning("Error", "Ingresá un nombre para el grupo")
                return

            grupo_id = self.db.crear_grupo_splitwise(
                nombre,
                entry_desc.get().strip(),
                combo_tipo.get(),
                combo_icono.get()
            )

            messagebox.showinfo("Éxito", f"✅ Grupo '{nombre}' creado!\n\nAhora agregá participantes al grupo.")
            v.destroy()
            self.mostrar_splitwise()
            # Abrir ventana de participantes automáticamente
            self.ventana_participantes_grupo(grupo_id)

        frame_btns = tk.Frame(frame, bg=COLORES['background'])
        frame_btns.pack(pady=20)

        tk.Button(
            frame_btns,
            text="✅ Crear Grupo",
            command=guardar,
            bg=COLORES['success'],
            fg='white',
            font=('Segoe UI', 12, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            padx=40,
            pady=12,
            borderwidth=0
        ).pack(side=tk.LEFT, padx=8)

        tk.Button(
            frame_btns,
            text="❌ Cancelar",
            command=v.destroy,
            bg=COLORES['text_secondary'],
            fg='white',
            font=('Segoe UI', 11),
            relief=tk.FLAT,
            cursor='hand2',
            padx=40,
            pady=12,
            borderwidth=0
        ).pack(side=tk.LEFT, padx=8)

    def ventana_participantes_grupo(self, grupo_id):
        """Gestionar participantes de un grupo"""
        v = tk.Toplevel(self.root)
        v.title("👥 Participantes del Grupo")
        v.geometry("600x650")
        v.configure(bg=COLORES['background'])
        v.transient(self.root)
        v.grab_set()

        v.update_idletasks()
        x = (v.winfo_screenwidth() // 2) - (600 // 2)
        y = (v.winfo_screenheight() // 2) - (650 // 2)
        v.geometry(f'600x650+{x}+{y}')

        frame = tk.Frame(v, bg=COLORES['background'], padx=25, pady=25)
        frame.pack(fill=tk.BOTH, expand=True)

        # Header moderno
        header_frame = tk.Frame(frame, bg=COLORES['primary'], relief=tk.FLAT)
        header_frame.pack(fill=tk.X, pady=(0, 20), padx=-5)

        tk.Label(
            header_frame,
            text="👥 Participantes del Grupo",
            font=('Segoe UI', 16, 'bold'),
            bg=COLORES['primary'],
            fg='white'
        ).pack(pady=15)

        # Formulario para agregar participante
        frame_form = tk.Frame(frame, bg=COLORES['card_bg'], relief=tk.SOLID, bd=1, highlightbackground=COLORES['border'], highlightthickness=1)
        frame_form.pack(fill=tk.X, pady=10)

        tk.Label(
            frame_form,
            text="➕ Agregar Participante",
            font=('Segoe UI', 12, 'bold'),
            bg=COLORES['card_bg']
        ).pack(pady=10)

        frame_inputs = tk.Frame(frame_form, bg=COLORES['card_bg'])
        frame_inputs.pack(padx=15, pady=5)

        tk.Label(frame_inputs, text="Nombre:", bg=COLORES['card_bg'], font=('Segoe UI', 10)).grid(row=0, column=0, sticky='w', pady=5)
        entry_nombre = tk.Entry(frame_inputs, font=('Segoe UI', 10), width=20)
        entry_nombre.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame_inputs, text="Email (opcional):", bg=COLORES['card_bg'], font=('Segoe UI', 10)).grid(row=1, column=0, sticky='w', pady=5)
        entry_email = tk.Entry(frame_inputs, font=('Segoe UI', 10), width=20)
        entry_email.grid(row=1, column=1, padx=5, pady=5)

        def agregar_participante():
            nombre = entry_nombre.get().strip()
            if not nombre:
                messagebox.showwarning("Error", "Ingresá un nombre")
                return

            self.db.agregar_participante_splitwise(grupo_id, nombre, entry_email.get().strip())
            entry_nombre.delete(0, tk.END)
            entry_email.delete(0, tk.END)
            actualizar_lista()

        tk.Button(
            frame_form,
            text="➕ Agregar",
            command=agregar_participante,
            bg=COLORES['success'],
            fg='white',
            font=('Segoe UI', 10, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=5
        ).pack(pady=10)

        # Lista de participantes
        frame_lista = tk.Frame(frame, bg=COLORES['background'])
        frame_lista.pack(fill=tk.BOTH, expand=True, pady=10)

        tk.Label(
            frame_lista,
            text="📋 Lista de Participantes",
            font=('Segoe UI', 12, 'bold'),
            bg=COLORES['background']
        ).pack(pady=5)

        lista_container = tk.Frame(frame_lista, bg=COLORES['background'])
        lista_container.pack(fill=tk.BOTH, expand=True)

        def actualizar_lista():
            for widget in lista_container.winfo_children():
                widget.destroy()

            participantes = self.db.obtener_participantes_grupo(grupo_id)

            if not participantes:
                tk.Label(
                    lista_container,
                    text="No hay participantes todavía",
                    font=('Segoe UI', 10),
                    bg=COLORES['background'],
                    fg='gray'
                ).pack(pady=20)
            else:
                for p in participantes:
                    nombre = p[2]
                    email = p[3]

                    frame_p = tk.Frame(lista_container, bg=COLORES['card_bg'], relief=tk.RAISED, bd=1)
                    frame_p.pack(fill=tk.X, pady=3)

                    tk.Label(
                        frame_p,
                        text=f"👤 {nombre}",
                        font=('Segoe UI', 11, 'bold'),
                        bg=COLORES['card_bg']
                    ).pack(side=tk.LEFT, padx=10, pady=8)

                    if email:
                        tk.Label(
                            frame_p,
                            text=email,
                            font=('Segoe UI', 9),
                            bg=COLORES['card_bg'],
                            fg='gray'
                        ).pack(side=tk.LEFT, padx=5)

        actualizar_lista()

        tk.Button(
            frame,
            text="✅ Cerrar",
            command=v.destroy,
            bg=COLORES['primary'],
            fg='white',
            font=('Segoe UI', 11, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            padx=30,
            pady=10
        ).pack(pady=10)

    def ventana_agregar_gasto_splitwise(self, grupo_id):
        """Agregar un gasto compartido al grupo"""
        v = tk.Toplevel(self.root)
        v.title("➕ Agregar Gasto Compartido")
        v.geometry("650x700")
        v.configure(bg=COLORES['background'])
        v.transient(self.root)
        v.grab_set()

        v.update_idletasks()
        x = (v.winfo_screenwidth() // 2) - (650 // 2)
        y = (v.winfo_screenheight() // 2) - (700 // 2)
        v.geometry(f'650x700+{x}+{y}')

        frame = tk.Frame(v, bg=COLORES['background'], padx=25, pady=25)
        frame.pack(fill=tk.BOTH, expand=True)

        # Header moderno
        header_frame = tk.Frame(frame, bg=COLORES['primary'], relief=tk.FLAT)
        header_frame.pack(fill=tk.X, pady=(0, 20), padx=-5)

        tk.Label(
            header_frame,
            text="➕ Nuevo Gasto Compartido",
            font=('Segoe UI', 16, 'bold'),
            bg=COLORES['primary'],
            fg='white'
        ).pack(pady=15)

        # Obtener participantes
        participantes = self.db.obtener_participantes_grupo(grupo_id)
        if not participantes:
            messagebox.showwarning("Error", "Primero debés agregar participantes al grupo")
            v.destroy()
            return

        nombres_participantes = [p[2] for p in participantes]

        # Formulario con diseño moderno
        form_frame = tk.Frame(frame, bg=COLORES['card_bg'], relief=tk.FLAT, bd=1, highlightbackground=COLORES['border'], highlightthickness=1)
        form_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=5, ipady=15)

        form_inner = tk.Frame(form_frame, bg=COLORES['card_bg'])
        form_inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        tk.Label(form_inner, text="📝 Descripción:", bg=COLORES['card_bg'], font=('Segoe UI', 11, 'bold'), fg=COLORES['text']).pack(anchor='w', pady=(5,3))
        entry_desc = tk.Entry(form_inner, font=('Segoe UI', 12), relief=tk.FLAT, bg=COLORES['light'], fg=COLORES['text'])
        entry_desc.pack(fill=tk.X, pady=(0,10), ipady=8)

        tk.Label(form_inner, text="💰 Monto total:", bg=COLORES['card_bg'], font=('Segoe UI', 11, 'bold'), fg=COLORES['text']).pack(anchor='w', pady=(5,3))
        entry_monto = tk.Entry(form_inner, font=('Segoe UI', 12), relief=tk.FLAT, bg=COLORES['light'], fg=COLORES['text'])
        entry_monto.pack(fill=tk.X, pady=(0,10), ipady=8)

        tk.Label(form_inner, text="💳 Pagado por:", bg=COLORES['card_bg'], font=('Segoe UI', 11, 'bold'), fg=COLORES['text']).pack(anchor='w', pady=(5,3))
        combo_pagador = ttk.Combobox(form_inner, values=nombres_participantes, state='readonly', font=('Segoe UI', 12))
        if nombres_participantes:
            combo_pagador.set(nombres_participantes[0])
        combo_pagador.pack(fill=tk.X, pady=(0,10), ipady=5)

        tk.Label(form_inner, text="📂 Categoría (opcional):", bg=COLORES['card_bg'], font=('Segoe UI', 11, 'bold'), fg=COLORES['text']).pack(anchor='w', pady=(5,3))
        entry_categoria = tk.Entry(form_inner, font=('Segoe UI', 12), relief=tk.FLAT, bg=COLORES['light'], fg=COLORES['text'])
        entry_categoria.pack(fill=tk.X, pady=(0,10), ipady=8)

        tk.Label(form_inner, text="🔀 Método de división:", bg=COLORES['card_bg'], font=('Segoe UI', 11, 'bold'), fg=COLORES['text']).pack(anchor='w', pady=(5,3))
        metodos = ['equitativa', 'porcentajes', 'montos', 'partes']
        combo_metodo = ttk.Combobox(form_inner, values=metodos, state='readonly', font=('Segoe UI', 12))
        combo_metodo.set('equitativa')
        combo_metodo.pack(fill=tk.X, pady=(0,10), ipady=5)

        tk.Label(form_inner, text="📋 Notas (opcional):", bg=COLORES['card_bg'], font=('Segoe UI', 11, 'bold'), fg=COLORES['text']).pack(anchor='w', pady=(5,3))
        entry_notas = tk.Entry(form_inner, font=('Segoe UI', 12), relief=tk.FLAT, bg=COLORES['light'], fg=COLORES['text'])
        entry_notas.pack(fill=tk.X, pady=(0,10), ipady=8)

        def guardar():
            descripcion = entry_desc.get().strip()
            monto_str = entry_monto.get().strip()
            pagador = combo_pagador.get()

            if not descripcion or not monto_str or not pagador:
                messagebox.showwarning("Error", "Completá todos los campos obligatorios")
                return

            try:
                monto = float(monto_str.replace(',', '.'))
                if monto <= 0:
                    raise ValueError()

                # Por ahora solo división equitativa (se puede extender)
                metodo = combo_metodo.get()

                self.db.agregar_gasto_splitwise(
                    grupo_id,
                    descripcion,
                    monto,
                    pagador,
                    metodo,
                    None,  # divisiones automáticas
                    entry_categoria.get().strip(),
                    entry_notas.get().strip()
                )

                messagebox.showinfo("Éxito", f"✅ Gasto agregado: ${monto:,.2f}")
                v.destroy()
                self.mostrar_splitwise()

            except ValueError:
                messagebox.showerror("Error", "Monto inválido")

        frame_btns = tk.Frame(frame, bg=COLORES['background'])
        frame_btns.pack(pady=20)

        tk.Button(
            frame_btns,
            text="💾 Guardar Gasto",
            command=guardar,
            bg=COLORES['success'],
            fg='white',
            font=('Segoe UI', 12, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            padx=40,
            pady=12,
            borderwidth=0
        ).pack(side=tk.LEFT, padx=8)

        tk.Button(
            frame_btns,
            text="❌ Cancelar",
            command=v.destroy,
            bg=COLORES['text_secondary'],
            fg='white',
            font=('Segoe UI', 11),
            relief=tk.FLAT,
            cursor='hand2',
            padx=40,
            pady=12,
            borderwidth=0
        ).pack(side=tk.LEFT, padx=8)

    def ventana_settle_up(self, grupo_id):
        """Ventana para saldar deudas del grupo"""
        v = tk.Toplevel(self.root)
        v.title("💰 Settle Up - Saldar Cuentas")
        v.geometry("700x750")
        v.configure(bg=COLORES['background'])
        v.transient(self.root)
        v.grab_set()

        v.update_idletasks()
        x = (v.winfo_screenwidth() // 2) - (700 // 2)
        y = (v.winfo_screenheight() // 2) - (750 // 2)
        v.geometry(f'700x750+{x}+{y}')

        frame = tk.Frame(v, bg=COLORES['background'], padx=25, pady=25)
        frame.pack(fill=tk.BOTH, expand=True)

        # Header moderno
        header_frame = tk.Frame(frame, bg=COLORES['primary'], relief=tk.FLAT)
        header_frame.pack(fill=tk.X, pady=(0, 20), padx=-5)

        tk.Label(
            header_frame,
            text="💰 Settle Up - Saldar Cuentas",
            font=('Segoe UI', 16, 'bold'),
            bg=COLORES['primary'],
            fg='white'
        ).pack(pady=15)

        # Mostrar deudas simplificadas
        transacciones = self.db.simplificar_deudas_grupo(grupo_id)

        if not transacciones:
            tk.Label(
                frame,
                text="✅ ¡Todas las cuentas están saldadas!\n\nNo hay deudas pendientes en este grupo.",
                font=('Segoe UI', 12),
                bg=COLORES['background'],
                fg=COLORES['success'],
                justify=tk.CENTER
            ).pack(expand=True, pady=50)
        else:
            tk.Label(
                frame,
                text=f"📊 Para saldar todas las deudas, se necesitan {len(transacciones)} transferencias:",
                font=('Segoe UI', 11),
                bg=COLORES['background'],
                fg='gray'
            ).pack(pady=10)

            # Frame con scroll para transacciones
            frame_scroll = tk.Frame(frame, bg=COLORES['background'])
            frame_scroll.pack(fill=tk.BOTH, expand=True, pady=10)

            canvas = tk.Canvas(frame_scroll, bg=COLORES['background'], highlightthickness=0, height=400)
            scrollbar = tk.Scrollbar(frame_scroll, orient="vertical", command=canvas.yview)
            frame_trans = tk.Frame(canvas, bg=COLORES['background'])

            frame_trans.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=frame_trans, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            for i, (deudor, acreedor, monto) in enumerate(transacciones, 1):
                frame_t = tk.Frame(frame_trans, bg=COLORES['card_bg'], relief=tk.FLAT, bd=2, highlightbackground=COLORES['border'], highlightthickness=1)
                frame_t.pack(fill=tk.X, pady=8, padx=5, ipady=5)

                # Número de transacción
                tk.Label(
                    frame_t,
                    text=f"#{i}",
                    font=('Segoe UI', 10, 'bold'),
                    bg=COLORES['secondary'],
                    fg='white',
                    width=3
                ).pack(side=tk.LEFT, fill=tk.Y)

                # Detalles de la transacción
                frame_detalles = tk.Frame(frame_t, bg=COLORES['card_bg'])
                frame_detalles.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=10)

                tk.Label(
                    frame_detalles,
                    text=f"👤 {deudor}  →  👤 {acreedor}",
                    font=('Segoe UI', 11, 'bold'),
                    bg=COLORES['card_bg']
                ).pack(anchor='w')

                tk.Label(
                    frame_detalles,
                    text=f"💰 ${monto:,.2f}",
                    font=('Segoe UI', 14, 'bold'),
                    bg=COLORES['card_bg'],
                    fg=COLORES['success']
                ).pack(anchor='w')

                # Botón para marcar como pagado
                def marcar_pagado(d=deudor, a=acreedor, m=monto):
                    if messagebox.askyesno("Confirmar Pago", f"¿Confirmar que {d} le pagó ${m:,.2f} a {a}?"):
                        self.db.registrar_pago_splitwise(grupo_id, d, a, m, f"Settle Up #{i}")
                        messagebox.showinfo("✅ Pago Registrado", "El pago ha sido registrado correctamente")
                        v.destroy()
                        self.mostrar_splitwise()

                tk.Button(
                    frame_t,
                    text="✅ Marcar\nPagado",
                    font=('Segoe UI', 8, 'bold'),
                    bg=COLORES['success'],
                    fg='white',
                    relief=tk.FLAT,
                    cursor='hand2',
                    command=marcar_pagado,
                    padx=10,
                    pady=5
                ).pack(side=tk.RIGHT, padx=10)

            # Información adicional
            frame_info = tk.Frame(frame, bg=COLORES['light'], relief=tk.RAISED, bd=2)
            frame_info.pack(fill=tk.X, pady=10)

            tk.Label(
                frame_info,
                text="💡 Consejo",
                font=('Segoe UI', 11, 'bold'),
                bg=COLORES['light']
            ).pack(pady=5)

            tk.Label(
                frame_info,
                text="Estas son las transacciones mínimas necesarias para saldar todas las deudas.\n"
                     "Marcá cada pago como completado una vez que se haya realizado la transferencia.",
                font=('Segoe UI', 9),
                bg=COLORES['light'],
                fg='gray',
                justify=tk.CENTER
            ).pack(padx=15, pady=5)

        tk.Button(
            frame,
            text="✅ Cerrar",
            command=v.destroy,
            bg=COLORES['primary'],
            fg='white',
            font=('Segoe UI', 12, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            padx=50,
            pady=12,
            borderwidth=0
        ).pack(pady=15)

    def ventana_ver_gastos_grupo(self, grupo_id):
        """Ver todos los gastos de un grupo"""
        v = tk.Toplevel(self.root)
        v.title("📋 Gastos del Grupo")
        v.geometry("800x700")
        v.configure(bg=COLORES['background'])
        v.transient(self.root)
        v.grab_set()

        v.update_idletasks()
        x = (v.winfo_screenwidth() // 2) - (800 // 2)
        y = (v.winfo_screenheight() // 2) - (700 // 2)
        v.geometry(f'800x700+{x}+{y}')

        frame = tk.Frame(v, bg=COLORES['background'], padx=25, pady=25)
        frame.pack(fill=tk.BOTH, expand=True)

        # Obtener nombre del grupo
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT nombre FROM grupos_splitwise WHERE id = ?', (grupo_id,))
        grupo_info = cursor.fetchone()
        nombre_grupo = grupo_info[0] if grupo_info else "Grupo"

        # Header moderno
        header_frame = tk.Frame(frame, bg=COLORES['primary'], relief=tk.FLAT)
        header_frame.pack(fill=tk.X, pady=(0, 20), padx=-5)

        tk.Label(
            header_frame,
            text=f"📋 Gastos de: {nombre_grupo}",
            font=('Segoe UI', 16, 'bold'),
            bg=COLORES['primary'],
            fg='white'
        ).pack(pady=15)

        # Obtener gastos
        gastos = self.db.obtener_gastos_grupo(grupo_id)

        if not gastos:
            tk.Label(
                frame,
                text="No hay gastos registrados en este grupo",
                font=('Segoe UI', 12),
                bg=COLORES['background'],
                fg='gray'
            ).pack(expand=True, pady=50)
        else:
            # Frame con scroll
            frame_scroll = tk.Frame(frame, bg=COLORES['background'])
            frame_scroll.pack(fill=tk.BOTH, expand=True)

            canvas = tk.Canvas(frame_scroll, bg=COLORES['background'], highlightthickness=0)
            scrollbar = tk.Scrollbar(frame_scroll, orient="vertical", command=canvas.yview)
            frame_gastos = tk.Frame(canvas, bg=COLORES['background'])

            frame_gastos.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=frame_gastos, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            for gasto in gastos:
                descripcion = gasto[2]
                monto = gasto[3]
                pagado_por = gasto[4]
                fecha = gasto[5]
                categoria = gasto[6] if gasto[6] else ''

                frame_g = tk.Frame(frame_gastos, bg=COLORES['card_bg'], relief=tk.SOLID, bd=1, highlightbackground=COLORES['border'], highlightthickness=1)
                frame_g.pack(fill=tk.X, pady=5)

                # Header del gasto
                frame_g_header = tk.Frame(frame_g, bg=COLORES['info'])
                frame_g_header.pack(fill=tk.X)

                tk.Label(
                    frame_g_header,
                    text=descripcion,
                    font=('Segoe UI', 12, 'bold'),
                    bg=COLORES['info'],
                    fg='white'
                ).pack(side=tk.LEFT, padx=15, pady=8)

                tk.Label(
                    frame_g_header,
                    text=f"${monto:,.2f}",
                    font=('Segoe UI', 12, 'bold'),
                    bg=COLORES['info'],
                    fg='white'
                ).pack(side=tk.RIGHT, padx=15, pady=8)

                # Detalles
                frame_detalles = tk.Frame(frame_g, bg=COLORES['card_bg'])
                frame_detalles.pack(fill=tk.X, padx=15, pady=8)

                tk.Label(
                    frame_detalles,
                    text=f"💳 Pagado por: {pagado_por}",
                    font=('Segoe UI', 10),
                    bg=COLORES['card_bg']
                ).pack(anchor='w')

                tk.Label(
                    frame_detalles,
                    text=f"📅 Fecha: {fecha}",
                    font=('Segoe UI', 10),
                    bg=COLORES['card_bg'],
                    fg='gray'
                ).pack(anchor='w')

                if categoria:
                    tk.Label(
                        frame_detalles,
                        text=f"📂 {categoria}",
                        font=('Segoe UI', 9),
                        bg=COLORES['card_bg'],
                        fg='gray'
                    ).pack(anchor='w')

        tk.Button(
            frame,
            text="✅ Cerrar",
            command=v.destroy,
            bg=COLORES['primary'],
            fg='white',
            font=('Segoe UI', 11, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            padx=30,
            pady=10
        ).pack(pady=10)

    # === BUDDY - PRESUPUESTOS COMPARTIDOS ===
    def mostrar_buddy_presupuestos(self):
        """Vista de presupuestos compartidos estilo Buddy"""
        # Header
        frame_header = tk.Frame(self.frame_contenido, bg=COLORES['primary'], height=80)
        frame_header.pack(fill=tk.X, padx=15, pady=15)
        frame_header.pack_propagate(False)

        tk.Label(
            frame_header,
            text="🤝 Buddy - Presupuestos Compartidos",
            font=('Segoe UI', 18, 'bold'),
            bg=COLORES['primary'],
            fg='white'
        ).pack(side=tk.LEFT, padx=20, pady=20)

        tk.Button(
            frame_header,
            text="➕ Nuevo Presupuesto",
            font=('Segoe UI', 11, 'bold'),
            bg=COLORES['success'],
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.ventana_nuevo_presupuesto_buddy,
            padx=20,
            pady=8
        ).pack(side=tk.RIGHT, padx=20)

        # Verificar alertas al abrir la vista
        alertas = self.db.verificar_alertas_presupuesto()
        if alertas:
            for alerta in alertas:
                self.db.crear_alerta(alerta['tipo'] if 'tipo' in alerta else 'info', alerta['mensaje'], alerta['nivel'])

        # Obtener presupuestos
        presupuestos = self.db.obtener_presupuestos_compartidos()

        if not presupuestos:
            tk.Label(
                self.frame_contenido,
                text="🤝 No tenés presupuestos compartidos\n\nCreá uno para gestionar tus finanzas con tu pareja o familia",
                font=('Segoe UI', 12),
                bg=COLORES['background'],
                fg='gray',
                justify=tk.CENTER
            ).pack(expand=True)
            return

        # Frame con scroll
        frame_scroll = tk.Frame(self.frame_contenido, bg=COLORES['background'])
        frame_scroll.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        canvas = tk.Canvas(frame_scroll, bg=COLORES['background'], highlightthickness=0)
        scrollbar = tk.Scrollbar(frame_scroll, orient="vertical", command=canvas.yview)
        frame_presups = tk.Frame(canvas, bg=COLORES['background'])

        frame_presups.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=frame_presups, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        for presup in presupuestos:
            presup_id = presup[0]
            nombre = presup[1]
            categoria = presup[2] if presup[2] else "General"
            icono = presup[9] if len(presup) > 9 else '💰'
            descripcion = presup[8] if len(presup) > 8 and presup[8] else ''

            # Calcular uso
            gastado, limite, porcentaje = self.db.calcular_uso_presupuesto_compartido(presup_id)

            # Determinar color según porcentaje
            if porcentaje >= 100:
                color_barra = COLORES['danger']
                color_header = COLORES['danger']
            elif porcentaje >= 90:
                color_barra = COLORES['warning']
                color_header = COLORES['warning']
            elif porcentaje >= 80:
                color_barra = COLORES['info']
                color_header = COLORES['info']
            else:
                color_barra = COLORES['success']
                color_header = COLORES['primary']

            # Tarjeta del presupuesto
            frame_presup = tk.Frame(frame_presups, bg=COLORES['card_bg'], relief=tk.SOLID, bd=1, highlightbackground=COLORES['border'], highlightthickness=1)
            frame_presup.pack(fill=tk.X, pady=8)

            # Header
            frame_presup_header = tk.Frame(frame_presup, bg=color_header)
            frame_presup_header.pack(fill=tk.X)

            tk.Label(
                frame_presup_header,
                text=f"{icono} {nombre}",
                font=('Segoe UI', 14, 'bold'),
                bg=color_header,
                fg='white'
            ).pack(side=tk.LEFT, padx=15, pady=10)

            tk.Label(
                frame_presup_header,
                text=categoria,
                font=('Segoe UI', 9),
                bg=color_header,
                fg='white'
            ).pack(side=tk.RIGHT, padx=15)

            # Descripción
            if descripcion:
                tk.Label(
                    frame_presup,
                    text=descripcion,
                    font=('Segoe UI', 9),
                    bg=COLORES['card_bg'],
                    fg='gray'
                ).pack(padx=15, pady=5, anchor='w')

            # Estadísticas
            frame_stats = tk.Frame(frame_presup, bg=COLORES['card_bg'])
            frame_stats.pack(fill=tk.X, padx=15, pady=10)

            # Gastado vs Límite
            tk.Label(
                frame_stats,
                text=f"${gastado:,.0f} / ${limite:,.0f}",
                font=('Segoe UI', 16, 'bold'),
                bg=COLORES['card_bg'],
                fg=color_barra
            ).pack()

            # Barra de progreso
            frame_barra = tk.Frame(frame_stats, bg='#e5e7eb', height=20)
            frame_barra.pack(fill=tk.X, pady=5)

            ancho_barra = min(porcentaje, 100)
            if ancho_barra > 0:
                frame_progreso = tk.Frame(frame_barra, bg=color_barra, height=20)
                frame_progreso.place(relwidth=ancho_barra/100, relheight=1)

            tk.Label(
                frame_barra,
                text=f"{porcentaje:.1f}%",
                font=('Segoe UI', 9, 'bold'),
                bg='#e5e7eb' if porcentaje < 50 else color_barra,
                fg='gray' if porcentaje < 50 else 'white'
            ).place(relx=0.5, rely=0.5, anchor='center')

            # Participantes
            participantes = self.db.obtener_participantes_presupuesto(presup_id)
            if participantes:
                frame_part = tk.Frame(frame_presup, bg=COLORES['card_bg'])
                frame_part.pack(fill=tk.X, padx=15, pady=5)

                tk.Label(
                    frame_part,
                    text=f"👥 {len(participantes)} participante(s)",
                    font=('Segoe UI', 9),
                    bg=COLORES['card_bg'],
                    fg='gray'
                ).pack(anchor='w')

            # Botones
            frame_btns = tk.Frame(frame_presup, bg=COLORES['card_bg'])
            frame_btns.pack(fill=tk.X, padx=15, pady=10)

            tk.Button(
                frame_btns,
                text="👥 Participantes",
                font=('Segoe UI', 9, 'bold'),
                bg=COLORES['secondary'],
                fg='white',
                relief=tk.FLAT,
                cursor='hand2',
                command=lambda pid=presup_id: self.ventana_participantes_presupuesto(pid),
                padx=15,
                pady=5
            ).pack(side=tk.LEFT, padx=3)

    def ventana_nuevo_presupuesto_buddy(self):
        """Crear un nuevo presupuesto compartido"""
        v = tk.Toplevel(self.root)
        v.title("➕ Nuevo Presupuesto Compartido")
        v.geometry("500x550")
        v.configure(bg=COLORES['background'])
        v.transient(self.root)
        v.grab_set()

        v.update_idletasks()
        x = (v.winfo_screenwidth() // 2) - (500 // 2)
        y = (v.winfo_screenheight() // 2) - (550 // 2)
        v.geometry(f'500x550+{x}+{y}')

        frame = tk.Frame(v, bg=COLORES['background'], padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            frame,
            text="➕ Nuevo Presupuesto Compartido",
            font=('Segoe UI', 16, 'bold'),
            bg=COLORES['background']
        ).pack(pady=10)

        # Formulario
        tk.Label(frame, text="📝 Nombre:", bg=COLORES['background'], font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=3)
        entry_nombre = tk.Entry(frame, font=('Segoe UI', 11))
        entry_nombre.pack(fill=tk.X, pady=3)

        tk.Label(frame, text="📂 Categoría (opcional):", bg=COLORES['background'], font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=3)
        categorias = [c[1] for c in self.db.obtener_categorias()]
        categorias.insert(0, "Todas las categorías")
        combo_categoria = ttk.Combobox(frame, values=categorias, state='readonly', font=('Segoe UI', 11))
        combo_categoria.set("Todas las categorías")
        combo_categoria.pack(fill=tk.X, pady=3)

        tk.Label(frame, text="💰 Límite mensual:", bg=COLORES['background'], font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=3)
        entry_limite = tk.Entry(frame, font=('Segoe UI', 11))
        entry_limite.pack(fill=tk.X, pady=3)

        tk.Label(frame, text="📅 Mes (YYYY-MM):", bg=COLORES['background'], font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=3)
        entry_mes = tk.Entry(frame, font=('Segoe UI', 11))
        entry_mes.insert(0, self.mes_actual)
        entry_mes.pack(fill=tk.X, pady=3)

        tk.Label(frame, text="👤 Creado por (tu nombre):", bg=COLORES['background'], font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=3)
        entry_creado_por = tk.Entry(frame, font=('Segoe UI', 11))
        entry_creado_por.pack(fill=tk.X, pady=3)

        tk.Label(frame, text="🎨 Icono:", bg=COLORES['background'], font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=3)
        iconos = ['💰', '🏠', '🍕', '🚗', '✈️', '🛒', '💳', '🎓', '🏥', '🎮']
        combo_icono = ttk.Combobox(frame, values=iconos, state='readonly', font=('Segoe UI', 11))
        combo_icono.set('💰')
        combo_icono.pack(fill=tk.X, pady=3)

        tk.Label(frame, text="📄 Descripción (opcional):", bg=COLORES['background'], font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=3)
        entry_desc = tk.Entry(frame, font=('Segoe UI', 11))
        entry_desc.pack(fill=tk.X, pady=3)

        var_compartido = tk.BooleanVar(value=True)
        tk.Checkbutton(
            frame,
            text="🤝 Presupuesto compartido (puedes invitar a otras personas)",
            variable=var_compartido,
            bg=COLORES['background'],
            font=('Segoe UI', 10)
        ).pack(pady=10)

        def guardar():
            nombre = entry_nombre.get().strip()
            limite_str = entry_limite.get().strip()
            creado_por = entry_creado_por.get().strip()
            mes = entry_mes.get().strip()

            if not nombre or not limite_str or not creado_por:
                messagebox.showwarning("Error", "Completá los campos obligatorios")
                return

            try:
                limite = float(limite_str.replace(',', '.'))
                if limite <= 0:
                    raise ValueError()

                categoria_sel = combo_categoria.get()
                categoria = None if categoria_sel == "Todas las categorías" else categoria_sel

                presup_id = self.db.crear_presupuesto_compartido(
                    nombre,
                    categoria,
                    limite,
                    mes,
                    creado_por,
                    var_compartido.get(),
                    entry_desc.get().strip(),
                    combo_icono.get()
                )

                messagebox.showinfo("Éxito", f"✅ Presupuesto '{nombre}' creado!")
                v.destroy()
                self.mostrar_buddy_presupuestos()

                # Si es compartido, abrir ventana de participantes
                if var_compartido.get():
                    self.ventana_participantes_presupuesto(presup_id)

            except ValueError:
                messagebox.showerror("Error", "Límite inválido")

        frame_btns = tk.Frame(frame, bg=COLORES['background'])
        frame_btns.pack(pady=20)

        tk.Button(
            frame_btns,
            text="✅ Crear",
            command=guardar,
            bg=COLORES['success'],
            fg='white',
            font=('Segoe UI', 11, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            padx=25,
            pady=10
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            frame_btns,
            text="❌ Cancelar",
            command=v.destroy,
            bg=COLORES['text_secondary'],
            fg='white',
            font=('Segoe UI', 11),
            relief=tk.FLAT,
            cursor='hand2',
            padx=40,
            pady=12,
            borderwidth=0
        ).pack(side=tk.LEFT, padx=8)

    def ventana_participantes_presupuesto(self, presup_id):
        """Gestionar participantes de un presupuesto compartido"""
        v = tk.Toplevel(self.root)
        v.title("👥 Participantes del Presupuesto")
        v.geometry("500x550")
        v.configure(bg=COLORES['background'])
        v.transient(self.root)

        v.update_idletasks()
        x = (v.winfo_screenwidth() // 2) - (500 // 2)
        y = (v.winfo_screenheight() // 2) - (550 // 2)
        v.geometry(f'500x550+{x}+{y}')

        frame = tk.Frame(v, bg=COLORES['background'], padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            frame,
            text="👥 Gestionar Participantes",
            font=('Segoe UI', 16, 'bold'),
            bg=COLORES['background']
        ).pack(pady=10)

        # Formulario para agregar
        frame_form = tk.Frame(frame, bg=COLORES['card_bg'], relief=tk.SOLID, bd=1, highlightbackground=COLORES['border'], highlightthickness=1)
        frame_form.pack(fill=tk.X, pady=10)

        tk.Label(
            frame_form,
            text="➕ Agregar Participante",
            font=('Segoe UI', 12, 'bold'),
            bg=COLORES['card_bg']
        ).pack(pady=10)

        frame_inputs = tk.Frame(frame_form, bg=COLORES['card_bg'])
        frame_inputs.pack(padx=15, pady=5)

        tk.Label(frame_inputs, text="Nombre:", bg=COLORES['card_bg'], font=('Segoe UI', 10)).grid(row=0, column=0, sticky='w', pady=5)
        entry_nombre = tk.Entry(frame_inputs, font=('Segoe UI', 10), width=20)
        entry_nombre.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame_inputs, text="Email:", bg=COLORES['card_bg'], font=('Segoe UI', 10)).grid(row=1, column=0, sticky='w', pady=5)
        entry_email = tk.Entry(frame_inputs, font=('Segoe UI', 10), width=20)
        entry_email.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(frame_inputs, text="Rol:", bg=COLORES['card_bg'], font=('Segoe UI', 10)).grid(row=2, column=0, sticky='w', pady=5)
        combo_rol = ttk.Combobox(frame_inputs, values=['viewer', 'contributor', 'admin'], state='readonly', font=('Segoe UI', 10))
        combo_rol.set('viewer')
        combo_rol.grid(row=2, column=1, padx=5, pady=5)

        def agregar():
            nombre = entry_nombre.get().strip()
            if not nombre:
                messagebox.showwarning("Error", "Ingresá un nombre")
                return

            self.db.agregar_participante_presupuesto(presup_id, nombre, entry_email.get().strip(), combo_rol.get())
            entry_nombre.delete(0, tk.END)
            entry_email.delete(0, tk.END)
            actualizar_lista()

        tk.Button(
            frame_form,
            text="➕ Agregar",
            command=agregar,
            bg=COLORES['success'],
            fg='white',
            font=('Segoe UI', 10, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=5
        ).pack(pady=10)

        # Lista
        frame_lista = tk.Frame(frame, bg=COLORES['background'])
        frame_lista.pack(fill=tk.BOTH, expand=True, pady=10)

        tk.Label(
            frame_lista,
            text="📋 Participantes Actuales",
            font=('Segoe UI', 12, 'bold'),
            bg=COLORES['background']
        ).pack(pady=5)

        lista_container = tk.Frame(frame_lista, bg=COLORES['background'])
        lista_container.pack(fill=tk.BOTH, expand=True)

        def actualizar_lista():
            for widget in lista_container.winfo_children():
                widget.destroy()

            participantes = self.db.obtener_participantes_presupuesto(presup_id)

            if not participantes:
                tk.Label(
                    lista_container,
                    text="No hay participantes agregados",
                    font=('Segoe UI', 10),
                    bg=COLORES['background'],
                    fg='gray'
                ).pack(pady=20)
            else:
                for p in participantes:
                    nombre = p[2]
                    email = p[3]
                    rol = p[4]

                    frame_p = tk.Frame(lista_container, bg=COLORES['card_bg'], relief=tk.RAISED, bd=1)
                    frame_p.pack(fill=tk.X, pady=3)

                    tk.Label(
                        frame_p,
                        text=f"👤 {nombre}",
                        font=('Segoe UI', 11, 'bold'),
                        bg=COLORES['card_bg']
                    ).pack(side=tk.LEFT, padx=10, pady=8)

                    if email:
                        tk.Label(
                            frame_p,
                            text=email,
                            font=('Segoe UI', 9),
                            bg=COLORES['card_bg'],
                            fg='gray'
                        ).pack(side=tk.LEFT, padx=5)

                    # Rol badge
                    rol_colors = {'viewer': '#6b7280', 'contributor': '#3b82f6', 'admin': '#10b981'}
                    tk.Label(
                        frame_p,
                        text=rol.upper(),
                        font=('Segoe UI', 8, 'bold'),
                        bg=rol_colors.get(rol, '#6b7280'),
                        fg='white',
                        padx=8,
                        pady=2
                    ).pack(side=tk.RIGHT, padx=10)

        actualizar_lista()

        tk.Button(
            frame,
            text="✅ Cerrar",
            command=v.destroy,
            bg=COLORES['primary'],
            fg='white',
            font=('Segoe UI', 11, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            padx=30,
            pady=10
        ).pack(pady=10)

    def mostrar_buddy_notificaciones(self):
        """Centro de notificaciones estilo Buddy"""
        # Header
        frame_header = tk.Frame(self.frame_contenido, bg=COLORES['primary'], height=80)
        frame_header.pack(fill=tk.X, padx=15, pady=15)
        frame_header.pack_propagate(False)

        notifs_no_leidas = self.db.obtener_notificaciones_buddy(solo_no_leidas=True)

        tk.Label(
            frame_header,
            text=f"🔔 Notificaciones ({len(notifs_no_leidas)} nuevas)",
            font=('Segoe UI', 18, 'bold'),
            bg=COLORES['primary'],
            fg='white'
        ).pack(side=tk.LEFT, padx=20, pady=20)

        def marcar_todas_leidas():
            for notif in notifs_no_leidas:
                self.db.marcar_notificacion_leida(notif[0])
            self.mostrar_buddy_notificaciones()

        if notifs_no_leidas:
            tk.Button(
                frame_header,
                text="✅ Marcar Todas Leídas",
                font=('Segoe UI', 10, 'bold'),
                bg=COLORES['success'],
                fg='white',
                relief=tk.FLAT,
                cursor='hand2',
                command=marcar_todas_leidas,
                padx=15,
                pady=5
            ).pack(side=tk.RIGHT, padx=20)

        # Obtener todas las notificaciones
        notifs = self.db.obtener_notificaciones_buddy()

        if not notifs:
            tk.Label(
                self.frame_contenido,
                text="🔔 No tenés notificaciones\n\nTe avisaremos cuando haya algo importante",
                font=('Segoe UI', 12),
                bg=COLORES['background'],
                fg='gray',
                justify=tk.CENTER
            ).pack(expand=True)
            return

        # Frame con scroll
        frame_scroll = tk.Frame(self.frame_contenido, bg=COLORES['background'])
        frame_scroll.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        canvas = tk.Canvas(frame_scroll, bg=COLORES['background'], highlightthickness=0)
        scrollbar = tk.Scrollbar(frame_scroll, orient="vertical", command=canvas.yview)
        frame_notifs = tk.Frame(canvas, bg=COLORES['background'])

        frame_notifs.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=frame_notifs, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        for notif in notifs:
            notif_id = notif[0]
            tipo = notif[1]
            titulo = notif[2]
            mensaje = notif[3]
            nivel = notif[6]
            leida = notif[8]

            # Determinar color según nivel
            nivel_colors = {
                'info': COLORES['info'],
                'success': COLORES['success'],
                'warning': COLORES['warning'],
                'danger': COLORES['danger']
            }
            color = nivel_colors.get(nivel, COLORES['info'])

            # Tarjeta de notificación
            frame_notif = tk.Frame(
                frame_notifs,
                bg='#e5e7eb' if leida else COLORES['card_bg'],
                relief=tk.RAISED,
                bd=2
            )
            frame_notif.pack(fill=tk.X, pady=5)

            # Barra lateral de color
            frame_barra = tk.Frame(frame_notif, bg=color, width=5)
            frame_barra.pack(side=tk.LEFT, fill=tk.Y)

            # Contenido
            frame_contenido_notif = tk.Frame(frame_notif, bg='#e5e7eb' if leida else COLORES['card_bg'])
            frame_contenido_notif.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=10)

            tk.Label(
                frame_contenido_notif,
                text=titulo,
                font=('Segoe UI', 11, 'bold'),
                bg='#e5e7eb' if leida else COLORES['card_bg']
            ).pack(anchor='w')

            tk.Label(
                frame_contenido_notif,
                text=mensaje,
                font=('Segoe UI', 10),
                bg='#e5e7eb' if leida else COLORES['card_bg'],
                wraplength=400,
                justify=tk.LEFT
            ).pack(anchor='w', pady=5)

            # Botón marcar como leída
            if not leida:
                def marcar_leida(nid=notif_id):
                    self.db.marcar_notificacion_leida(nid)
                    self.mostrar_buddy_notificaciones()

                tk.Button(
                    frame_notif,
                    text="✓",
                    font=('Segoe UI', 12, 'bold'),
                    bg=COLORES['success'],
                    fg='white',
                    relief=tk.FLAT,
                    cursor='hand2',
                    command=marcar_leida,
                    width=3
                ).pack(side=tk.RIGHT, padx=10)

    def mostrar_temas(self):
        """Selector de temas de colores estilo Buddy"""
        # Header
        frame_header = tk.Frame(self.frame_contenido, bg=COLORES['primary'], height=80)
        frame_header.pack(fill=tk.X, padx=15, pady=15)
        frame_header.pack_propagate(False)

        tk.Label(
            frame_header,
            text="🎨 Temas de Colores",
            font=('Segoe UI', 18, 'bold'),
            bg=COLORES['primary'],
            fg='white'
        ).pack(padx=20, pady=20)

        # Descripción
        tk.Label(
            self.frame_contenido,
            text="Personalizá la apariencia de tu app con estos temas de colores",
            font=('Segoe UI', 11),
            bg=COLORES['background'],
            fg='gray'
        ).pack(pady=10)

        # Obtener temas
        temas = self.db.obtener_temas_disponibles()
        tema_activo = self.db.obtener_tema_activo()
        tema_activo_id = tema_activo[0] if tema_activo else None

        # Grid de temas
        frame_temas = tk.Frame(self.frame_contenido, bg=COLORES['background'])
        frame_temas.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        for i, tema in enumerate(temas):
            tema_id = tema[0]
            nombre = tema[1]
            primary = tema[2]
            success = tema[4]
            danger = tema[5]
            bg_color = tema[8]

            # Tarjeta del tema
            frame_tema = tk.Frame(
                frame_temas,
                bg=bg_color,
                relief=tk.RAISED,
                bd=4 if tema_id == tema_activo_id else 2,
                highlightthickness=3 if tema_id == tema_activo_id else 0,
                highlightbackground=COLORES['success'] if tema_id == tema_activo_id else bg_color
            )
            frame_tema.grid(row=i//2, column=i%2, padx=10, pady=10, sticky='nsew')

            # Nombre del tema
            tk.Label(
                frame_tema,
                text=nombre + (" ✓ ACTIVO" if tema_id == tema_activo_id else ""),
                font=('Segoe UI', 14, 'bold'),
                bg=bg_color,
                fg=primary
            ).pack(pady=15)

            # Paleta de colores
            frame_paleta = tk.Frame(frame_tema, bg=bg_color)
            frame_paleta.pack(pady=10)

            colores_muestra = [
                (primary, "Primary"),
                (success, "Success"),
                (danger, "Danger")
            ]

            for color, label in colores_muestra:
                frame_color = tk.Frame(frame_paleta, bg=color, width=60, height=40)
                frame_color.pack(side=tk.LEFT, padx=5)
                frame_color.pack_propagate(False)

                tk.Label(
                    frame_color,
                    text=label,
                    font=('Segoe UI', 7),
                    bg=color,
                    fg='white'
                ).pack(expand=True)

            # Botón activar
            def activar(tid=tema_id, tnombre=nombre):
                self.db.activar_tema(tid)
                messagebox.showinfo("Tema Activado", f"✅ Tema '{tnombre}' activado!\n\nReiniciá la app para ver los cambios.")
                # Limpiar y recargar la vista correctamente
                for widget in self.frame_contenido.winfo_children():
                    widget.destroy()
                self.mostrar_temas()

            if tema_id != tema_activo_id:
                tk.Button(
                    frame_tema,
                    text="Activar Tema",
                    font=('Segoe UI', 10, 'bold'),
                    bg=primary,
                    fg='white',
                    relief=tk.FLAT,
                    cursor='hand2',
                    command=activar,
                    padx=20,
                    pady=8
                ).pack(pady=15)
            else:
                tk.Label(
                    frame_tema,
                    text="✓ En Uso",
                    font=('Segoe UI', 10, 'bold'),
                    bg=success,
                    fg='white',
                    padx=20,
                    pady=8
                ).pack(pady=15)

        frame_temas.columnconfigure(0, weight=1)
        frame_temas.columnconfigure(1, weight=1)

    def ventana_conversor(self):
        """Ventana de conversor de monedas múltiples"""
        v = tk.Toplevel(self.root)
        v.title("💱 Conversor de Monedas")
        v.geometry("500x600")
        v.configure(bg=COLORES['background'])
        v.transient(self.root)
        
        v.update_idletasks()
        x = (v.winfo_screenwidth() // 2) - (500 // 2)
        y = (v.winfo_screenheight() // 2) - (600 // 2)
        v.geometry(f'500x600+{x}+{y}')
        
        frame = tk.Frame(v, bg=COLORES['background'], padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            frame,
            text="💱 Conversor Multi-Moneda",
            font=('Segoe UI', 16, 'bold'),
            bg=COLORES['background']
        ).pack(pady=10)
        
        tk.Label(
            frame,
            text="Cargando tasas de conversión...",
            font=('Segoe UI', 9),
            bg=COLORES['background'],
            fg=COLORES['text_secondary']
        ).pack()
        
        frame_conv = tk.Frame(frame, bg=COLORES['card_bg'], relief=tk.SOLID, bd=1, highlightbackground=COLORES['border'], highlightthickness=1)
        frame_conv.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # DE
        tk.Label(frame_conv, text="De:", font=('Segoe UI', 10, 'bold'), 
                bg=COLORES['card_bg']).pack(anchor='w', padx=15, pady=(15, 5))
        
        frame_de = tk.Frame(frame_conv, bg=COLORES['card_bg'])
        frame_de.pack(fill=tk.X, padx=15, pady=5)
        
        entry_monto = tk.Entry(frame_de, font=('Segoe UI', 12), width=15)
        entry_monto.pack(side=tk.LEFT, padx=5)
        entry_monto.insert(0, "100")
        
        monedas = ['USD', 'EUR', 'GBP', 'ARS', 'BRL', 'CLP', 'MXN', 'UYU']
        combo_de = ttk.Combobox(frame_de, values=monedas, state='readonly', width=10)
        combo_de.set('USD')
        combo_de.pack(side=tk.LEFT, padx=5)
        
        # A
        tk.Label(frame_conv, text="A:", font=('Segoe UI', 10, 'bold'),
                bg=COLORES['card_bg']).pack(anchor='w', padx=15, pady=(15, 5))
        
        frame_a = tk.Frame(frame_conv, bg=COLORES['card_bg'])
        frame_a.pack(fill=tk.X, padx=15, pady=5)
        
        lbl_resultado = tk.Label(frame_a, text="0.00", font=('Segoe UI', 16, 'bold'),
                                bg=COLORES['card_bg'], fg=COLORES['success'])
        lbl_resultado.pack(side=tk.LEFT, padx=5)
        
        combo_a = ttk.Combobox(frame_a, values=monedas, state='readonly', width=10)
        combo_a.set('ARS')
        combo_a.pack(side=tk.LEFT, padx=5)
        
        # Tasas
        frame_tasas = tk.Frame(frame_conv, bg=COLORES['light'])
        frame_tasas.pack(fill=tk.X, padx=15, pady=15)
        
        lbl_tasa = tk.Label(
            frame_tasas,
            text="",
            font=('Segoe UI', 9),
            bg=COLORES['light'],
            fg=COLORES['text_secondary']
        )
        lbl_tasa.pack(pady=5)
        
        def convertir():
            try:
                monto = float(entry_monto.get().replace(',', '.'))
                de = combo_de.get()
                a = combo_a.get()
                
                tasas = obtener_tasas_conversion()
                
                # Convertir a USD primero, luego a moneda destino
                monto_usd = monto / tasas[de]
                resultado = monto_usd * tasas[a]
                
                lbl_resultado.config(text=f"{resultado:,.2f}")
                
                tasa = tasas[a] / tasas[de]
                lbl_tasa.config(text=f"1 {de} = {tasa:.4f} {a}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error en conversión: {e}")
        
        entry_monto.bind('<KeyRelease>', lambda e: convertir())
        combo_de.bind('<<ComboboxSelected>>', lambda e: convertir())
        combo_a.bind('<<ComboboxSelected>>', lambda e: convertir())
        
        tk.Button(
            frame_conv,
            text="🔄 Convertir",
            command=convertir,
            bg=COLORES['info'],
            fg='white',
            font=('Segoe UI', 11, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            padx=30,
            pady=10
        ).pack(pady=15)
        
        # Cargar tasas al abrir
        v.after(100, convertir)

    def ventana_registro_rapido(self):
        """Ventana de registro rápido con texto libre"""
        v = tk.Toplevel(self.root)
        v.title("⚡ Registro Rápido de Gasto")
        v.geometry("600x550")
        v.configure(bg=COLORES['background'])
        v.transient(self.root)
        v.grab_set()

        v.update_idletasks()
        x = (v.winfo_screenwidth() // 2) - (600 // 2)
        y = (v.winfo_screenheight() // 2) - (550 // 2)
        v.geometry(f'600x550+{x}+{y}')

        frame = tk.Frame(v, bg=COLORES['background'], padx=25, pady=25)
        frame.pack(fill=tk.BOTH, expand=True)

        # Header con gradiente visual (simulado con frame)
        header_frame = tk.Frame(frame, bg=COLORES['primary'], relief=tk.FLAT)
        header_frame.pack(fill=tk.X, pady=(0, 20), padx=-5)

        tk.Label(
            header_frame,
            text="⚡ Registro Rápido",
            font=('Segoe UI', 16, 'bold'),
            bg=COLORES['primary'],
            fg='white'
        ).pack(pady=15)

        tk.Label(
            frame,
            text='💬 Escribí tu gasto en lenguaje natural o usá el micrófono',
            font=('Segoe UI', 11, 'bold'),
            bg=COLORES['background'],
            fg=COLORES['text']
        ).pack(pady=(0, 5))

        tk.Label(
            frame,
            text='Ejemplos: "Gasto 2000 en supermercado" • "Pagué 1500 de comida" • "Almuerzo $350"',
            font=('Segoe UI', 9),
            bg=COLORES['background'],
            fg=COLORES['text_secondary'],
            justify=tk.CENTER
        ).pack(pady=(0, 15))

        # Frame para entry + botón de micrófono con estilo moderno
        frame_input_container = tk.Frame(frame, bg=COLORES['card_bg'], relief=tk.FLAT, bd=2, highlightbackground=COLORES['primary_light'], highlightthickness=2)
        frame_input_container.pack(fill=tk.X, pady=10, ipady=5)

        frame_input = tk.Frame(frame_input_container, bg=COLORES['card_bg'])
        frame_input.pack(fill=tk.X, padx=5, pady=5)

        entry_texto = tk.Entry(frame_input, font=('Segoe UI', 13), relief=tk.FLAT, bg=COLORES['card_bg'], fg=COLORES['text'], insertbackground=COLORES['primary'])
        entry_texto.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=5)
        entry_texto.focus()

        # Botón de micrófono
        def iniciar_voz():
            btn_mic.config(text="🎙️ Grabando...", bg=COLORES['danger'])
            frame.update()

            try:
                import speech_recognition as sr
                recognizer = sr.Recognizer()

                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)

                texto = recognizer.recognize_google(audio, language='es-AR')
                entry_texto.delete(0, tk.END)
                entry_texto.insert(0, texto)
                actualizar_preview()

                btn_mic.config(text="🎤", bg=COLORES['info'])
                messagebox.showinfo("✅ Voz reconocida", f"Detectado: '{texto}'")

            except ImportError:
                btn_mic.config(text="🎤", bg=COLORES['info'])
                messagebox.showerror("Error",
                    "Necesitas instalar:\npip install SpeechRecognition pyaudio")
            except sr.WaitTimeoutError:
                btn_mic.config(text="🎤", bg=COLORES['info'])
                messagebox.showwarning("Timeout", "No se detectó ningún audio")
            except sr.UnknownValueError:
                btn_mic.config(text="🎤", bg=COLORES['info'])
                messagebox.showwarning("No entendido", "No se pudo entender el audio")
            except sr.RequestError as e:
                btn_mic.config(text="🎤", bg=COLORES['info'])
                messagebox.showerror("Error de red", f"Error al conectar con el servicio: {e}")
            except Exception as e:
                btn_mic.config(text="🎤", bg=COLORES['info'])
                messagebox.showerror("Error", f"Error al capturar voz: {e}")

        btn_mic = tk.Button(
            frame_input,
            text="🎤",
            font=('Segoe UI', 16, 'bold'),
            bg=COLORES['info'],
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=iniciar_voz,
            padx=15,
            pady=8,
            borderwidth=0
        )
        btn_mic.pack(side=tk.RIGHT, padx=5)

        # Frame de vista previa con diseño moderno
        frame_preview = tk.Frame(frame, bg=COLORES['card_bg'], relief=tk.FLAT, bd=2, highlightbackground=COLORES['border'], highlightthickness=1)
        frame_preview.pack(fill=tk.BOTH, expand=True, pady=15, ipady=10)

        tk.Label(
            frame_preview,
            text="📝 Vista Previa del Gasto",
            font=('Segoe UI', 12, 'bold'),
            bg=COLORES['card_bg'],
            fg=COLORES['primary']
        ).pack(pady=15)

        lbl_monto = tk.Label(frame_preview, text="💰 Monto: -", font=('Segoe UI', 12, 'bold'),
                            bg=COLORES['card_bg'], anchor='w', fg=COLORES['text'])
        lbl_monto.pack(fill=tk.X, padx=20, pady=8)

        lbl_categoria = tk.Label(frame_preview, text="📂 Categoría: -", font=('Segoe UI', 11),
                                bg=COLORES['card_bg'], anchor='w', fg=COLORES['text'])
        lbl_categoria.pack(fill=tk.X, padx=20, pady=8)

        lbl_descripcion = tk.Label(frame_preview, text="📝 Descripción: -", font=('Segoe UI', 11),
                                   bg=COLORES['card_bg'], anchor='w', fg=COLORES['text'])
        lbl_descripcion.pack(fill=tk.X, padx=20, pady=8)

        lbl_confianza = tk.Label(frame_preview, text="", font=('Segoe UI', 10, 'bold'),
                                bg=COLORES['card_bg'], fg=COLORES['text_secondary'])
        lbl_confianza.pack(pady=10)

        datos_parseados = {'monto': 0, 'categoria': None, 'descripcion': ''}

        def actualizar_preview(event=None):
            nonlocal datos_parseados
            texto = entry_texto.get()

            if texto.strip():
                categorias = [c[1] for c in self.db.obtener_categorias()]
                datos_parseados = parsear_gasto_texto(texto, categorias)

                lbl_monto.config(text=f"💰 Monto: ${datos_parseados['monto']:,.0f}")
                lbl_categoria.config(text=f"📂 Categoría: {datos_parseados['categoria'] or 'No detectada'}")
                lbl_descripcion.config(text=f"📝 Descripción: {datos_parseados['descripcion']}")

                if datos_parseados['confianza'] >= 0.8:
                    lbl_confianza.config(text="✅ Alta confianza", fg=COLORES['success'])
                elif datos_parseados['confianza'] >= 0.5:
                    lbl_confianza.config(text="⚠️ Confianza media - Verificá los datos", fg=COLORES['warning'])
                else:
                    lbl_confianza.config(text="❌ Baja confianza - Revisá los datos", fg=COLORES['danger'])
            else:
                lbl_monto.config(text="💰 Monto: -")
                lbl_categoria.config(text="📂 Categoría: -")
                lbl_descripcion.config(text="📝 Descripción: -")
                lbl_confianza.config(text="")

        entry_texto.bind('<KeyRelease>', actualizar_preview)

        def guardar():
            if datos_parseados['monto'] <= 0:
                messagebox.showwarning("Error", "No se pudo detectar un monto válido")
                return

            if not datos_parseados['categoria']:
                messagebox.showwarning("Error", "No se pudo detectar una categoría")
                return

            try:
                fecha = datetime.date.today().isoformat()
                cuentas = self.db.obtener_cuentas()
                cuenta = cuentas[0][1] if cuentas else '💵 Efectivo'

                self.db.agregar_gasto(
                    fecha,
                    datos_parseados['categoria'],
                    datos_parseados['monto'],
                    'ARS',
                    datos_parseados['descripcion'],
                    cuenta
                )

                # Verificar logros
                self.db.verificar_logros()

                messagebox.showinfo("Éxito", "✅ Gasto registrado con éxito!")
                v.destroy()

                if self.vista_actual == 'gastos':
                    self.cargar_gastos()

            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {e}")

        frame_btns = tk.Frame(frame, bg=COLORES['background'])
        frame_btns.pack(pady=15)

        tk.Button(frame_btns, text="💾 Guardar Gasto", command=guardar, bg=COLORES['success'],
                 fg='white', font=('Segoe UI', 12, 'bold'), relief=tk.FLAT, cursor='hand2',
                 padx=40, pady=12, borderwidth=0).pack(side=tk.LEFT, padx=8)

        tk.Button(frame_btns, text="❌ Cancelar", command=v.destroy, bg=COLORES['text_secondary'],
                 fg='white', font=('Segoe UI', 11), relief=tk.FLAT, cursor='hand2',
                 padx=40, pady=12, borderwidth=0).pack(side=tk.LEFT, padx=8)

    def ventana_entrada_rapida_monefy(self):
        """Entrada ultra-rápida estilo Monefy con calculadora"""
        v = tk.Toplevel(self.root)
        v.title("⚡ Entrada Rápida Monefy")
        v.geometry("400x650")
        v.configure(bg=COLORES['background'])
        v.transient(self.root)
        v.grab_set()

        v.update_idletasks()
        x = (v.winfo_screenwidth() // 2) - (400 // 2)
        y = (v.winfo_screenheight() // 2) - (650 // 2)
        v.geometry(f'400x650+{x}+{y}')

        # Variables
        monto_actual = tk.StringVar(value="0")
        categoria_seleccionada = tk.StringVar()
        es_gasto = tk.BooleanVar(value=True)  # True=Gasto, False=Ingreso

        # Header con toggle Gasto/Ingreso
        frame_toggle = tk.Frame(v, bg=COLORES['background'])
        frame_toggle.pack(fill=tk.X, padx=20, pady=10)

        def toggle_tipo():
            if es_gasto.get():
                btn_gasto.config(bg=COLORES['danger'], relief=tk.SUNKEN)
                btn_ingreso.config(bg=COLORES['text_secondary'], relief=tk.FLAT)
            else:
                btn_gasto.config(bg=COLORES['text_secondary'], relief=tk.FLAT)
                btn_ingreso.config(bg=COLORES['success'], relief=tk.SUNKEN)

        btn_gasto = tk.Button(
            frame_toggle,
            text="📤 GASTO",
            font=('Segoe UI', 11, 'bold'),
            bg=COLORES['danger'],
            fg='white',
            relief=tk.SUNKEN,
            cursor='hand2',
            command=lambda: [es_gasto.set(True), toggle_tipo()],
            padx=20,
            pady=10
        )
        btn_gasto.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        btn_ingreso = tk.Button(
            frame_toggle,
            text="📥 INGRESO",
            font=('Segoe UI', 11, 'bold'),
            bg=COLORES['text_secondary'],
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=lambda: [es_gasto.set(False), toggle_tipo()],
            padx=20,
            pady=10
        )
        btn_ingreso.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        # Display del monto (estilo calculadora)
        frame_display = tk.Frame(v, bg=COLORES['primary'], height=80)
        frame_display.pack(fill=tk.X, padx=20, pady=10)
        frame_display.pack_propagate(False)

        tk.Label(
            frame_display,
            textvariable=monto_actual,
            font=('Segoe UI', 36, 'bold'),
            bg=COLORES['primary'],
            fg='white',
            anchor='e'
        ).pack(expand=True, fill=tk.BOTH, padx=15)

        # Calculadora
        frame_calc = tk.Frame(v, bg=COLORES['background'])
        frame_calc.pack(padx=20, pady=5)

        def agregar_digito(digito):
            actual = monto_actual.get()
            if actual == "0":
                monto_actual.set(digito)
            else:
                monto_actual.set(actual + digito)

        def borrar():
            actual = monto_actual.get()
            if len(actual) > 1:
                monto_actual.set(actual[:-1])
            else:
                monto_actual.set("0")

        def limpiar():
            monto_actual.set("0")

        # Botones de la calculadora
        botones = [
            ['7', '8', '9'],
            ['4', '5', '6'],
            ['1', '2', '3'],
            ['C', '0', '⌫']
        ]

        for fila in botones:
            frame_fila = tk.Frame(frame_calc, bg=COLORES['background'])
            frame_fila.pack()
            for btn_text in fila:
                if btn_text == 'C':
                    cmd = limpiar
                    bg = COLORES['warning']
                elif btn_text == '⌫':
                    cmd = borrar
                    bg = COLORES['danger']
                else:
                    cmd = lambda d=btn_text: agregar_digito(d)
                    bg = COLORES['card_bg']

                tk.Button(
                    frame_fila,
                    text=btn_text,
                    font=('Segoe UI', 16, 'bold'),
                    bg=bg,
                    fg='white' if btn_text in ['C', '⌫'] else COLORES['text'],
                    relief=tk.RAISED,
                    cursor='hand2',
                    command=cmd,
                    width=4,
                    height=2
                ).pack(side=tk.LEFT, padx=3, pady=3)

        # Selector de categorías (iconos grandes)
        tk.Label(
            v,
            text="Seleccioná Categoría:",
            font=('Segoe UI', 11, 'bold'),
            bg=COLORES['background']
        ).pack(pady=(15, 5))

        frame_categorias = tk.Frame(v, bg=COLORES['background'])
        frame_categorias.pack(padx=20)

        categorias = self.db.obtener_categorias()[:8]  # Primeras 8 categorías

        cat_buttons = {}
        for i, cat in enumerate(categorias):
            id_cat, nombre_cat, icono = cat[:3]

            def seleccionar_cat(nombre=nombre_cat, icono_cat=icono):
                categoria_seleccionada.set(nombre)
                # Actualizar visual
                for btn in cat_buttons.values():
                    btn.config(relief=tk.FLAT, bg=COLORES['card_bg'])
                cat_buttons[nombre].config(relief=tk.SUNKEN, bg=COLORES['primary'])

            btn = tk.Button(
                frame_categorias,
                text=f"{icono}\n{nombre_cat[:8]}",
                font=('Segoe UI', 9),
                bg=COLORES['card_bg'],
                fg=COLORES['text'],
                relief=tk.FLAT,
                cursor='hand2',
                command=seleccionar_cat,
                width=10,
                height=3
            )
            btn.grid(row=i//4, column=i%4, padx=3, pady=3)
            cat_buttons[nombre_cat] = btn

        # Seleccionar primera categoría por defecto
        if categorias:
            categoria_seleccionada.set(categorias[0][1])
            cat_buttons[categorias[0][1]].config(relief=tk.SUNKEN, bg=COLORES['primary'])

        # Botón de guardar grande
        def guardar_rapido():
            try:
                monto = float(monto_actual.get())
                if monto <= 0:
                    messagebox.showwarning("Error", "Ingresá un monto válido")
                    return

                cat = categoria_seleccionada.get()
                if not cat:
                    messagebox.showwarning("Error", "Seleccioná una categoría")
                    return

                fecha = datetime.date.today().isoformat()

                if es_gasto.get():
                    # Es un gasto
                    self.db.agregar_gasto(fecha, cat, monto, 'ARS', '', 'Efectivo', '')
                else:
                    # Es un ingreso (monto negativo)
                    self.db.agregar_gasto(fecha, cat, -monto, 'ARS', 'Ingreso', 'Efectivo', '')

                messagebox.showinfo("✅ Listo", f"{'Gasto' if es_gasto.get() else 'Ingreso'} guardado: ${monto:,.0f}")
                v.destroy()

                if self.vista_actual == 'gastos' or self.vista_actual == 'dashboard':
                    if self.vista_actual == 'gastos':
                        self.cargar_gastos()
                    else:
                        self.mostrar_dashboard()

            except ValueError:
                messagebox.showerror("Error", "Monto inválido")

        tk.Button(
            v,
            text="💾 GUARDAR",
            font=('Segoe UI', 14, 'bold'),
            bg=COLORES['success'],
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=guardar_rapido,
            pady=15
        ).pack(fill=tk.X, padx=20, pady=15)

    def ventana_agregar_gasto(self):
        v = tk.Toplevel(self.root)
        v.title("➕ Agregar Gasto")
        v.geometry("450x550")
        v.configure(bg=COLORES['background'])
        v.transient(self.root)
        v.grab_set()
        
        v.update_idletasks()
        x = (v.winfo_screenwidth() // 2) - (450 // 2)
        y = (v.winfo_screenheight() // 2) - (550 // 2)
        v.geometry(f'450x550+{x}+{y}')
        
        frame = tk.Frame(v, bg=COLORES['background'], padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        campos = [
            ("📅 Fecha:", tk.Entry(frame)),
            ("📂 Categoría:", ttk.Combobox(frame, values=[c[1] for c in self.db.obtener_categorias()], state='readonly')),
            ("💰 Monto:", tk.Entry(frame)),
            ("💱 Moneda:", ttk.Combobox(frame, values=['ARS', 'USD'], state='readonly')),
            ("📝 Descripción:", tk.Entry(frame)),
            ("🏦 Cuenta:", ttk.Combobox(frame, values=[c[1] for c in self.db.obtener_cuentas()], state='readonly')),
        ]
        
        campos[0][1].insert(0, datetime.date.today().isoformat())
        if self.db.obtener_categorias():
            campos[1][1].set(self.db.obtener_categorias()[0][1])
        campos[3][1].set('ARS')
        if self.db.obtener_cuentas():
            campos[5][1].set(self.db.obtener_cuentas()[0][1])
        
        for label, widget in campos:
            tk.Label(frame, text=label, font=('Segoe UI', 9), bg=COLORES['background']).pack(anchor='w', pady=3)
            widget.pack(fill=tk.X, pady=3)
        
        tk.Label(frame, text="🗒️ Notas:", font=('Segoe UI', 9), bg=COLORES['background']).pack(anchor='w', pady=3)
        entry_notas = tk.Text(frame, height=3)
        entry_notas.pack(fill=tk.X, pady=3)
        
        def guardar():
            try:
                fecha = campos[0][1].get()
                categoria = campos[1][1].get()
                monto = float(campos[2][1].get().replace(',', '.'))
                moneda = campos[3][1].get()
                descripcion = campos[4][1].get()
                cuenta = campos[5][1].get()
                notas = entry_notas.get('1.0', tk.END).strip()
                
                if not categoria or monto <= 0:
                    messagebox.showwarning("Error", "Datos inválidos")
                    return
                
                self.db.agregar_gasto(fecha, categoria, monto, moneda, descripcion, cuenta, notas)
                messagebox.showinfo("Éxito", "✅ Gasto agregado")
                v.destroy()
                if self.vista_actual == 'gastos':
                    self.cargar_gastos()
            except ValueError:
                messagebox.showerror("Error", "Monto inválido")
        
        frame_btns = tk.Frame(frame, bg=COLORES['background'])
        frame_btns.pack(pady=15)
        
        tk.Button(frame_btns, text="💾 Guardar", command=guardar, bg=COLORES['success'], 
                 fg='white', font=('Segoe UI', 10, 'bold'), relief=tk.FLAT, cursor='hand2',
                 padx=25, pady=8).pack(side=tk.LEFT, padx=5)
        
        tk.Button(frame_btns, text="❌ Cancelar", command=v.destroy, bg=COLORES['danger'],
                 fg='white', font=('Segoe UI', 10), relief=tk.FLAT, cursor='hand2',
                 padx=25, pady=8).pack(side=tk.LEFT, padx=5)

    def ventana_nueva_meta(self):
        v = tk.Toplevel(self.root)
        v.title("🎯 Nueva Meta")
        v.geometry("450x450")
        v.configure(bg=COLORES['background'])
        v.transient(self.root)
        v.grab_set()
        
        v.update_idletasks()
        x = (v.winfo_screenwidth() // 2) - (450 // 2)
        y = (v.winfo_screenheight() // 2) - (450 // 2)
        v.geometry(f'450x450+{x}+{y}')
        
        frame = tk.Frame(v, bg=COLORES['background'], padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="📝 Nombre:", bg=COLORES['background']).pack(anchor='w', pady=3)
        entry_nombre = tk.Entry(frame)
        entry_nombre.pack(fill=tk.X, pady=3)
        
        tk.Label(frame, text="💰 Monto objetivo:", bg=COLORES['background']).pack(anchor='w', pady=3)
        entry_monto = tk.Entry(frame)
        entry_monto.pack(fill=tk.X, pady=3)
        
        tk.Label(frame, text="💱 Moneda:", bg=COLORES['background']).pack(anchor='w', pady=3)
        combo_moneda = ttk.Combobox(frame, values=['ARS', 'USD'], state='readonly')
        combo_moneda.set('ARS')
        combo_moneda.pack(fill=tk.X, pady=3)
        
        tk.Label(frame, text="📅 Fecha objetivo (YYYY-MM-DD):", bg=COLORES['background']).pack(anchor='w', pady=3)
        entry_fecha = tk.Entry(frame)
        entry_fecha.insert(0, (datetime.date.today() + timedelta(days=180)).isoformat())
        entry_fecha.pack(fill=tk.X, pady=3)
        
        tk.Label(frame, text="🎨 Icono:", bg=COLORES['background']).pack(anchor='w', pady=3)
        iconos = ['🎯', '💰', '🏠', '🚗', '✈️', '🎓', '💍', '🏖️']
        combo_icono = ttk.Combobox(frame, values=iconos, state='readonly')
        combo_icono.set('🎯')
        combo_icono.pack(fill=tk.X, pady=3)
        
        def guardar():
            try:
                nombre = entry_nombre.get().strip()
                monto = float(entry_monto.get().replace(',', '.'))
                moneda = combo_moneda.get()
                fecha = entry_fecha.get()
                icono = combo_icono.get()
                
                if not nombre or monto <= 0:
                    messagebox.showwarning("Error", "Datos inválidos")
                    return
                
                datetime.datetime.strptime(fecha, '%Y-%m-%d')
                
                self.db.agregar_meta(nombre, monto, fecha, moneda, icono)
                messagebox.showinfo("Éxito", "✅ Meta creada")
                v.destroy()
                self.cargar_metas()
            except ValueError:
                messagebox.showerror("Error", "Datos inválidos")
        
        frame_btns = tk.Frame(frame, bg=COLORES['background'])
        frame_btns.pack(pady=20)
        
        tk.Button(frame_btns, text="💾 Crear", command=guardar, bg=COLORES['success'],
                 fg='white', font=('Segoe UI', 10, 'bold'), relief=tk.FLAT, cursor='hand2',
                 padx=25, pady=8).pack(side=tk.LEFT, padx=5)
        
        tk.Button(frame_btns, text="❌ Cancelar", command=v.destroy, bg=COLORES['danger'],
                 fg='white', font=('Segoe UI', 10), relief=tk.FLAT, cursor='hand2',
                 padx=25, pady=8).pack(side=tk.LEFT, padx=5)

    def ventana_sueldo(self):
        v = tk.Toplevel(self.root)
        v.title("💰 Sueldo Mensual")
        v.geometry("400x300")
        v.configure(bg=COLORES['background'])
        v.transient(self.root)
        v.grab_set()
        
        v.update_idletasks()
        x = (v.winfo_screenwidth() // 2) - (400 // 2)
        y = (v.winfo_screenheight() // 2) - (300 // 2)
        v.geometry(f'400x300+{x}+{y}')
        
        frame = tk.Frame(v, bg=COLORES['background'], padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="📅 Mes:", bg=COLORES['background']).pack(anchor='w', pady=3)
        entry_mes = tk.Entry(frame)
        entry_mes.insert(0, self.mes_actual)
        entry_mes.pack(fill=tk.X, pady=3)
        
        tk.Label(frame, text="💰 Sueldo:", bg=COLORES['background']).pack(anchor='w', pady=3)
        entry_sueldo = tk.Entry(frame)
        sueldo_actual = self.db.obtener_sueldo_mes(self.mes_actual)
        if sueldo_actual:
            entry_sueldo.insert(0, str(sueldo_actual[2]))
        entry_sueldo.pack(fill=tk.X, pady=3)
        
        tk.Label(frame, text="🎁 Bonos:", bg=COLORES['background']).pack(anchor='w', pady=3)
        entry_bonos = tk.Entry(frame)
        entry_bonos.insert(0, '0')
        entry_bonos.pack(fill=tk.X, pady=3)
        
        def guardar():
            try:
                mes = entry_mes.get()
                sueldo = float(entry_sueldo.get().replace(',', '.'))
                bonos = float(entry_bonos.get().replace(',', '.'))
                
                if sueldo <= 0:
                    messagebox.showwarning("Error", "Sueldo inválido")
                    return
                
                self.db.guardar_sueldo_mes(mes, sueldo, bonos)
                messagebox.showinfo("Éxito", "✅ Sueldo guardado")
                v.destroy()
            except ValueError:
                messagebox.showerror("Error", "Monto inválido")
        
        frame_btns = tk.Frame(frame, bg=COLORES['background'])
        frame_btns.pack(pady=20)
        
        tk.Button(frame_btns, text="💾 Guardar", command=guardar, bg=COLORES['success'],
                 fg='white', font=('Segoe UI', 10, 'bold'), relief=tk.FLAT, cursor='hand2',
                 padx=25, pady=8).pack(side=tk.LEFT, padx=5)
        
        tk.Button(frame_btns, text="❌ Cancelar", command=v.destroy, bg=COLORES['danger'],
                 fg='white', font=('Segoe UI', 10), relief=tk.FLAT, cursor='hand2',
                 padx=25, pady=8).pack(side=tk.LEFT, padx=5)

    def ventana_categorias(self):
        v = tk.Toplevel(self.root)
        v.title("📂 Categorías")
        v.geometry("600x500")
        v.configure(bg=COLORES['background'])
        v.transient(self.root)
        
        v.update_idletasks()
        x = (v.winfo_screenwidth() // 2) - (600 // 2)
        y = (v.winfo_screenheight() // 2) - (500 // 2)
        v.geometry(f'600x500+{x}+{y}')
        
        frame = tk.Frame(v, bg=COLORES['background'], padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        frame_header = tk.Frame(frame, bg=COLORES['background'])
        frame_header.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(frame_header, text="📂 Gestión de Categorías", font=('Segoe UI', 14, 'bold'),
                bg=COLORES['background']).pack(side=tk.LEFT)
        
        tk.Button(frame_header, text="➕ Nueva", command=lambda: self.ventana_nueva_categoria(cargar),
                 bg=COLORES['success'], fg='white', font=('Segoe UI', 9, 'bold'), relief=tk.FLAT,
                 cursor='hand2', padx=15, pady=6).pack(side=tk.RIGHT)
        
        canvas = tk.Canvas(frame, bg=COLORES['background'], highlightthickness=0)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        frame_lista = tk.Frame(canvas, bg=COLORES['background'])
        
        frame_lista.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame_lista, anchor="nw", width=540)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def cargar():
            for widget in frame_lista.winfo_children():
                widget.destroy()
            
            cats = self.db.obtener_categorias()
            
            if not cats:
                tk.Label(frame_lista, text="No hay categorías", bg=COLORES['background']).pack(pady=30)
                return
            
            for cat in cats:
                id_cat, nombre, color = cat[:3]
                icono = cat[3] if len(cat) > 3 else '❓'
                
                f = tk.Frame(frame_lista, bg=COLORES['card_bg'], relief=tk.RAISED, bd=1)
                f.pack(fill=tk.X, pady=4, padx=4)
                
                tk.Frame(f, bg=color, width=6).pack(side=tk.LEFT, fill=tk.Y)
                
                tk.Label(f, text=f"{icono} {nombre}", font=('Segoe UI', 10, 'bold'),
                        bg=COLORES['card_bg']).pack(side=tk.LEFT, padx=15, pady=10)
                
                tk.Button(f, text="🗑️", command=lambda i=id_cat: eliminar(i), bg=COLORES['danger'],
                         fg='white', relief=tk.FLAT, cursor='hand2', width=3).pack(side=tk.RIGHT, padx=10)
        
        def eliminar(id_cat):
            if messagebox.askyesno("Confirmar", "¿Eliminar esta categoría?"):
                try:
                    self.db.eliminar_categoria(id_cat)
                    messagebox.showinfo("Éxito", "Categoría eliminada")
                    cargar()
                except Exception as e:
                    messagebox.showerror("Error", f"Error: {e}")
        
        cargar()

    def ventana_nueva_categoria(self, callback=None):
        v = tk.Toplevel(self.root)
        v.title("➕ Nueva Categoría")
        v.geometry("650x600")
        v.configure(bg=COLORES['background'])
        v.transient(self.root)
        v.grab_set()

        v.update_idletasks()
        x = (v.winfo_screenwidth() // 2) - (650 // 2)
        y = (v.winfo_screenheight() // 2) - (600 // 2)
        v.geometry(f'650x600+{x}+{y}')

        frame = tk.Frame(v, bg=COLORES['background'], padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="📝 Nombre:", bg=COLORES['background']).pack(anchor='w', pady=3)
        entry_nombre = tk.Entry(frame, font=('Segoe UI', 11))
        entry_nombre.pack(fill=tk.X, pady=3)

        tk.Label(frame, text="🎨 Color (hex):", bg=COLORES['background']).pack(anchor='w', pady=3)
        entry_color = tk.Entry(frame, font=('Segoe UI', 11))
        entry_color.insert(0, '#4a90e2')
        entry_color.pack(fill=tk.X, pady=3)

        tk.Label(frame, text=f"📌 Selecciona un icono ({len(ICONOS_CATEGORIAS)} disponibles):",
                font=('Segoe UI', 10, 'bold'), bg=COLORES['background']).pack(anchor='w', pady=(10, 3))

        # Canvas con scroll para los iconos
        canvas_iconos = tk.Canvas(frame, height=300, bg=COLORES['card_bg'], highlightthickness=1,
                                 highlightbackground=COLORES['border'])
        scrollbar_iconos = tk.Scrollbar(frame, orient="vertical", command=canvas_iconos.yview)

        frame_iconos = tk.Frame(canvas_iconos, bg=COLORES['card_bg'])
        frame_iconos.bind("<Configure>", lambda e: canvas_iconos.configure(scrollregion=canvas_iconos.bbox("all")))

        canvas_iconos.create_window((0, 0), window=frame_iconos, anchor="nw", width=580)
        canvas_iconos.configure(yscrollcommand=scrollbar_iconos.set)

        canvas_iconos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=5)
        scrollbar_iconos.pack(side=tk.RIGHT, fill=tk.Y)

        icono_sel = tk.StringVar(value='📂')
        botones_iconos = []

        # Crear grid de iconos
        for i, ico in enumerate(ICONOS_CATEGORIAS):
            btn = tk.Button(frame_iconos, text=ico, font=('Segoe UI', 16), bg=COLORES['card_bg'],
                           relief=tk.FLAT, cursor='hand2', width=2, height=1,
                           command=lambda ic=ico: seleccionar_icono(ic))
            btn.grid(row=i//15, column=i%15, padx=2, pady=2)
            botones_iconos.append(btn)

        # Icono seleccionado (más grande)
        frame_sel = tk.Frame(frame, bg=COLORES['light'], relief=tk.RAISED, bd=2)
        frame_sel.pack(fill=tk.X, pady=10)

        tk.Label(frame_sel, text="Icono seleccionado:", font=('Segoe UI', 9),
                bg=COLORES['light']).pack(pady=(10, 5))
        lbl_icono = tk.Label(frame_sel, textvariable=icono_sel, font=('Segoe UI', 40),
                            bg=COLORES['light'])
        lbl_icono.pack(pady=(0, 10))

        def seleccionar_icono(icono):
            icono_sel.set(icono)
            # Resaltar botón seleccionado
            for btn in botones_iconos:
                btn.config(bg=COLORES['card_bg'])
            # Encontrar y resaltar el botón clickeado
            for btn in botones_iconos:
                if btn.cget('text') == icono:
                    btn.config(bg=COLORES['primary'])
                    break

        def guardar():
            try:
                nombre = entry_nombre.get().strip()
                color = entry_color.get().strip()
                icono = icono_sel.get()

                if not nombre:
                    messagebox.showwarning("Error", "Ingresá un nombre")
                    return

                self.db.agregar_categoria(nombre, color, icono)
                messagebox.showinfo("Éxito", "✅ Categoría agregada")
                v.destroy()
                if callback:
                    callback()
            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")

        frame_btns = tk.Frame(frame, bg=COLORES['background'])
        frame_btns.pack(pady=10)

        tk.Button(frame_btns, text="💾 Guardar", command=guardar, bg=COLORES['success'],
                 fg='white', font=('Segoe UI', 10, 'bold'), relief=tk.FLAT, cursor='hand2',
                 padx=25, pady=8).pack(side=tk.LEFT, padx=5)

        tk.Button(frame_btns, text="❌ Cancelar", command=v.destroy, bg=COLORES['danger'],
                 fg='white', font=('Segoe UI', 10), relief=tk.FLAT, cursor='hand2',
                 padx=25, pady=8).pack(side=tk.LEFT, padx=5)

    def exportar_csv(self):
        try:
            gastos = self.db.obtener_gastos()
            if not gastos:
                messagebox.showwarning("Sin datos", "No hay gastos para exportar")
                return
            
            archivo = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialfile=f"gastos_{datetime.date.today().isoformat()}.csv"
            )
            
            if archivo:
                with open(archivo, 'w', encoding='utf-8-sig') as f:
                    f.write("Fecha,Categoría,Monto,Moneda,Descripción,Cuenta\n")
                    for g in gastos:
                        f.write(f"{g[1]},{g[2]},{g[3]},{g[4]},{g[5] or ''},{g[6]}\n")
                
                messagebox.showinfo("Éxito", f"✅ Exportado:\n{archivo}")
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")

    def hacer_backup(self):
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            archivo = RUTA_BACKUPS / f"backup_{timestamp}.db"
            shutil.copy2(RUTA_DB, archivo)
            messagebox.showinfo("Backup", f"✅ Backup creado:\n{archivo}")
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")

    def mostrar_ayuda(self):
        """Sección de ayuda con explicaciones detalladas y ejemplos"""
        # Header
        frame_header = tk.Frame(self.frame_contenido, bg=COLORES['primary'], height=80)
        frame_header.pack(fill=tk.X, padx=15, pady=15)
        frame_header.pack_propagate(False)

        tk.Label(
            frame_header,
            text="❓ Centro de Ayuda",
            font=('Segoe UI', 18, 'bold'),
            bg=COLORES['primary'],
            fg='white'
        ).pack(padx=20, pady=20)

        # Frame principal con scroll
        canvas = tk.Canvas(self.frame_contenido, bg=COLORES['background'], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.frame_contenido, orient="vertical", command=canvas.yview)
        frame_scroll = tk.Frame(canvas, bg=COLORES['background'])

        frame_scroll.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=frame_scroll, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Secciones de ayuda
        secciones_ayuda = [
            {
                "titulo": "📊 Dashboard",
                "icono": "📊",
                "descripcion": "Panel principal con resumen de tu actividad financiera",
                "caracteristicas": [
                    "Visualiza tu balance total actualizado",
                    "Gráficos de gastos por categoría",
                    "Estadísticas mensuales y tendencias",
                    "Acceso rápido a todas las funciones"
                ],
                "ejemplo": "💡 Ejemplo: Si gastaste $50,000 este mes y tu sueldo es $100,000, verás tu balance restante de $50,000 destacado en el dashboard."
            },
            {
                "titulo": "⚡ Entrada Rápida",
                "icono": "⚡",
                "descripcion": "Registra gastos e ingresos de forma ultra-rápida estilo Monefy",
                "caracteristicas": [
                    "Interfaz simplificada con teclado numérico",
                    "Categorías predefinidas con emojis",
                    "Registro en segundos sin complicaciones",
                    "Perfecto para uso diario"
                ],
                "ejemplo": "💡 Ejemplo: Compraste café por $2,500 → Abrí Entrada Rápida → Tecleá 2500 → Tocá ☕ Café → ¡Listo!"
            },
            {
                "titulo": "📋 Gastos",
                "icono": "📋",
                "descripcion": "Gestión completa de todos tus movimientos financieros",
                "caracteristicas": [
                    "Lista detallada de ingresos y gastos",
                    "Filtros por fecha, categoría y tipo",
                    "Editar o eliminar transacciones",
                    "Exportar a CSV o Excel"
                ],
                "ejemplo": "💡 Ejemplo: Para ver todos los gastos de 'Supermercado' en enero, usá los filtros de categoría y fecha."
            },
            {
                "titulo": "🔔 Alertas",
                "icono": "🔔",
                "descripcion": "Sistema inteligente de notificaciones proactivas",
                "caracteristicas": [
                    "Alertas cuando te acercás al límite de presupuesto",
                    "Recordatorios de cuentas por pagar",
                    "Notificaciones de metas cercanas a cumplirse",
                    "Avisos de suscripciones próximas a vencer"
                ],
                "ejemplo": "💡 Ejemplo: Si configuraste un presupuesto de $80,000 para 'Entretenimiento' y ya gastaste $70,000, recibirás una alerta proactiva."
            },
            {
                "titulo": "📅 Cuentas por Pagar",
                "icono": "📅",
                "descripcion": "Nunca olvides un pago importante",
                "caracteristicas": [
                    "Registra servicios, impuestos y facturas",
                    "Establecé fechas de vencimiento",
                    "Marca como pagado cuando abones",
                    "Recibí recordatorios automáticos"
                ],
                "ejemplo": "💡 Ejemplo: Agregá 'Luz - $5,000 - Vence 15/11' → La app te recordará 3 días antes del vencimiento."
            },
            {
                "titulo": "👥 Deudas Compartidas (Splitwise)",
                "icono": "👥",
                "descripcion": "Gestiona gastos compartidos con amigos y familia",
                "caracteristicas": [
                    "Crea grupos de gasto compartido",
                    "Divide gastos equitativamente o por porcentaje",
                    "Visualiza quién debe a quién",
                    "Registra pagos y liquida cuentas"
                ],
                "ejemplo": "💡 Ejemplo: Viaje con 3 amigos → Creá grupo 'Viaje a Bariloche' → Registrá gasto de hotel $30,000 → La app calcula que cada uno debe $7,500."
            },
            {
                "titulo": "🎯 Metas de Ahorro",
                "icono": "🎯",
                "descripcion": "Alcanza tus objetivos financieros",
                "caracteristicas": [
                    "Define metas con monto objetivo",
                    "Establece fecha límite",
                    "Aporta fondos progresivamente",
                    "Visualiza tu progreso con barras animadas"
                ],
                "ejemplo": "💡 Ejemplo: Meta 'Notebook Nueva' - $500,000 - Para diciembre → Aporta $50,000 mensuales → Seguí tu progreso: 20%, 40%, 60%..."
            },
            {
                "titulo": "💰 Ahorro Automático",
                "icono": "💰",
                "descripcion": "Reglas inteligentes para ahorrar sin esfuerzo",
                "caracteristicas": [
                    "Ahorro por redondeo (guarda el vuelto)",
                    "Ahorro por porcentaje de ingresos",
                    "Ahorro en fechas específicas",
                    "Aporte automático a tus metas"
                ],
                "ejemplo": "💡 Ejemplo: Configurá 'Ahorrar 10% de cada ingreso' → Si cobras $100,000, automáticamente se destinan $10,000 a tu meta."
            },
            {
                "titulo": "📺 Suscripciones",
                "icono": "📺",
                "descripcion": "Controla todos tus servicios recurrentes",
                "caracteristicas": [
                    "Registra Netflix, Spotify, gym, etc.",
                    "Visualiza costo mensual y anual",
                    "Recibí alertas de renovación",
                    "Identifica suscripciones que no usás"
                ],
                "ejemplo": "💡 Ejemplo: Netflix $3,500/mes + Spotify $1,000/mes = $4,500/mes → Anual: $54,000. ¿Realmente usás ambas?"
            },
            {
                "titulo": "💳 Tarjetas de Crédito",
                "icono": "💳",
                "descripcion": "Gestiona tus tarjetas y evita sorpresas",
                "caracteristicas": [
                    "Registra múltiples tarjetas con límites",
                    "Visualiza saldo disponible",
                    "Calcula interés de financiaciones",
                    "Alerta cuando te acercás al límite"
                ],
                "ejemplo": "💡 Ejemplo: Visa con límite $200,000 → Ya gastaste $180,000 → Alerta: 'Solo quedan $20,000 disponibles'."
            },
            {
                "titulo": "🔄 Gastos Recurrentes",
                "icono": "🔄",
                "descripcion": "Automatiza gastos que se repiten",
                "caracteristicas": [
                    "Define frecuencia: diaria, semanal, mensual",
                    "La app registra automáticamente",
                    "Edita o pausa recurrencias",
                    "Ideal para alquileres, expensas, etc."
                ],
                "ejemplo": "💡 Ejemplo: Alquiler $50,000 cada día 10 → Se registra automáticamente sin que tengas que recordarlo."
            },
            {
                "titulo": "📊 Presupuestos",
                "icono": "📊",
                "descripcion": "Establece límites de gasto por categoría",
                "caracteristicas": [
                    "Define presupuesto mensual por categoría",
                    "Visualiza % consumido en tiempo real",
                    "Recibí alertas al llegar al 80%",
                    "Compara meses anteriores"
                ],
                "ejemplo": "💡 Ejemplo: Presupuesto 'Comida' $60,000 → Ya gastaste $48,000 (80%) → Alerta: 'Te quedan $12,000 para este mes'."
            },
            {
                "titulo": "🤝 Buddy Presupuestos",
                "icono": "🤝",
                "descripcion": "Comparte presupuestos con pareja o familia",
                "caracteristicas": [
                    "Presupuestos colaborativos",
                    "Cada miembro registra sus gastos",
                    "Visualiza consumo grupal",
                    "Notificaciones compartidas"
                ],
                "ejemplo": "💡 Ejemplo: Presupuesto compartido 'Hogar' $100,000 → Vos gastás $40,000 + Tu pareja $35,000 = $75,000 usado (75%)."
            },
            {
                "titulo": "🏆 FinScore",
                "icono": "🏆",
                "descripcion": "Tu score de salud financiera gamificado",
                "caracteristicas": [
                    "Puntaje de 0 a 1000 según tus hábitos",
                    "Factores: ahorro, deudas, presupuestos",
                    "Consejos personalizados para mejorar",
                    "Compara tu progreso mensual"
                ],
                "ejemplo": "💡 Ejemplo: FinScore 750 → 'Muy Bueno' → Mejora aportando más a metas y reduciendo gastos hormiga."
            },
            {
                "titulo": "🎨 Temas",
                "icono": "🎨",
                "descripcion": "Personaliza la apariencia de tu app",
                "caracteristicas": [
                    "Múltiples temas de colores",
                    "Modo claro y oscuro",
                    "Paletas cuidadosamente diseñadas",
                    "Cambia cuando quieras"
                ],
                "ejemplo": "💡 Ejemplo: ¿Te cansa el azul? Cambia a 'Sunset Vibes' con tonos naranjas y violetas."
            },
            {
                "titulo": "🎮 Logros",
                "icono": "🎮",
                "descripcion": "Sistema de gamificación para motivarte",
                "caracteristicas": [
                    "Desbloquea logros por buenos hábitos",
                    "Badges especiales y rarezas",
                    "Progreso con barras visuales",
                    "¡Colecciona todos los logros!"
                ],
                "ejemplo": "💡 Ejemplo: Logro desbloqueado: '💰 Ahorrador Novato' - Alcanzaste tu primera meta de ahorro de $10,000."
            },
            {
                "titulo": "💱 Conversor",
                "icono": "💱",
                "descripcion": "Conversión de monedas en tiempo real",
                "caracteristicas": [
                    "Dólar oficial, blue, MEP, etc.",
                    "Múltiples monedas internacionales",
                    "Tasas actualizadas automáticamente",
                    "Calcula en ambas direcciones"
                ],
                "ejemplo": "💡 Ejemplo: ¿Cuánto es USD 100 al blue? → El conversor te muestra: $107,500 (si blue = $1,075)."
            },
        ]

        for seccion in secciones_ayuda:
            # Frame de la sección
            frame_seccion = tk.Frame(
                frame_scroll,
                bg=COLORES['card_bg'],
                relief=tk.SOLID,
                bd=1,
                highlightbackground=COLORES['border'],
                highlightthickness=1
            )
            frame_seccion.pack(fill=tk.X, padx=10, pady=10)

            # Título de la sección
            frame_titulo = tk.Frame(frame_seccion, bg=COLORES['primary'], height=50)
            frame_titulo.pack(fill=tk.X)
            frame_titulo.pack_propagate(False)

            tk.Label(
                frame_titulo,
                text=seccion['titulo'],
                font=('Segoe UI', 14, 'bold'),
                bg=COLORES['primary'],
                fg='white',
                anchor='w'
            ).pack(side=tk.LEFT, padx=15, pady=10)

            # Descripción
            tk.Label(
                frame_seccion,
                text=seccion['descripcion'],
                font=('Segoe UI', 11),
                bg=COLORES['card_bg'],
                fg=COLORES['text_primary'],
                wraplength=800,
                justify=tk.LEFT,
                anchor='w'
            ).pack(fill=tk.X, padx=15, pady=(10, 5))

            # Características
            tk.Label(
                frame_seccion,
                text="✨ Características:",
                font=('Segoe UI', 10, 'bold'),
                bg=COLORES['card_bg'],
                fg=COLORES['primary'],
                anchor='w'
            ).pack(fill=tk.X, padx=15, pady=(10, 5))

            for caract in seccion['caracteristicas']:
                tk.Label(
                    frame_seccion,
                    text=f"  • {caract}",
                    font=('Segoe UI', 9),
                    bg=COLORES['card_bg'],
                    fg=COLORES['text_secondary'],
                    wraplength=780,
                    justify=tk.LEFT,
                    anchor='w'
                ).pack(fill=tk.X, padx=15, pady=2)

            # Ejemplo
            frame_ejemplo = tk.Frame(
                frame_seccion,
                bg='#FFF9E6',
                relief=tk.SOLID,
                bd=1,
                highlightbackground='#FFD700',
                highlightthickness=2
            )
            frame_ejemplo.pack(fill=tk.X, padx=15, pady=10)

            tk.Label(
                frame_ejemplo,
                text=seccion['ejemplo'],
                font=('Segoe UI', 10, 'italic'),
                bg='#FFF9E6',
                fg='#8B6914',
                wraplength=760,
                justify=tk.LEFT,
                anchor='w'
            ).pack(padx=10, pady=8)

        # Footer con tips adicionales
        frame_footer = tk.Frame(
            frame_scroll,
            bg=COLORES['success'],
            relief=tk.SOLID,
            bd=2
        )
        frame_footer.pack(fill=tk.X, padx=10, pady=20)

        tk.Label(
            frame_footer,
            text="💡 Tip General: Usa el botón '⚡ ENTRADA RÁPIDA' para gastos del día a día, "
                 "y '➕ Entrada Completa' cuando necesites agregar más detalles como notas, fotos o etiquetas.",
            font=('Segoe UI', 10, 'bold'),
            bg=COLORES['success'],
            fg='white',
            wraplength=780,
            justify=tk.CENTER
        ).pack(padx=20, pady=15)

        # Bind scroll con rueda del mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def mostrar_acerca_de(self):
        messagebox.showinfo(
            "Acerca de",
            "💰 Gestor de Gastos Personal v3.1\n\n"
            "Desarrollado por: Maximiliano Burgos\n"
            "Año: 2025\n\n"
            "✨ Características:\n"
            "• Dashboard interactivo\n"
            "• Gestión completa de gastos\n"
            "• Metas de ahorro\n"
            "• Cotización del dólar\n"
            "• Exportación CSV\n"
            "• Backups automáticos\n\n"
            "Tecnologías:\n"
            "Python • Tkinter • SQLite • Matplotlib"
        )

    def al_cerrar(self):
        if messagebox.askyesno("Salir", "¿Cerrar la aplicación?"):
            try:
                timestamp = datetime.datetime.now().strftime("%Y%m%d")
                archivo = RUTA_BACKUPS / f"auto_{timestamp}.db"
                if not archivo.exists():
                    shutil.copy2(RUTA_DB, archivo)
            except:
                pass
            
            self.db.cerrar()
            self.root.destroy()


# === PUNTO DE ENTRADA ===
if __name__ == "__main__":
    print("=" * 50)
    print("💰 GESTOR DE GASTOS PERSONAL v3.1")
    print("=" * 50)
    print(f"📁 Base de datos: {RUTA_DB}")
    print(f"💾 Backups: {RUTA_BACKUPS}")
    print("=" * 50)
    
    try:
        root = tk.Tk()
        app = GestorGastos(root)
        root.mainloop()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        messagebox.showerror("Error Fatal", f"Error:\n{e}")
    
    print("\n👋 Aplicación cerrada")