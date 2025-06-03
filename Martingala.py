import streamlit as st
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

# Configuración de acceso a Google Sheets usando el secreto
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credenciales = ServiceAccountCredentials.from_json_keyfile_dict(
    json.loads(st.secrets["GOOGLE_CREDENTIALS"]), scope
)
cliente = gspread.authorize(credenciales)
sheet = cliente.open("Control Apuestas Rentables").sheet1

st.set_page_config(page_title="Simulador de Apuesta con Martingala Reducida", layout="centered")
st.title("📈 Simulador de Apuesta con\nMartingala Reducida")

# Leer última fila
datos = pd.DataFrame(sheet.get_all_records())

if datos.empty:
    st.warning("No hay datos aún.")
    datos = pd.DataFrame(columns=["Bankroll", "Cuota", "Apuesta", "Ganancia", "Resultado"])

# Configuración inicial
st.subheader("🎰 Configuración inicial")
bankroll_inicial = st.number_input("💰 Ingrese su bankroll inicial:", value=200000)
cuota_promedio = st.number_input("🎯 Cuota promedio:", value=1.80, step=0.01)

if st.button("Guardar configuración inicial"):
    apuesta = bankroll_inicial / 100
    nueva_fila = [bankroll_inicial, cuota_promedio, round(apuesta, 2), 0, "Inicio"]
    sheet.append_row(nueva_fila)
    st.success(f"✅ Primera apuesta sugerida: {apuesta:.2f}")

# Evaluar siguiente apuesta
st.markdown("---")
st.subheader("🔁 ¿Cómo terminó la última apuesta?")

cuota_real = st.number_input("📌 Ingresa la cuota real de esta apuesta:", value=1.80, step=0.01)
ganada = st.checkbox("✅ Ganada")
perdida = st.checkbox("❌ Perdida")

if ganada and perdida:
    st.error("Selecciona solo una opción: Ganada o Perdida.")
elif cuota_real > 10:
    st.warning("⚠️ Cuota muy alta. Por favor corrígela antes de continuar.")
else:
    if st.button("Guardar resultado"):
        ultima = pd.DataFrame(sheet.get_all_records()).iloc[-1]

        if ultima["Resultado"] == "Inicio":
            bankroll = float(ultima["Bankroll"])
        else:
            bankroll = float(ultima["Bankroll"])

        apuesta = float(ultima["Apuesta"])

        if ganada:
            ganancia = apuesta * (cuota_real - 1)
            nuevo_bankroll = bankroll + ganancia
            nueva_apuesta = nuevo_bankroll / 100
            resultado = "Ganada"
            st.success(f"✅ Ganaste. Nueva apuesta sugerida: {nueva_apuesta:.2f}")
        elif perdida:
            ganancia = 0
            nuevo_bankroll = bankroll - apuesta
            nueva_apuesta = apuesta * cuota_real
            resultado = "Perdida"
            st.error(f"❌ Perdiste. Nueva apuesta sugerida: {nueva_apuesta:.2f}")
        else:
            ganancia = 0
            nueva_apuesta = apuesta
            resultado = ""

        nueva_fila = [nuevo_bankroll, cuota_real, round(nueva_apuesta, 2), round(ganancia, 2), resultado]
        sheet.append_row(nueva_fila)

# Mostrar próxima apuesta sugerida
st.markdown("---")
st.subheader("📌 Próxima apuesta sugerida")

try:
    ultima_valida = pd.DataFrame(sheet.get_all_records()).iloc[-1]
    st.success(f"💵 {ultima_valida['Apuesta']:.2f}")
except:
    st.info("No hay apuestas previas.")
