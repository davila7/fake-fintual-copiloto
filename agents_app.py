import streamlit as st
import time
import requests
import json
import os
from PIL import Image
from dotenv import load_dotenv
load_dotenv()
from llamaapi import LlamaAPI
import asyncio
from pydantic import BaseModel
from typing import List
import matplotlib.pyplot as plt
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
import time
import pandas as pd
from pandasai import PandasAI
from judini.codegpt.agent import Agent

#Judini
judini_api_key= os.getenv("JUDINI_API_KEY")
agent_unificador_id= "ff98f267-93a3-4201-9886-1aca85f854fb"
 # os.getenv("JUDINI_AGENT_ID")
url = 'https://playground.judini.ai/api/v1/agent/'+agent_unificador_id
headers = {"Content-Type": "application/json; charset=utf-8", "Authorization": "Bearer "+judini_api_key}

def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

class FunctionCallArguments(BaseModel):
    fondo_name: str
    date_from: str
    date_to: str

class FunctionCall(BaseModel):
    name: str
    arguments: FunctionCallArguments

class Message(BaseModel):
    function_call: FunctionCall

class Choice(BaseModel):
    message: Message

class ChoiceList(BaseModel):
    choices: List[Choice]

def api_fintual(fondo, from_date, to_date):
    """ id, from_date, to_date """
    id=15077
    if fondo == "Very Conservative Streep":
        id = 15077
    if fondo == "Conservative Clooney":
        id = 188
    if fondo == "Moderate Pit":
        id = 187
    if fondo == "Risky Norris":
        id = 186

    url_fintual = 'https://fintual.cl/api/real_assets/'+str(id)+'/days?from_date='+from_date+'&to_date='+to_date

    response = requests.get(url_fintual)
    json_response = response.json()

    dates = [item["attributes"]["date"] for item in json_response["data"]]
    prices = [item["attributes"]["price"] for item in json_response["data"]]
    # return an array
    return dates, prices

# Define your API request
def run_llama_api(prompt):
    # Initialize the llamaapi with your api_token
    llama = LlamaAPI(os.getenv("LLAMA_API_API_KEY"))
    function_calling_json = [
            {
                "name": "get_fondo_data",
                "description": "útil cuando un usuario quiere preguntar sobre fondos de desde un rango específico",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "fondo_name": {
                            "type": "string",
                            "description": "nombre del fondo",
                        },
                        "date_from": {
                            "type": "string",
                            "description":"Fecha desde cuando se quiere consultar"
                        },
                        "date_to": {
                            "type": "string",
                            "description":"Fecha hasta cuando se quiere consultar"
                        },
                    },
                },
            }
        ]

    api_request_json = {
    "messages": [
        {"role": "user", "content": prompt},
    ],
    "functions": function_calling_json,
    "stream": False,
    "function_call": "get_fondo_data"
    }

    # Make your request and handle the response
    response = llama.run(api_request_json)
    message = response.json()
    #st.write(message)
    has_function_callings = False
    # Step 2, check if the model wants to call a function
    if message['choices'][0]['message']['function_call']:
        function_name = message['choices'][0]['message']['function_call']["name"]
        #st.write(function_name)
        if(function_name == 'get_fondo_data'):
            has_function_callings = True
            # Access the arguments
            model = ChoiceList(**message)
            arguments = model.choices[0].message.function_call.arguments
            #st.write(arguments)
    date_to = ''
    date_from = ''
    fondo = ''
    if has_function_callings:
        #obtener el dato dates and prices de la variable function_response
        date_to = arguments.date_to
        date_from = arguments.date_from
        fondo = arguments.fondo_name
    return date_to, date_from, fondo
        

st.set_page_config(layout="centered")  

image = Image.open('fake-fintual-copiloto.png')
st.image(image, width=50)
st.title("Fake Fintual Copiloto 🤖")
st.write("Preguntame cualquier cosa sobre los fondos de fintual... pero una advertencia ⚠️ Soy la versión Fake!")
st.markdown('Creado por <a href="https://www.linkedin.com/in/daniel-avila-arias/">Daniel San</a> con <a href="https://judini.ai/">Judini</a>', unsafe_allow_html=True)
st.markdown('---')
# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt := st.chat_input("En que te puedo ayudar?"):
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.spinner('Consultando a la base de agentes disponibles...'):
        agent_clasificador = Agent(judini_api_key, "8060a9ec-b87f-42ab-822e-3e2352077567")
        response = agent_clasificador.completion(prompt)

    #valida que response sea un json
    agent_flow = False
    try:
        data_dict = json.loads(response)
        agent_flow = True
    except json.JSONDecodeError:
        data_dict = {}

    array_response = []
    st.write(data_dict)
    for fondo in data_dict:
        # encontró un agente! nos ponemos a buscar la respuesta con este agente
        if 'agent_id' in fondo:
            with st.spinner('Consultando al agente experto '+fondo['name']+'...'):
                agent_id = fondo['agent_id']
                _question = fondo['question']
                _agent = Agent(judini_api_key, agent_id)
                _response = _agent.completion(_question)
                #guarda la respuesta del agente en agents_response
                array_response.append(_response)
        else:
            print("agent_id not found")

    # pasa todo el array agents_response a un string separado por un salto de linea
    agents_response = '\n'.join(array_response)
    
    st.write(agents_response)
    prompt_template_unificador = PromptTemplate(
        input_variables=["prompt", "agents_response"],
        template='''
        Question:{prompt}
        Responde en base a este contexto:
        {agents_response}
        '''
    )
    prompt_template_unificador.format(prompt=prompt, agents_response=agents_response)

    full_response = ""
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        prompt_data_fintual = ''
        message_placeholder = st.empty()
        if False:
            with st.spinner('Iré a buscar los datos a fintual...'):
                data_arguments = run_llama_api(prompt=prompt)
            date_to = data_arguments[0]
            date_from = data_arguments[1]
            fondo = data_arguments[2]
            
            # llamo a fintual y pinto el gráfico
            # pregunto si debo llamar a la api de fintual

            date_price = api_fintual(
                fondo, date_from, date_to
            )
            # parar la ejecución del código por 5 segundos
            with st.spinner('Datos obtenidos, ahora los graficaré...'):
                time.sleep(5)
            
            dates = date_price[0]
            prices = date_price[1]

            plt.figure(figsize=(10,5))
            plt.bar(dates, prices, color = 'blue')

            plt.xlabel('Fecha')
            plt.ylabel('Precio')
            plt.title('Precio por Fecha')
            plt.xticks(rotation=90) 
            st.pyplot(plt)

            prompt_data_fintual = PromptTemplate(
                input_variables=["prompt", "fondo", "dates", "prices"],
                template='''
                    {prompt}
                    Basate en los siguientes datos:
                    Fondo:{fondo}
                    Fechas: {dates}
                    Precios: {prices}

                    Entrega una conclusión de cómo se ha ido comportando el fondo y un consejo al usuario de si debe seguir invirtiendo o retirar fondos
                    ''',
            )
            prompt = prompt_data_fintual.format(prompt=prompt, fondo=fondo, dates=dates, prices=prices)
        if agent_flow:
            data = {
                "messages": [{
                    "role": "user",
                    "content": prompt_template_unificador.format(prompt=prompt, agents_response=agents_response)
                }]
            }
            fill_response = ''
        else:
            data = {
                "messages": st.session_state.messages
            }
        
        response = requests.post(url, headers=headers, json=data, stream=True)
        raw_data = ''
        tokens = ''
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                raw_data = chunk.decode('utf-8').replace("data: ", '')
                if raw_data != "":
                    lines = raw_data.strip().splitlines()
                    for line in lines:
                        line = line.strip()
                        if line and line != "[DONE]":
                            try:
                                json_object = json.loads(line) 
                                result = json_object['data']
                                full_response += result
                                time.sleep(0.05)
                                # Add a blinking cursor to simulate typing
                                message_placeholder.markdown(full_response + "▌")
                            except json.JSONDecodeError:
                                print(f'Error al decodificar el objeto JSON en la línea: {line}')
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
