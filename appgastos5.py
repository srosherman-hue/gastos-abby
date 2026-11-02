import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Control de Gastos", layout="wide")

FILE_GASTOS = "gastos.csv"
COLS_GASTOS = ["Fecha", "Centro_Costo", "Categoria", "Tipo", "Monto", "Descripcion"]

def cargar_datos(archivo, columnas):
    if os.path.exists(archivo):
        return pd.read_csv(archivo)
    return pd.DataFrame(columns=columnas)

def guardar_datos(df, archivo):
    df.to_csv(archivo, index=False)

df_gastos = cargar_datos(FILE_GASTOS, COLS_GASTOS)

# Sucursales
centros = ["Ciudad Varyna", "Don Samuel", "Dominga Ortiz", "CrediAbby", "Administrativo"]

# Listas de gastos
tipos_fijos = [
    "Contabilidad", "Internet y Telefonia", "Electricidad", "Agua", 
    "Aseo", "Gasolina", "Gasoy", "Gastos Fiscales", 
    "Gastos Parafiscales", "Alquiler de local"
]

tipos_variables = [
    "Mantenimiento de equipo", "Mantenimiento Camiones", "Mantenimiento de Motos", 
    "Muebles y equipo de oficina", "Bolsas y Envases", "Bandejas y Emboplast (CHAR.)", 
    "Papeleria", "Mantenimiento de Local", "ARTICULOS DE LIMPIEZA", "Café", 
    "Otros Gastos", "Publicidad", "Flet", "Uniformes"
]

st.title("📊 Registro y Control de Gastos")

tab1, tab2 = st.tabs(["📝 Registrar Gasto", "🔍 Revisar y Filtrar"])

# --- PESTAÑA 1: REGISTRO ---
with tab1:
    st.subheader("Nuevo Gasto")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fecha = st.date_input("Fecha del Gasto", value=datetime.today())
        centro_costo = st.selectbox("Sucursal / Departamento", centros)
        categoria = st.selectbox("Categoría", ["Fijo", "Variable"])
        
        opciones_tipo = tipos_fijos if categoria == "Fijo" else tipos_variables
        tipo = st.selectbox("Tipo de Gasto", opciones_tipo)

    with col2:
        monto = st.number_input("Monto", min_value=0.0, step=1.0, value=0.0)
        descripcion = st.text_input("Descripción", value="")
        
    if st.button("Registrar Gasto"):
        nuevo_gasto = pd.DataFrame([[fecha, centro_costo, categoria, tipo, monto, descripcion]], columns=COLS_GASTOS)
        df_gastos = pd.concat([df_gastos, nuevo_gasto], ignore_index=True)
        guardar_datos(df_gastos, FILE_GASTOS)
            
        st.success("Gasto registrado exitosamente.")
        st.rerun()

# --- PESTAÑA 2: FILTROS Y REVISIÓN ---
with tab2:
    st.subheader("Filtros de Búsqueda")
    if df_gastos.empty:
        st.info("No hay gastos registrados aún.")
    else:
        df_gastos["Fecha"] = pd.to_datetime(df_gastos["Fecha"])
        
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        with col_f1:
            filtro_centro = st.multiselect("Filtrar por Sucursal", centros, default=centros)
        with col_f2:
            filtro_categoria = st.multiselect("Filtrar por Categoría", ["Fijo", "Variable"], default=["Fijo", "Variable"])
        with col_f3:
            tipos_disponibles = df_gastos["Tipo"].unique().tolist()
            filtro_tipo = st.multiselect("Filtrar por Tipo", tipos_disponibles, default=tipos_disponibles)
        with col_f4:
            fecha_inicio = st.date_input("Fecha Inicio", df_gastos["Fecha"].min())
            fecha_fin = st.date_input("Fecha Fin", df_gastos["Fecha"].max())

        # Aplicar filtros
        mask = (
            (df_gastos["Centro_Costo"].isin(filtro_centro)) &
            (df_gastos["Categoria"].isin(filtro_categoria)) &
            (df_gastos["Tipo"].isin(filtro_tipo)) &
            (df_gastos["Fecha"].dt.date >= fecha_inicio) &
            (df_gastos["Fecha"].dt.date <= fecha_fin)
        )
        df_filtrado = df_gastos[mask]

        st.metric(label="Total Gastos (Filtrados)", value=f"${df_filtrado['Monto'].sum():,.2f}")
        st.dataframe(df_filtrado, use_container_width=True)

        st.divider()
        st.subheader("🗑️ Eliminar un registro")
        if not df_filtrado.empty:
            opciones_borrar = df_filtrado.index.tolist()
            gasto_borrar = st.selectbox(
                "Selecciona el gasto que deseas eliminar:", 
                opciones_borrar, 
                format_func=lambda x: f"{df_filtrado.loc[x, 'Fecha'].strftime('%Y-%m-%d')} | {df_filtrado.loc[x, 'Centro_Costo']} | {df_filtrado.loc[x, 'Tipo']} | ${df_filtrado.loc[x, 'Monto']} | {df_filtrado.loc[x, 'Descripcion']}"
            )
            if st.button("Eliminar Gasto Seleccionado"):
                df_gastos = df_gastos.drop(index=gasto_borrar)
                guardar_datos(df_gastos, FILE_GASTOS)
                st.success("Gasto eliminado exitosamente.")
                st.rerun()