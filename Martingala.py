import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# Autenticación con Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credenciales = ServiceAccountCredentials.from_json_keyfile_dict(
    st.secrets["GOOGLE_CREDENTIALS"], scope
)
cliente = gspread.authorize(credenciales)
hoja = cliente.open("Control Apuestas Rentables").sheet1

# Configuración de página
st.set_page_config(page_title="📈 Martingala Reducida", layout="centered")
st.title("🎯 Seguimiento con Martingala Reducida")

# Leer datos
datos = hoja.get_all_records()

if not datos:
    st.subheader("⚙️ Configuración Inicial")
    bankroll_inicial = st.number_input("Bankroll Inicial (COP)", min_value=10000, step=1000)
    cuota_base = st.number_input("Cuota Promedio", min_value=1.01, step=0.01, value=1.8)
    
    if st.button("Guardar configuración inicial"):
        hoja.append_row(["Inicial", bankroll_inicial, cuota_base, "", "", "", ""])
        st.success("✅ Configuración guardada. Puedes comenzar a registrar tus apuestas.")
        st.stop()

else:
    df = pd.DataFrame(datos)
    df.columns = ["Tipo", "Bankroll", "Cuota", "Monto", "Ganancia", "Resultado", "Comentario"]
    df = df[df["Tipo"] != "Inicial"]
    
    config = pd.DataFrame(datos)
    config.columns = ["Tipo", "Bankroll", "Cuota", "Monto", "Ganancia", "Resultado", "Comentario"]
    bankroll_actual = float(config.iloc[0]["Bankroll"])
    cuota_base = float(config.iloc[0]["Cuota"])
    
    st.markdown(f"### 💰 Bankroll actual: `{bankroll_actual:,.0f}` COP")
    
    unidad = bankroll_actual / 100
    st.markdown(f"🔹 Unidad base: `{unidad:,.0f}` COP")
    
    # Calcular número de derrotas seguidas
    perdidas_seguidas = 0
    for res in reversed(df["Resultado"]):
        if res == "PERDIDA":
            perdidas_seguidas += 1
        else:
            break

    # Calcular próxima apuesta
    proxima_apuesta = round(unidad * (1.8 ** perdidas_seguidas), 0)
    st.markdown(f"📌 Próxima Apuesta sugerida: `{proxima_apuesta:,.0f}` COP (Tras {perdidas_seguidas} pérdida(s) consecutiva(s))")
    
    st.subheader("🎲 Registrar Apuesta")
    resultado = st.radio("Resultado de la apuesta anterior:", ["GANADA", "PERDIDA"])
    cuota = st.number_input("Cuota utilizada", min_value=1.01, step=0.01, value=cuota_base)
    comentario = st.text_input("Comentario opcional")
    
    if st.button("Registrar"):
        ganancia = 0
        if resultado == "GANADA":
            ganancia = round(proxima_apuesta * (cuota - 1), 0)
        else:
            ganancia = -proxima_apuesta

        nuevo_bankroll = bankroll_actual + ganancia

        hoja.append_row(["Apuesta", nuevo_bankroll, cuota, proxima_apuesta, ganancia, resultado, comentario])
        st.success(f"✅ Apuesta registrada. Nuevo bankroll: `{nuevo_bankroll:,.0f}` COP")
        st.experimental_rerun()
