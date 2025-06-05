import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

st.set_page_config(page_title="Simulador Martingala", layout="centered")
st.title("📈 Simulador de Apuesta con\nMartingala Reducida")

# ---------------------- AUTENTICACIÓN GOOGLE ---------------------- #
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credenciales = ServiceAccountCredentials.from_json_keyfile_dict(
    st.secrets["GOOGLE_CREDENTIALS"], scope
)
cliente = gspread.authorize(credenciales)
spreadsheet = cliente.open("Control Apuestas Rentables")
sheet = spreadsheet.sheet1

# ---------------------- FUNCIONES ---------------------- #
def calcular_apuesta_siguiente(df):
    if df.empty:
        return 0
    ultima = df.iloc[-1]
    resultado = ultima["Resultado"]
    cuota = float(ultima["Cuota"])
    ultima_apuesta = float(ultima["Apuesta"])
    bankroll = float(ultima["Bankroll"])
    if resultado == "Ganada":
        nueva_apuesta = bankroll / 100
    else:
        nueva_apuesta = ultima_apuesta * cuota
    return round(nueva_apuesta, 2)

def calcular_winrate(df):
    ganadas = df[df["Resultado"] == "Ganada"].shape[0]
    perdidas = df[df["Resultado"] == "Perdida"].shape[0]
    total = ganadas + perdidas
    return round((ganadas / total) * 100, 2) if total > 0 else 0

def calcular_rentabilidad(df):
    if df.empty or df.shape[0] < 2:
        return 0
    inicial = float(df.iloc[1]["Bankroll"])
    final = float(df.iloc[-1]["Bankroll"])
    return round(((final - inicial) / inicial) * 100, 2)

# ---------------------- CONFIGURACIÓN INICIAL ---------------------- #
st.subheader("🎰 Configuración inicial")
with st.form("config"):
    bankroll_inicial = st.number_input("💰 Ingrese su bankroll inicial:", value=200000)
    cuota_promedio = st.number_input("🎯 Cuota promedio:", value=1.80, format="%.2f")
    enviado = st.form_submit_button("Guardar configuración inicial")

if enviado:
    primera_apuesta = round(bankroll_inicial / 100, 2)
    sheet.clear()
    sheet.append_row(["Bankroll", "Cuota", "Apuesta", "Ganancia", "Resultado"])
    sheet.append_row([str(bankroll_inicial), str(cuota_promedio), str(primera_apuesta), "0", "Inicio"])
    st.success(f"✅ Primera apuesta sugerida: {primera_apuesta}")

# ---------------------- REGISTRAR RESULTADO ---------------------- #
st.markdown("---")
st.subheader("🔄 ¿Cómo terminó la última apuesta?")
cuota_real = st.text_input("📌 Ingresa la cuota real de esta apuesta:", value="1.80")
col1, col2 = st.columns(2)
resultado = None
with col1:
    if st.button("✅ Ganada"):
        resultado = "Ganada"
with col2:
    if st.button("❌ Perdida"):
        resultado = "Perdida"

if resultado:
    df = pd.DataFrame(sheet.get_all_records())
    if not df.empty:
        ultima = df.iloc[-1]
        apuesta = float(ultima["Apuesta"])
        cuota = float(cuota_real)
        bankroll = float(ultima["Bankroll"])
        if resultado == "Ganada":
            ganancia = round(apuesta * (cuota - 1), 2)
            nuevo_bankroll = bankroll + ganancia
        else:
            ganancia = 0
            nuevo_bankroll = bankroll - apuesta
        nueva_apuesta = round(nuevo_bankroll / 100, 2) if resultado == "Ganada" else round(apuesta * cuota, 2)
        nueva_fila = [str(nuevo_bankroll), str(cuota), str(nueva_apuesta), str(ganancia), resultado]
        sheet.append_row(nueva_fila)
        st.success(f"🎯 {resultado}. Nueva apuesta sugerida: {nueva_apuesta}")

# ---------------------- MOSTRAR DATOS ---------------------- #
st.markdown("---")
st.subheader("📌 Próxima apuesta sugerida y resumen")

try:
    df = pd.DataFrame(sheet.get_all_records())
    apuesta_actual = calcular_apuesta_siguiente(df)
    bankroll_actual = float(df.iloc[-1]["Bankroll"])
    winrate = calcular_winrate(df)
    rentabilidad = calcular_rentabilidad(df)

    st.markdown(
        f"""
        <div style='background-color:#013220;padding:10px;border-radius:10px;margin-bottom:10px;'>
            <span style='color:#39FF14;font-size:24px;'>💵 Apuesta sugerida: {apuesta_actual}</span>
        </div>
        <div style='background-color:#262730;padding:10px;border-radius:10px;margin-bottom:10px;'>
            <span style='color:#ffffff;font-size:18px;'>💼 Bankroll actual: <strong>{bankroll_actual:,.2f}</strong></span>
        </div>
        <div style='background-color:#1a1a1a;padding:10px;border-radius:10px;'>
            <span style='color:#00d4ff;font-size:16px;'>📊 Winrate: <strong>{winrate}%</strong></span><br>
            <span style='color:#ffa500;font-size:16px;'>📈 Rentabilidad: <strong>{rentabilidad}%</strong></span>
        </div>
        """,
        unsafe_allow_html=True
    )

except Exception as e:
    st.warning("⚠️ No se puede calcular la siguiente apuesta aún.")
