import os, time, requests, json
import streamlit as st
import asyncio

from PIL import Image
from dotenv import load_dotenv
load_dotenv()
from pydantic import BaseModel
from typing import List
import matplotlib.pyplot as plt
from langchain.prompts import PromptTemplate

from judini.codegpt.agent import Agent

from typing import Any, List, Mapping, Optional
from langchain.callbacks.manager import CallbackManagerForLLMRun

from langchain.callbacks import StdOutCallbackHandler
from langchain.callbacks.streamlit import LLMThoughtLabeler, StreamlitCallbackHandler

#Judini
CODEGPT_API_KEY= os.getenv("CODEGPT_API_KEY")
CODEGPT_AGENT_ORQUESTADOR= os.getenv("CODEGPT_AGENT_ORQUESTADOR")
CODEGPT_AGENT_GENERAL= os.getenv("CODEGPT_AGENT_GENERAL")
CODEGPT_AGENT_RISKY_NORRIS= os.getenv("CODEGPT_AGENT_RISKY_NORRIS")
CODEGPT_AGENT_MODERATE_PITT= os.getenv("CODEGPT_AGENT_MODERATE_PITT")
CODEGPT_AGENT_CONSERVATIVE_CLOONEY= os.getenv("CODEGPT_AGENT_CONSERVATIVE_CLOONEY")
CODEGPT_AGENT_UNIFICADOR= os.getenv("CODEGPT_AGENT_UNIFICADOR")

url = 'https://plus.codegpt.co/api/v1/agent/'

# set_page_config() can only be called once per app page, and must be called as the first Streamlit command in your script.

st.set_page_config(
    page_title="Llama CodeGPT Agent",
    page_icon="✨",
    layout="wide",
)

st.image('fake-fintual-copiloto.png', width=50)
st.title("Fake Fintual Copiloto 🤖")
st.write("Preguntame cualquier cosa sobre los fondos de fintual... pero una advertencia ⚠️ Soy la versión Fake!")
st.write('Creado por <a href="https://www.linkedin.com/in/daniel-avila-arias/">Daniel San</a> con <a href="https://codegpt.co/">CodeGPT</a>', unsafe_allow_html=True)
st.divider()

# Crear un sidebar
st.sidebar.title("Agentes interactuando")


if "agents" not in st.session_state:
    st.session_state["agents"] = []

if "user" not in st.session_state:
    st.session_state['user'] = ''

if "password" not in st.session_state:
    st.session_state['password'] = ''

headers = {
    "Content-Type": "application/json; charset=utf-8",
    "Authorization": f"Bearer {CODEGPT_API_KEY}"
}


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

async def run_function_agent(agent_id, prompt):
    st.session_state.agents.append({
        "time": time.time(),
        "agent": "agente_orquestador"
    })
    agent_instance = Agent(api_key=CODEGPT_API_KEY,agent_id=agent_id )
    full_response = ""
    async for response in agent_instance.chat_completion(prompt, stream=False):
        full_response += response
    try:
        json_response = json.loads(full_response)
        return json_response
    except json.JSONDecodeError:
        json_response = full_response
    return json_response


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

async def run_rag_agent(type_agent):

    if(type_agent == "agente_general"):
        agent_id = CODEGPT_AGENT_GENERAL
        role = 'assistant'
    if(type_agent == "risky_norris_rag_agent"):
        agent_id = CODEGPT_AGENT_RISKY_NORRIS
        role = 'user'
    if(type_agent == "moderate_pitt_rag_agent"):
        agent_id = CODEGPT_AGENT_MODERATE_PITT
        role = 'user'
    if(type_agent == "conservative_clooney_rag_agent"):
        agent_id = CODEGPT_AGENT_CONSERVATIVE_CLOONEY
        role = 'user'
    if(type_agent == "fintual_api_agent"):
        agent_id = CODEGPT_AGENT_RISKY_NORRIS
        role = 'user'


    # Cuando está activa, duplica la respuesta del bot
    # st.session_state.messages.append({"role": role, "content": prompt})

    # st.write(data)
    # st.write(headers)
    # st.write(url+agent_id)

    # add agent to sidebar list

    st.session_state.agents.append({
        "time": time.time(),
        "agent": type_agent
    })

    data = { "messages": st.session_state.messages }
    response = requests.post(url+agent_id, headers=headers, json=data, stream=True)

    raw_data = ""
    full_response = ""

    # quité el nombre del agente del full_response porque lo envias en el mensaje y se duplica en la respuesta

    for chunk in response.iter_content(chunk_size=1024):
        if chunk:
            raw_data = chunk.decode('utf-8').replace("data: ", '').strip()
            if raw_data != "":
                lines = raw_data.strip().splitlines()
                for line in lines:
                    line = line.strip()
                    if line and line != "[DONE]":
                        try:
                            json_object = json.loads(line)
                            result = json_object['data']
                            full_response += result
                            time.sleep(0.03)
                            # Add a blinking cursor to simulate typing
                            message_placeholder.write(f"{full_response} ▌")
                        except json.JSONDecodeError:
                            print(f'Error al decodificar el objeto JSON en la línea: {line}')
            # add to the first space in full_response "hola"
            # "**"+type_agent.replace("_", " ").capitalize()+"** dice: \r\r"
            # full_response = "**"+type_agent.replace("_", " ").capitalize()+"** dice: \r\r"

    return full_response

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



# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar='fake-fintual-copiloto.png' if message["role"] == "assistant" else None):
        st.write(message["content"])

if prompt := st.chat_input("En que te puedo ayudar?"):

    # with st.chat_message(name="Gus"):
    with st.chat_message("user"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.write(prompt)

    array_response = []
    # full_response = ""

    # Display assistant response in chat message container

    with st.chat_message("assistant", avatar='fake-fintual-copiloto.png'):

        with st.status("Buscando al mejor agente para esta consulta...", expanded=True) as status:

            prompt_data_fintual = ''
            message_placeholder = st.empty()

            message_placeholder.write("🤖 Pensando...")
            # st.session_state.agents.append

            is_function = False

            response = asyncio.run(run_function_agent(CODEGPT_AGENT_ORQUESTADOR, prompt))

            status.update(label="Agente seleccionado", state="running", expanded=True)

            if(response["function"] != False):
                # ejecutar agent general
                st.code(response["function"], language="json", line_numbers=True)
                agent_name = response["function"]["name"]
                title_agent_name=agent_name.replace("_", " ")
                status.update(label=f"Ejecutando agente {title_agent_name}", state="running", expanded=True)
                json_arguments = json.loads(response["function"]["arguments"])
                sub_rag_string = "rag"
                sub_api_string = "api"

                # function rag
                if sub_rag_string in agent_name:
                    question = json_arguments["question"]
                    # ejecutar rag agent
                    prompt = asyncio.run(run_rag_agent(agent_name))

                if sub_api_string in agent_name:
                    st.code(sub_api_string in agent_name, language="json", line_numbers=True)
                    fondo_name = json_arguments["fondo_name"]
                    date_to = json_arguments["date_to"]
                    date_from = json_arguments["date_from"]
                    date_price = api_fintual(
                    fondo_name, date_from, date_to
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
                    prompt = prompt_data_fintual.format(prompt=prompt, fondo=fondo_name, dates=dates, prices=prices)
            
            status.update(label="Preparando respuesta final", state="running", expanded=True)
            response_agent = asyncio.run(run_rag_agent('agente_general'))
            status.update(label="Respuesta obtenida", state="complete", expanded=True)
            
            st.session_state.messages.append({"role": "assistant", "content": response_agent})


        # # st.write(full_response)
        # print(full_response)

        # status.update(label="Download complete!", state="complete", expanded=False)

agent_story=""
for agent in st.session_state.agents:
    # # show hour of agent
    # st.session_state.agents.append({
    #     "time": time.time(),
    #     "agent": type_agent
    # })
    # order agents by time
    st.session_state.agents.sort(key=lambda x: x['time'], reverse=True)
    agent_story += f"{int((time.time() - agent['time']) / 60)} min ago\t{agent['agent'].replace('_', ' ').capitalize()}\n"


# st.sidebar.write("🤖 " + agent['agent'].replace("_", " ") + f" - {int((time.time() - agent['time']) / 60)} min ago")

st.sidebar.code(agent_story, language="markdown", line_numbers=False)


# with st.chat_message("assistant"):
#     st.write(full_response)