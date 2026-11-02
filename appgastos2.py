import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Control de Gastos", layout="wide")

FILE_GASTOS = "gastos.csv"
FILE_PLANTILLAS = "plantillas.csv"
COLS_GASTOS = ["Fecha", "Centro_Costo", "Categoria", "Tipo", "Monto", "Descripcion"]
COLS_PLANTILLAS = ["Nombre_Plantilla", "Centro_Costo", "Categoria", "Tipo", "Monto", "Descripcion"]

def cargar_datos(archivo, columnas):
    if os.path.exists(archivo):
        return pd.read_csv(archivo)
    return pd.DataFrame(columns=columnas)

def guardar_datos(df, archivo):
    df.to_csv(archivo, index=False)

df_gastos = cargar_datos(FILE_GASTOS, COLS_GASTOS)
df_plantillas = cargar_datos(FILE_PLANTILLAS, COLS_PLANTILLAS)

# Sucursales actualizadas
centros = ["Ciudad Varyna", "Don Samuel", "Dominga Ortiz", "CrediAbby", "Administrativo"]
tipos_fijos = ["Alquiler", "Nómina", "Servicios Públicos", "Suscripciones", "Otros Fijos"]
tipos_variables = ["Papelería", "Mantenimiento", "Viáticos", "Publicidad", "Otros Variables"]

st.title("📊 Registro y Control de Gastos")

tab1, tab2 = st.tabs(["📝 Registrar Gasto", "🔍 Revisar y Filtrar"])

with tab1:
    st.subheader("Nuevo Gasto")
    
    usar_plantilla = st.checkbox("Cargar desde plantilla guardada")
    if usar_plantilla and not df_plantillas.empty:
        plantilla_seleccionada = st.selectbox("Selecciona la plantilla", df_plantillas["Nombre_Plantilla"].tolist())
        datos_p = df_plantillas[df_plantillas["Nombre_Plantilla"] == plantilla_seleccionada].iloc[0]
    else:
        datos_p = None

    with st.form("form_gastos", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            fecha = st.date_input("Fecha del Gasto", value=datetime.today())
            centro_costo = st.selectbox("Sucursal / Departamento", centros, 
                                        index=centros.index(datos_p["Centro_Costo"]) if datos_p is not None else 0)
            categoria = st.selectbox("Categoría", ["Fijo", "Variable"], 
                                     index=0 if datos_p is not None and datos_p["Categoria"] == "Fijo" else 1 if datos_p is not None else 0)
            
            opciones_tipo = tipos_fijos if categoria == "Fijo" else tipos_variables
            
            index_tipo = 0
            if datos_p is not None and datos_p["Tipo"] in opciones_tipo:
                index_tipo = opciones_tipo.index(datos_p["Tipo"])
                
            tipo = st.selectbox("Tipo de Gasto", opciones_tipo, index=index_tipo)

        with col2:
            monto = st.number_input("Monto", min_value=0.0, step=1.0, 
                                    value=float(datos_p["Monto"]) if datos_p is not None else 0.0)
            descripcion = st.text_input("Descripción", 
                                        value=datos_p["Descripcion"] if datos_p is not None else "")
            
            guardar_como_plantilla = st.text_input("Nombre para guardar como plantilla (Opcional)", 
                                                   help="Ejemplo: 'Pago Internet Dominga Ortiz'")

        submit = st.form_submit_button("Registrar Gasto")

        if submit:
            nuevo_gasto = pd.DataFrame([[fecha, centro_costo, categoria, tipo, monto, descripcion]], columns=COLS_GASTOS)
            df_gastos = pd.concat([df_gastos, nuevo_gasto], ignore_index=True)
            guardar_datos(df_gastos, FILE_GASTOS)
            
            if guardar_como_plantilla:
                nueva_plantilla = pd.DataFrame([[guardar_como_plantilla, centro_costo, categoria, tipo, monto, descripcion]], columns=COLS_PLANTILLAS)
                df_plantillas = pd.concat([df_plantillas, nueva_plantilla], ignore_index=True)
                guardar_datos(df_plantillas, FILE_PLANTILLAS)
                
            st.success("Gasto registrado exitosamente.")
            st.rerun()

with tab2:
    st.subheader("Filtros de Búsqueda")
    if df_gastos.empty:
        st.info("No hay gastos registrados aún.")
    else:
        df_gastos["Fecha"] = pd.to_datetime(df_gastos["Fecha"])
        
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            filtro_centro = st.multiselect("Filtrar por Sucursal/Dpto", centros, default=centros)
        with col_f2:
            filtro_categoria = st.multiselect("Filtrar por Categoría", ["Fijo", "Variable"], default=["Fijo", "Variable"])
        with col_f3:
            fecha_inicio = st.date_input("Fecha Inicio", df_gastos["Fecha"].min())
            fecha_fin = st.date_input("Fecha Fin", df_gastos["Fecha"].max())

        mask = (
            (df_gastos["Centro_Costo"].isin(filtro_centro)) &
            (df_gastos["Categoria"].isin(filtro_categoria)) &
            (df_gastos["Fecha"].dt.date >= fecha_inicio) &
            (df_gastos["Fecha"].dt.date <= fecha_fin)
        )
        df_filtrado = df_gastos[mask]

        st.metric(label="Total Gastos (Filtrados)", value=f"${df_filtrado['Monto'].sum():,.2f}")
        st.dataframe(df_filtrado, use_container_width=True)