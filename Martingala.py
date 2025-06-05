import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# Configurar acceso a Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credenciales = ServiceAccountCredentials.from_json_keyfile_dict(
    st.secrets["GOOGLE_CREDENTIALS"], scope
)
cliente = gspread.authorize(credenciales)
sheet = cliente.open("Control Apuestas Rentables").sheet1

st.set_page_config(page_title="Simulador Martingala", layout="centered")

st.title("📈 Simulador de Apuesta con\nMartingala Reducida")

st.header("🎰 Configuración inicial")
bankroll_inicial = st.number_input("💰 Ingrese su bankroll inicial:", step=1000, value=200000)
cuota_promedio = st.number_input("🎯 Cuota promedio:", step=0.1, value=1.8)

if st.button("Guardar configuración inicial"):
    unidad = bankroll_inicial / 100
    sheet.append_row([bankroll_inicial, cuota_promedio, unidad, 0, "Inicio"])
    st.success(f"✅ Primera apuesta sugerida: {unidad:.2f}")

st.divider()
st.subheader("🔄 ¿Cómo terminó la última apuesta?")
cuota_real = st.text_input("📌 Ingresa la cuota real de esta apuesta:", value="1.80")
col1, col2 = st.columns(2)

with col1:
    ganada = st.button("✅ Ganada")
with col2:
    perdida = st.button("❌ Perdida")

datos = sheet.get_all_records()
df = pd.DataFrame(datos)
ultima = df.iloc[-1]

try:
    cuota = float(cuota_real.replace(",", "."))
except:
    cuota = float(ultima["Cuota"])

apuesta_actual = ultima["Apuesta"]
nuevo_bankroll = float(ultima["Bankroll"])

if ganada:
    ganancia = apuesta_actual * (cuota - 1)
    nuevo_bankroll += ganancia
    nueva_apuesta = nuevo_bankroll / 100
    sheet.append_row([nuevo_bankroll, cuota, nueva_apuesta, ganancia, "Ganada"])
    st.success(f"🎯 Ganaste. Nueva apuesta sugerida: {nueva_apuesta:.2f}")

elif perdida:
    nueva_apuesta = apuesta_actual * cuota
    nuevo_bankroll -= apuesta_actual
    sheet.append_row([nuevo_bankroll, cuota, nueva_apuesta, 0, "Perdida"])
    st.error(f"💀 Perdiste. Nueva apuesta sugerida: {nueva_apuesta:.2f}")

# Mostrar bankroll actual
st.divider()
st.subheader("📌 Próxima apuesta sugerida")
ultima_valida = st.session_state.get("ultima_apuesta", apuesta_actual)
st.success(f"🤑 {round(ultima_valida, 2)}")

st.markdown("💼 **Bankroll actual:**")
st.success(f"💰 {round(nuevo_bankroll, 2):,.2f}")
