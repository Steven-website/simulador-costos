#!/usr/bin/env python
# coding: utf-8

# In[3]:
import streamlit as st
import pandas as pd
import requests

# -----------------------------
# CONFIGURACIÓN DE LA PÁGINA
# -----------------------------
st.set_page_config(page_title="Simulador de Costos", layout="centered")

# -----------------------------
# ENCABEZADO
# -----------------------------
st.markdown("""
<div style='text-align: center; padding-top: 10px;'>
    <h1 style='font-size: 2.2em;'>🧮<br>Simulador de Costo de Importación<br><span style="font-size: 0.9em;">(Yuan → Colón / Dólar)</span></h1>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# CARGA DE DATOS
# -----------------------------
@st.cache_data
def cargar_datos():
    try:
        df = pd.read_excel("Simulador.xlsx")
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"❌ Error al cargar el archivo Excel: {e}")
        return pd.DataFrame()

df = cargar_datos()

# -----------------------------
# TIPO DE CAMBIO
# -----------------------------
@st.cache_data
def obtener_tipos_cambio():
    try:
        url = "https://open.er-api.com/v6/latest/CNY"
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get("result") == "success":
            return data["rates"]["CRC"], data["rates"]["USD"]
    except:
        pass
    return 75.5, 0.14  # Valores por defecto

tipo_cambio_crc, tipo_cambio_usd = obtener_tipos_cambio()

# -----------------------------
# TARJETA DE TIPO DE CAMBIO
# -----------------------------
st.markdown(f"""
<div style="background-color: #f0f2f6; padding: 10px 15px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
    <span style='font-size: 18px;'>💱 <strong>Tipo de cambio:</strong> ¥1 = ₡{tipo_cambio_crc:.2f} | ${tipo_cambio_usd:.4f}</span>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# BOTÓN DE REINICIO
# -----------------------------
st.markdown("""
<div style='text-align: center; margin-bottom: 30px;'>
    <a href='https://simulador-costos-almacenes-el-rey.streamlit.app/' target='_self'>
        <button style='background-color: #e1ecf4; border: none; color: #0366d6; padding: 10px 20px;
                        text-align: center; font-size: 16px; border-radius: 10px; cursor: pointer;'>
            🔄 Reiniciar simulador
        </button>
    </a>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# FILTRO FAMILIA
# -----------------------------
if df.empty:
    st.stop()

st.subheader("📦 Filtro Familia")
familias = df["FAMILIA"].dropna().unique()
familia = st.selectbox("🏷️ Selecciona una familia", sorted(familias))

# -----------------------------
# PRECIO EN YUANES
# -----------------------------
precio_yuan = st.number_input("💰 Precio en Yuanes (¥)", min_value=0.0, step=0.01)

# -----------------------------
# CÁLCULO Y RESULTADOS
# -----------------------------
if precio_yuan > 0 and familia:
    resultados = df[df["FAMILIA"] == familia].copy()

    # Cálculos base
    resultados["$ Costo CN"] = precio_yuan * tipo_cambio_usd
    resultados["$ Costo CR"] = resultados["$ Costo CN"] * resultados["Factor_Importación"]
    resultados["₡ Costo CR"] = precio_yuan * tipo_cambio_crc * resultados["Factor_Importación"]

    if "Margen" in resultados.columns:
        resultados["₡ Precio CR"] = resultados["₡ Costo CR"] * (1 + resultados["Margen"])
    else:
        resultados["₡ Precio CR"] = resultados["₡ Costo CR"]

    # Formateo
    resultados["$ Costo CN"] = resultados["$ Costo CN"].apply(lambda x: f"${x:,.2f}")
    resultados["$ Costo CR"] = resultados["$ Costo CR"].apply(lambda x: f"${x:,.2f}")
    resultados["₡ Costo CR"] = resultados["₡ Costo CR"].apply(lambda x: f"₡{x:,.2f}")
    resultados["₡ Precio CR"] = resultados["₡ Precio CR"].apply(lambda x: f"₡{x:,.2f}")

    # Tabla final
    resultados_filtrados = resultados[[
        "CATEGORIA",
        "$ Costo CN",
        "$ Costo CR",
        "₡ Costo CR",
        "₡ Precio CR"
    ]].copy()

    resultados_filtrados = resultados_filtrados.rename(columns={
        "CATEGORIA": "Categoría"
    })

    st.markdown("### 📊 Resultados por Categoría")
    st.dataframe(resultados_filtrados, use_container_width=True)

# -----------------------------
# ESTILOS PARA CELULAR
# -----------------------------
st.markdown("""
<style>
    html, body, [class*="css"]  {
        font-size: 16px;
        padding: 0px;
        margin: 0px;
    }
    input, select {
        font-size: 18px !important;
    }
    .stButton button {
        width: 100%;
        font-size: 18px;
    }
    .stDataFrame div {
        font-size: 14px !important;
    }
</style>
""", unsafe_allow_html=True)

# In[ ]:




