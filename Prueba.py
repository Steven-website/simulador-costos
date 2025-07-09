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
# CARGA DE DATOS DESDE EL ARCHIVO EN GITHUB
# -----------------------------
@st.cache_data
def cargar_datos():
    try:
        df = pd.read_excel("Simulador.xlsx")
        df.columns = df.columns.str.strip()  # Limpia espacios en columnas
        return df
    except Exception as e:
        st.error(f"❌ Error al cargar el archivo Excel: {e}")
        return pd.DataFrame()  # Devuelve DataFrame vacío en caso de error

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
    return 75.5  # Valor por defecto

tipo_cambio = obtener_tipo_cambio()
st.write(f"💱 Tipo de cambio actual: ¥1 = ₡{tipo_cambio:.2f}")

# -----------------------------
# BOTÓN REFRESCAR PÁGINA
# -----------------------------
if st.button("🔄 Refrescar página"):
    st.cache_data.clear()
    st.experimental_rerun()

# -----------------------------
# FILTRO: SOLO FAMILIA (país eliminado)
# -----------------------------
if df.empty:
    st.stop()

st.subheader("Filtro")
familias = df["FAMILIA"].dropna().unique()
familia = st.selectbox("🏷️ Familia", sorted(familias))

# -----------------------------
# INGRESO DEL PRECIO EN YUANES
# -----------------------------
precio_yuan = st.number_input("💰 Precio en Yuanes (¥)", min_value=0.0, step=0.01)

# -----------------------------
# CÁLCULO Y TABLA DE RESULTADOS
# -----------------------------
if precio_yuan > 0 and familia:
    resultados = df[df["FAMILIA"] == familia].copy()
    resultados["Precio Colones"] = precio_yuan * tipo_cambio
    resultados["Precio Final Estimado"] = resultados["Precio Colones"] * resultados["Factor_Importación"]

    st.markdown("### 📊 Resultados por Categoría")
    st.dataframe(
        resultados[["CATEGORIA", "Factor_Importación", "Precio Final Estimado"]]
        .sort_values(by="Precio Final Estimado", ascending=False)
        .rename(columns={
            "CATEGORIA": "Categoría",
            "Factor_Importación": "Factor de Importación",
            "Precio Final Estimado": "₡ Precio Final Estimado"
        }),
        use_container_width=True
    )


# In[ ]:




