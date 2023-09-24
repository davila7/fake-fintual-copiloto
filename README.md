# Fake Fintual Copiloto 2.0

## Description

This repository contains code for the Fake Fintual Copiloto 2.0 agent. The agent is built using CodeGPT and Streamlit.

## Project Setup

Below are the main Python Packages used and their versions:

- `judini==0.0.17`
- `streamlit==1.27.0` 
- `langchain==0.0.240`
- `requests`
- `asyncio`
- `python-dotenv`
- `pydantic`
- `matplotlib`
- `plotly`
- `json`

## Installation

Clone the repository:

```git clone ```

Install the required dependencies:

```pip install -r requirements.txt```

Set up the environment variables:

- CODEGPT_API_KEY: Your CodeGPT API key
- CODEGPT_AGENT_ORQUESTADOR: The ID of the CodeGPT agent for the orquestador
- CODEGPT_AGENT_GENERAL: The ID of the CodeGPT agent for the general agent
- CODEGPT_AGENT_RISKY_NORRIS: The ID of the CodeGPT agent for the risky norris agent
- CODEGPT_AGENT_MODERATE_PITT: The ID of the CodeGPT agent for the moderate pitt agent
- CODEGPT_AGENT_CONSERVATIVE_CLOONEY: The ID of the CodeGPT agent for the conservative clooney agent
- CODEGPT_AGENT_UNIFICADOR: The ID of the CodeGPT agent for the unificador agent


## Usage

To run the code, use the following command:

```streamlit run app.py```

This will start the Streamlit app and you can interact with the Fake Fintual Copiloto 2.0 agent by asking questions about Fintual funds.

## Agents

The app supports multiple agents, including:

- Agente Orquestador
- Agente General
- Risky Norris RAG Agent
- Moderate Pitt RAG Agent
- Conservative Clooney RAG Agent
- Fintual API Agent

### Chat History

The app keeps track of the chat history and displays it on each run. You can see the chat messages between the user and the agent in the app.

### API Integration

The app integrates with the Fintual API to fetch data about the funds. It uses the api_fintual function to retrieve the data and displays it in a bar chart.

### Agent Story

The app also keeps track of the interactions with each agent and displays the agent story in the sidebar. You can see the interactions of each agent in the app.
