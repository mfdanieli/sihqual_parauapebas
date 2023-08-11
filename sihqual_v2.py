#!/usr/bin/env python
# coding: utf-8

# ******************
# Importando bibliotecas

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import geopandas as gpd
import streamlit as st
import time
import matplotlib.pyplot as plt

st.set_page_config(page_title='Metais no Rio Parauapebas',page_icon=' ', layout='wide')

# ****************** 
# Coordenadas ptos simulados

coord_cheia = pd.read_excel('df_coord_cheia.xlsx')
coord_seca = pd.read_excel('df_coord_seca.xlsx')

# ****************** 
# Função leitura dados e SihQual

def sihqual(period, metal,factor_load):

    if period == 'Estiagem':
        folder_path = "input_app_seca"
        dt = 50.
        dx = 100.
        J = 1075 
        N = 25921
    else:
        folder_path = "input_app_cheia"
        dt = 10.
        dx = 30.
        J = 3582
        N = 129601
        
    file_name = f'velocidade_1_{metal}.txt'
    file_path = os.path.join(folder_path, file_name)
    with open(file_path, 'r') as file:
        lines = file.readlines()        # Read all lines into a list
        velocidade = ''.join(lines[1:]) # Skip the first line 
        velocidade = np.fromstring(velocidade, sep=' ')  # Convert to NumPy array
    file_name = f'contorno_1_{metal}.txt'
    file_path = os.path.join(folder_path, file_name)
    with open(file_path, 'r') as file:
        contorno = file.read()
        contorno = np.fromstring(contorno, sep=' ') 
    file_name = f'carga_1_{metal}.txt'
    file_path = os.path.join(folder_path, file_name)
    with open(file_path, 'r') as file:
        lines = file.readlines()        
        carga = ''.join(lines[1:])
        carga = np.fromstring(carga, sep=' ') 
    file_name = f'area_1_{metal}.txt'
    file_path = os.path.join(folder_path, file_name)
    with open(file_path, 'r') as file:
        lines = file.readlines()        
        area = ''.join(lines[1:])
        area = np.fromstring(area, sep=' ') 
    file_name = f'REACAO_1_{metal}.txt'
    file_path = os.path.join(folder_path, file_name)
    with open(file_path, 'r') as file:
        lines = file.readlines()        
        REACAO = ''.join(lines[1:])
        REACAO = np.fromstring(REACAO, sep=' ') 

    DD = 30.
    A = area
    v = velocidade
    cq = carga*factor_load
    
    # Initialize the concentration array with zeros
    c = np.zeros((N, J))
    
    # Set initial and boundary conditions
    c[0, :] = contorno[0] # np.full(J,contorno[0])
    c[:, 0] = contorno
    
    # Precompute constants outside the loop
    dx2 = dx**2
    v_dt_2dx = (dt / (2 * dx)) * v
    DD_dt = DD * dt
    
    for k in range(0, N-1):
        c[k+1, 1:J-1] = c[k, 1:J-1] - (dt / (2 * dx)) * v[1:J-1] * (c[k, 2:J] - c[k, 0:J-2]) + \
                        (DD_dt / A[1:J-1]) * (A[2:J] - A[0:J-2]) / (2 * dx) * (c[k, 2:J] - c[k, 0:J-2]) / (2 * dx) + \
                        (DD_dt / dx2) * (c[k, 2:J] - 2 * c[k, 1:J-1] + c[k, 0:J-2]) - \
                        REACAO[1:J-1] * dt * c[k, 1:J-1] + cq[1:J-1] * dt
    
    return c[:,:]*1000 # kg/m3 to mg/L

# ****************** 

# criar abas
tab1,tab2 = st.tabs(['❗️Informações gerais','📊 Simulações'])

# ****************** 
# Função para receber dados do usuário 

with tab1: 
    with st.container(): 
        st.markdown('### Sobre a ferramenta:')
        st.markdown('###### Nessa página é possível simular a distribuição de até 19 metais ao longo do Rio Parauapebas, PA. Ao usuário é permitido alterar por um fator a carga de metais que atinge o rio ao longo do seu curso, assim como escolher quais metais de interesse e o período de simulação (estiagem ou chuvoso) - note que a simulação do período chuvoso pode ser significativamente mais lenta, devido aos requerimentos da solução numérica.')
        st.markdown('###### O aplicativo é um protótipo com base em pesquisa  desenvolvida no Instituto Tecnológico Vale. Informações sobre os dados, modelagem e hipóteses do estudo podem ser encontrados em: ["Modeling transport and fate of metals for risk assessment in the Parauapebas river"](https://www.sciencedirect.com/science/article/abs/pii/S0195925523001750).')
        st.markdown('###### Contato para mais informações: danieli.ferreira@pq.itv.org')

with tab2: 
    with st.container(): 
        def input_data():

            factor_load = st.sidebar.slider('Fator de alteração da carga afluente ao rio:', 0.1, 10.0, 1.0)

            # Metal name to number mapping
            metal_mapping = {
                'Ferro': 1,
                'Manganes': 2,
                'Aluminio': 3,
                'Calcio': 4,
                'Magnesio': 5,
                'Potassio': 6,
                'Sodio': 7,
                'Bario': 8,
                'Boro': 9,
                'Cobre': 10,
                'Cromo': 11,
                'Niquel': 12,
                'Vanadio': 13,
                'Zinco': 14,
                'Estanho': 15,
                'Cobalto': 16,
                'Estroncio': 17,
                'Rubidio': 18,
                'Titanio': 19,
            }
            
            season_options = ['Estiagem','Chuvoso']

            period = st.sidebar.selectbox('Selecione um período:', options=season_options)
                
            metal_names = st.sidebar.multiselect(
            'Selecione metais para simular:',     ['Ferro','Manganes','Aluminio','Calcio','Magnesio','Potassio','Sodio','Bario','Boro','Cobre','Cromo','Niquel','Vanadio','Zinco','Estanho','Cobalto','Estroncio','Rubidio','Titanio'],
            default = ['Ferro','Manganes','Aluminio'])

            metal_numbers = [metal_mapping[name] for name in metal_names]

            # um dicionário recebe as informações acima
            user_data = {'period': period, 
                         'metal': metal_numbers, 
                         }

            # Save the selected data to session_state
            st.session_state.period = period
            st.session_state.metal_names = metal_names

            # # Display the selected data
            # st.write("Selected Period:", st.session_state.period)
            # st.write("Selected Metal Names:", st.session_state.metal_names)

            # Add "Run Simulation" button
            for metal_name in metal_names:
                metal_number = metal_mapping[metal_name]
                st.write(f"{metal_name}:")

                # Call the sihqual function with the selected period and metal number
                start_time = time.time()
                result = sihqual(period, metal_number, factor_load)
                elapsed_time = time.time() - start_time

                # Call the sihqual function with the selected period and metal number
                result = sihqual(period, metal_number,factor_load)

                # Display a progress bar
                with st.spinner(f"Simulando {metal_name}..."):
                    progress_bar = st.progress(0)
                    for progress in range(101):
                        time.sleep(elapsed_time / 100)  # Adjust sleep time to control the progress speed
                        progress_bar.progress(progress)

                # st.success(f"Simulation for {metal_name} completed!")

                # st.write(f"Simulation Result for {metal_name}:")
                df = pd.DataFrame(result)

                # instante a imprimir
                if period == 'Estiagem':
                    instante_impressao = 25920
                else:
                    instante_impressao = 129600
                df1 = df.iloc[int(instante_impressao),:]

                # juntando o resultado com coord dos pontos
                if period == 'Estiagem':
                    df_coord = coord_seca
                else:
                    df_coord = coord_cheia.drop(coord_cheia.index[-1])
                col1, col2 = st.columns([1, 2])

                with col1:
                    st.markdown('##### ')

                with col2:


                    fig, ax = plt.subplots(figsize=(2, 3))
                    scatter = ax.scatter(df_coord['X'], df_coord['Y'], c=df1, cmap='magma',s=5)
                    ax.set_xlabel('X')
                    ax.set_ylabel('Y')
                    plt.colorbar(scatter, ax=ax, label='Concentration (mg/L)')
                    # Use CSS styling to decrease font size for plot labels
                    ax.xaxis.label.set_size(12)
                    ax.yaxis.label.set_size(12)
                    ax.xaxis.set_tick_params(labelsize=10)
                    ax.yaxis.set_tick_params(labelsize=10)
                    st.pyplot(fig)

    # chamando a funcao input_data
    user_input_variables = input_data()

# ****************** 

