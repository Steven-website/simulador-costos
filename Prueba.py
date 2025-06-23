#!/usr/bin/env python
# coding: utf-8

# In[3]:


import streamlit as st
import pandas as pd
import requests

# -----------------------------
# CONFIGURACIÓN
# -----------------------------
st.set_page_config(page_title="Simulador por Categoría", layout="centered")
st.title("🧮 Simulador de Costo de Importación (Yuan → Colón)")

# -----------------------------
# CARGA DE DATOS
# -----------------------------
@st.cache_data
def cargar_datos():
    ruta = r"C:\Users\SSEGURA\OneDrive - Almacenes El Rey Alajuela Ltda CSP\02.- Base de información\21.- Historico de Factores de Importación\Simulador.xlsx"
    df = pd.read_excel(ruta)
    df.columns = df.columns.str.strip()
    return df

df = cargar_datos()

# -----------------------------
# OBTENER TIPO DE CAMBIO
# -----------------------------
def obtener_tipo_cambio():
    try:
        url = "https://open.er-api.com/v6/latest/CNY"
        response = requests.get(url, timeout=10)
        data = response.json()
        if data["result"] == "success":
            return data["rates"]["CRC"]
        else:
            return 75.5  # Valor fijo de respaldo
    except:
        return 75.5

tipo_cambio = obtener_tipo_cambio()
st.write(f"💱 Tipo de cambio actual: ¥1 = ₡{tipo_cambio:.2f}")

# -----------------------------
# BOTÓN REFRESCAR PÁGINA
# -----------------------------
if st.button("🔄 Refrescar página"):
    st.cache_data.clear()
    st.experimental_rerun()

# -----------------------------
# FILTROS: PAÍS y FAMILIA
# -----------------------------
st.subheader("Filtros")
pais = st.selectbox("🌍 País", sorted(df["PAIS"].dropna().unique()))
familias = df[df["PAIS"] == pais]["FAMILIA"].dropna().unique()
familia = st.selectbox("🏷️ Familia", sorted(familias))

# -----------------------------
# INGRESO DEL PRECIO EN YUAN
# -----------------------------
precio_yuan = st.number_input("💰 Precio en Yuanes (¥)", min_value=0.0, step=0.01)

# -----------------------------
# CÁLCULO Y TABLA
# -----------------------------
if precio_yuan > 0 and pais and familia:
    resultados = df[(df["PAIS"] == pais) & (df["FAMILIA"] == familia)].copy()
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




