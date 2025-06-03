import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# Autenticación con Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credenciales = ServiceAccountCredentials.from_json_keyfile_name("apuestas-rentables-457423-f22b0dd2752c.json", scope)
cliente = gspread.authorize(credenciales)
sheet = cliente.open("Control Apuestas Rentables").sheet1

st.set_page_config(page_title="📈 Martingala Reducida", layout="centered")
st.title("📊 Simulador de Martingala Reducida con Rentabilidad")

# Leer datos actuales
data = sheet.get_all_records()
df = pd.DataFrame(data)

if df.empty:
    st.subheader("⚙️ Configura tu Bankroll Inicial")
    bankroll_inicial = st.number_input("Bankroll inicial (COP):", min_value=1000, step=1000)
    if st.button("Guardar configuración inicial"):
        sheet.append_row(["GANADA", "CUOTA", "MONTO", "GANANCIA", "BANKROLL"])
        sheet.append_row(["", "", "", "", bankroll_inicial])
        st.success("✅ Configuración guardada, ya puedes comenzar tus apuestas.")
else:
    st.subheader("🎯 Registrar nueva apuesta")
    estado = st.selectbox("Resultado de la apuesta", ["Ganada", "Perdida"])
    cuota = st.number_input("Cuota usada:", min_value=1.01, step=0.01)
    
    # Leer último bankroll
    try:
        last_row = sheet.get_all_values()[-1]
        bankroll = float(last_row[-1])
    except:
        st.error("❌ No se pudo obtener el bankroll actual.")
        st.stop()

    # Cálculo de monto
    monto_base = bankroll / 100
    historial = sheet.get_all_records()
    apuestas = historial[1:]  # omitir encabezado

    # Revisar si venimos de pérdida
    secuencia = 1
    for fila in reversed(apuestas):
        if fila["GANADA"] == "Perdida":
            secuencia *= 1.8
        else:
            break
    monto = round(monto_base * secuencia, 2)
    st.markdown(f"💰 **Apuesta sugerida:** ${monto:,.0f}")

    if st.button("Registrar Apuesta"):
        ganancia = round((monto * cuota) - monto, 2) if estado == "Ganada" else -monto
        nuevo_bankroll = bankroll + ganancia
        sheet.append_row([estado, cuota, monto, ganancia, nuevo_bankroll])
        st.success("✅ Apuesta registrada correctamente.")
        st.markdown(f"🏦 **Nuevo Bankroll:** ${nuevo_bankroll:,.0f}")
        
        # Mostrar mensaje final
        ultimas = sheet.get_all_records()[2:]  # omitir encabezados
        estados = [x["GANADA"] for x in ultimas]
        if all(e == "Ganada" for e in estados) and len(estados) >= 3:
            st.balloons()
            st.success("🎉 ¡Felicidades! Todas las apuestas han sido ganadas.")
        elif "Perdida" in estados:
            st.error("❌ Una apuesta fue perdida. Reinicia la secuencia.")
