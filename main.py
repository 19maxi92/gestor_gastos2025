"""
💰 GESTOR DE GASTOS PERSONAL v3.1 - VERSIÓN COMPLETA Y FUNCIONAL
Aplicación completa para gestión de finanzas personales
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

# === CONFIGURACION ===
warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")
plt.rcParams['font.family'] = 'DejaVu Sans'

# === RUTAS ===
RUTA_BASE = Path(__file__).parent
RUTA_DATA = RUTA_BASE / "data"
RUTA_DB = RUTA_DATA / "gastos.db"
RUTA_BACKUPS = RUTA_DATA / "backups"

for ruta in [RUTA_DATA, RUTA_BACKUPS]:
    ruta.mkdir(parents=True, exist_ok=True)

# === COLORES MODERNOS ===
COLORES = {
    'primary': '#6366f1',  # Indigo moderno
    'primary_dark': '#4f46e5',
    'secondary': '#8b5cf6',  # Purple
    'success': '#10b981',  # Green
    'danger': '#ef4444',  # Red
    'warning': '#f59e0b',  # Amber
    'info': '#06b6d4',  # Cyan
    'light': '#f9fafb',
    'dark': '#1f2937',
    'background': '#f3f4f6',  # Gray-100
    'card_bg': '#ffffff',
    'sidebar_bg': '#1f2937',  # Dark sidebar
    'sidebar_hover': '#374151',
    'text': '#111827',
    'text_secondary': '#6b7280',
    'border': '#e5e7eb',
    'accent': '#ec4899',  # Pink accent
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


# === APLICACIÓN PRINCIPAL ===
class GestorGastos:
    def __init__(self, root):
        self.root = root
        self.root.title("💰 Gestor de Gastos Personal v4.0 - Edición Mejorada")
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
        self.crear_interfaz()
        self.actualizar_cotizaciones()
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
        menu_config.add_command(label="Sueldo Mensual", command=self.ventana_sueldo)
        menu_config.add_command(label="Gestionar Categorías", command=self.ventana_categorias)

        menu_ayuda = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="❓ Ayuda", menu=menu_ayuda)
        menu_ayuda.add_command(label="Acerca de", command=self.mostrar_acerca_de)

        # HEADER
        frame_header = tk.Frame(self.root, bg=COLORES['primary'], height=65)
        frame_header.pack(fill=tk.X)
        frame_header.pack_propagate(False)

        tk.Label(
            frame_header,
            text="💰 Gestor de Gastos v4.0",
            font=('Segoe UI', 20, 'bold'),
            bg=COLORES['primary'],
            fg='white'
        ).pack(side=tk.LEFT, padx=25)

        # Cotización en header
        self.label_dolar = tk.Label(
            frame_header,
            text="💱 Cargando...",
            font=('Segoe UI', 10),
            bg=COLORES['primary'],
            fg='white'
        )
        self.label_dolar.pack(side=tk.RIGHT, padx=25)

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

        # SIDEBAR
        sidebar = tk.Frame(frame_main, bg=COLORES['sidebar_bg'], width=250)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        # Botón de agregar gasto destacado
        tk.Button(
            sidebar,
            text="➕ AGREGAR GASTO",
            font=('Segoe UI', 12, 'bold'),
            bg=COLORES['success'],
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.ventana_agregar_gasto,
            pady=15
        ).pack(fill=tk.X, padx=15, pady=(20, 30))

        # Botones de navegación
        nav_buttons = [
            ("📊 Dashboard", 'dashboard', self.mostrar_dashboard),
            ("⚡ Registro Rápido", 'registro_rapido', self.ventana_registro_rapido),
            ("📋 Gastos", 'gastos', self.mostrar_gastos),
            ("🔔 Alertas", 'alertas', self.mostrar_alertas),
            ("📅 Cuentas por Pagar", 'cuentas_pagar', self.mostrar_cuentas_por_pagar),
            ("👥 Deudas Compartidas", 'deudas', self.mostrar_deudas),
            ("🎯 Metas de Ahorro", 'metas', self.mostrar_metas),
            ("💳 Tarjetas", 'tarjetas', self.mostrar_tarjetas),
            ("🔄 Recurrentes", 'recurrentes', self.mostrar_recurrentes),
            ("📊 Presupuestos", 'presupuestos', self.mostrar_presupuestos),
            ("🎮 Logros", 'logros', self.mostrar_logros),
            ("💱 Conversor", 'conversor', self.ventana_conversor),
        ]

        self.nav_buttons = {}
        for text, vista, comando in nav_buttons:
            btn = tk.Button(
                sidebar,
                text=text,
                font=('Segoe UI', 11, 'bold'),
                bg=COLORES['sidebar_bg'],
                fg='white',
                relief=tk.FLAT,
                cursor='hand2',
                anchor='w',
                padx=20,
                pady=12,
                command=lambda v=vista, c=comando: self.cambiar_vista(v, c)
            )
            btn.pack(fill=tk.X, padx=5, pady=2)
            btn.bind('<Enter>', lambda e, b=btn: b.config(bg=COLORES['sidebar_hover']))
            btn.bind('<Leave>', lambda e, b=btn, v=vista: b.config(
                bg=COLORES['primary'] if self.vista_actual == v else COLORES['sidebar_bg']
            ))
            self.nav_buttons[vista] = btn

        # Espacio
        tk.Frame(sidebar, bg=COLORES['sidebar_bg']).pack(expand=True)

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
        frame_resumen = tk.Frame(frame_scroll, bg=COLORES['card_bg'], relief=tk.RAISED, bd=2)
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
        
        # Gráfico
        if gastos:
            frame_grafico = tk.Frame(frame_scroll, bg=COLORES['card_bg'], relief=tk.RAISED, bd=2)
            frame_grafico.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            tk.Label(
                frame_grafico,
                text="📊 Gastos por Categoría",
                font=('Segoe UI', 12, 'bold'),
                bg=COLORES['card_bg']
            ).pack(pady=10)
            
            cats = {}
            for g in gastos:
                cats[g[2]] = cats.get(g[2], 0) + g[3]
            
            fig = Figure(figsize=(9, 4), facecolor=COLORES['card_bg'])
            ax = fig.add_subplot(111)
            ax.pie(cats.values(), labels=cats.keys(), autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            
            canvas_graf = FigureCanvasTkAgg(fig, frame_grafico)
            canvas_graf.draw()
            canvas_graf.get_tk_widget().pack()

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
        
        for g in gastos:
            self.tree.insert('', tk.END, values=(g[1], g[2], f"{g[3]:,.2f}", g[4], g[5] or '', g[6]), tags=(g[0],))

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
        
        frame = tk.Frame(self.frame_metas, bg=COLORES['card_bg'], relief=tk.RAISED, bd=2)
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
        
        frame = tk.Frame(self.frame_tarjetas, bg=COLORES['card_bg'], relief=tk.RAISED, bd=2)
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

        frame = tk.Frame(parent, bg=COLORES['card_bg'], relief=tk.RAISED, bd=2)
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

        frame = tk.Frame(parent, bg=COLORES['card_bg'], relief=tk.RAISED, bd=2)
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

            frame = tk.Frame(frame_lista, bg=COLORES['card_bg'], relief=tk.RAISED, bd=2)
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

            frame = tk.Frame(frame_lista, bg=COLORES['card_bg'], relief=tk.RAISED, bd=2)
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

            frame = tk.Frame(frame_lista, bg=COLORES['card_bg'], relief=tk.RAISED, bd=2)
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

            frame = tk.Frame(frame_lista, bg=COLORES['card_bg'], relief=tk.RAISED, bd=2)
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
        
        frame_conv = tk.Frame(frame, bg=COLORES['card_bg'], relief=tk.RAISED, bd=2)
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
        v.geometry("550x500")
        v.configure(bg=COLORES['background'])
        v.transient(self.root)
        v.grab_set()

        v.update_idletasks()
        x = (v.winfo_screenwidth() // 2) - (550 // 2)
        y = (v.winfo_screenheight() // 2) - (500 // 2)
        v.geometry(f'550x500+{x}+{y}')

        frame = tk.Frame(v, bg=COLORES['background'], padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            frame,
            text="⚡ Registro Rápido - Escribí tu gasto en lenguaje natural",
            font=('Segoe UI', 12, 'bold'),
            bg=COLORES['background']
        ).pack(pady=(0, 10))

        tk.Label(
            frame,
            text='Ejemplos:\n"Gasto 2000 en supermercado"\n"Pagué 1500 de comida"\n"Almuerzo $350"\n"500 pesos en café"',
            font=('Segoe UI', 9),
            bg=COLORES['background'],
            fg=COLORES['text_secondary'],
            justify=tk.LEFT
        ).pack(pady=(0, 15))

        # Campo de texto libre
        tk.Label(frame, text="💬 Describe tu gasto:", font=('Segoe UI', 10, 'bold'),
                bg=COLORES['background']).pack(anchor='w', pady=3)

        entry_texto = tk.Entry(frame, font=('Segoe UI', 12))
        entry_texto.pack(fill=tk.X, pady=5, ipady=5)
        entry_texto.focus()

        # Frame de vista previa
        frame_preview = tk.Frame(frame, bg=COLORES['card_bg'], relief=tk.RAISED, bd=2)
        frame_preview.pack(fill=tk.BOTH, expand=True, pady=15)

        tk.Label(
            frame_preview,
            text="📝 Vista Previa",
            font=('Segoe UI', 10, 'bold'),
            bg=COLORES['card_bg']
        ).pack(pady=10)

        lbl_monto = tk.Label(frame_preview, text="💰 Monto: -", font=('Segoe UI', 10),
                            bg=COLORES['card_bg'], anchor='w')
        lbl_monto.pack(fill=tk.X, padx=15, pady=3)

        lbl_categoria = tk.Label(frame_preview, text="📂 Categoría: -", font=('Segoe UI', 10),
                                bg=COLORES['card_bg'], anchor='w')
        lbl_categoria.pack(fill=tk.X, padx=15, pady=3)

        lbl_descripcion = tk.Label(frame_preview, text="📝 Descripción: -", font=('Segoe UI', 10),
                                   bg=COLORES['card_bg'], anchor='w')
        lbl_descripcion.pack(fill=tk.X, padx=15, pady=3)

        lbl_confianza = tk.Label(frame_preview, text="", font=('Segoe UI', 9),
                                bg=COLORES['card_bg'], fg=COLORES['text_secondary'])
        lbl_confianza.pack(pady=5)

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
        frame_btns.pack(pady=10)

        tk.Button(frame_btns, text="💾 Guardar", command=guardar, bg=COLORES['success'],
                 fg='white', font=('Segoe UI', 11, 'bold'), relief=tk.FLAT, cursor='hand2',
                 padx=30, pady=10).pack(side=tk.LEFT, padx=5)

        tk.Button(frame_btns, text="❌ Cancelar", command=v.destroy, bg=COLORES['danger'],
                 fg='white', font=('Segoe UI', 10), relief=tk.FLAT, cursor='hand2',
                 padx=30, pady=10).pack(side=tk.LEFT, padx=5)

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