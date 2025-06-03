import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# Conexión a Google Sheets
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
CREDS = Credentials.from_service_account_file(
    "apuestas-rentables-457423-f22b0dd2752c.json", scopes=SCOPES
)
client = gspread.authorize(CREDS)
sheet = client.open("Control Apuestas Rentables").sheet1

# Configurar Streamlit
st.set_page_config(page_title="Simulador Martingala", layout="centered")
st.title("📈 Simulador de Apuesta con\nMartingala Reducida")

# Leer hoja de cálculo
datos = sheet.get_all_records()
df = pd.DataFrame(datos)

# Configuración inicial
st.subheader("🎰 Configuración inicial")
if df.empty:
    bankroll = st.number_input("💰 Ingrese su bankroll inicial:", min_value=1000, value=200000)
    cuota = st.number_input("🎯 Cuota promedio:", min_value=1.01, max_value=5.0, value=1.80, step=0.01, format="%.2f")

    if st.button("Guardar configuración inicial"):
        apuesta_inicial = round(bankroll / 100, 2)
        sheet.append_row(["Bankroll", "Cuota", "Apuesta", "Ganancia", "Resultado"])  # encabezado
        sheet.append_row([bankroll, cuota, apuesta_inicial, 0, "Inicio"])
        st.success(f"✅ Primera apuesta sugerida: {apuesta_inicial}")
        st.session_state["ultima_apuesta"] = apuesta_inicial

else:
    st.divider()
    st.subheader("🔁 ¿Cómo terminó la última apuesta?")
    ultima = df.iloc[-1]
    try:
        bankroll = float(str(ultima["Bankroll"]).replace(",", "."))
        apuesta = float(str(ultima["Apuesta"]).replace(",", "."))
    except ValueError:
        st.error("❌ Error al leer datos. Revisa tu hoja.")
        st.stop()

    cuota_input = st.number_input("📌 Ingresa la cuota real de esta apuesta:", min_value=1.01, max_value=5.0, value=1.80, step=0.01, format="%.2f")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Ganada"):
            ganancia = round(apuesta * (cuota_input - 1), 2)
            nuevo_bankroll = round(bankroll + ganancia, 2)
            nueva_apuesta = round(nuevo_bankroll / 100, 2)
            sheet.append_row([
                nuevo_bankroll,
                cuota_input,
                nueva_apuesta,
                ganancia,
                "Ganada"
            ])
            st.session_state["ultima_apuesta"] = nueva_apuesta
            st.success(f"🎉 Ganaste. Nueva apuesta sugerida: {nueva_apuesta}")

    with col2:
        if st.button("❌ Perdida"):
            nuevo_bankroll = round(bankroll - apuesta, 2)
            nueva_apuesta = round(apuesta * 1.8, 2)
            sheet.append_row([
                nuevo_bankroll,
                cuota_input,
                nueva_apuesta,
                0,
                "Perdida"
            ])
            st.session_state["ultima_apuesta"] = nueva_apuesta
            st.error(f"💥 Perdiste. Nueva apuesta sugerida: {nueva_apuesta}")

# Mostrar última apuesta sugerida
st.divider()
st.subheader("📌 Próxima apuesta sugerida")
ultima_valida = st.session_state.get("ultima_apuesta", apuesta)
st.markdown(f"""
<div style='background-color:#111;padding:1rem;border-radius:8px;border:1px solid #444;'>
<span style='font-size:24px;color:#0f0;'>💵 {ultima_valida:.2f}</span>
</div>
""", unsafe_allow_html=True)
