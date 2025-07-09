#!/usr/bin/env python
# coding: utf-8

# In[3]:

import streamlit as st
import pandas as pd
import requests

# -----------------------------
# CONFIGURACIÓN DE LA PÁGINA
# -----------------------------
st.set_page_config(page_title="Simulador por Categoría", layout="centered")
st.title("🧮 Simulador de Costo de Importación (Yuan → Colón)")

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
# OBTENER TIPO DE CAMBIO
# -----------------------------
@st.cache_data
def obtener_tipo_cambio():
    try:
        url = "https://open.er-api.com/v6/latest/CNY"
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get("result") == "success":
            return data["rates"]["CRC"]
    except:
        pass
    return 75.5

tipo_cambio = obtener_tipo_cambio()
st.markdown(f"💱 **Tipo de cambio actual:** ¥1 = ₡{tipo_cambio:.2f}")

# -----------------------------
# BOTÓN PARA REINICIAR
# -----------------------------
if st.button("🔄 Volver a empezar"):
    st.markdown(
        '<meta http-equiv="refresh" content="0;URL=\'https://simulador-costos-almacenes-el-rey.streamlit.app/\'" />',
        unsafe_allow_html=True
    )
    st.stop()

# -----------------------------
# FILTRO: FAMILIA
# -----------------------------
if df.empty:
    st.stop()

st.subheader("📦 Filtro Familia")
familias = df["FAMILIA"].dropna().unique()
familia = st.selectbox("🏷️ Selecciona una familia", sorted(familias))

# -----------------------------
# INGRESO DEL PRECIO
# -----------------------------
precio_yuan = st.number_input("💰 Precio en Yuanes (¥)", min_value=0.0, step=0.01)

# -----------------------------
# CÁLCULO Y RESULTADOS
# -----------------------------
if precio_yuan > 0 and familia:
    resultados = df[df["FAMILIA"] == familia].copy()
    resultados["Precio Colones"] = precio_yuan * tipo_cambio
    resultados["Precio Final Estimado"] = resultados["Precio Colones"] * resultados["Factor_Importación"]

    resultados_filtrados = resultados[["CATEGORIA", "Factor_Importación", "Precio Final Estimado"]].copy()
    resultados_filtrados = resultados_filtrados.rename(columns={
        "CATEGORIA": "Categoría",
        "Factor_Importación": "Factor",
        "Precio Final Estimado": "₡ Costo CRC"
    })

    st.markdown("### 📊 Resultados por Categoría")
    st.dataframe(resultados_filtrados.sort_values(by="₡ Costo CRC", ascending=False), use_container_width=True)

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




