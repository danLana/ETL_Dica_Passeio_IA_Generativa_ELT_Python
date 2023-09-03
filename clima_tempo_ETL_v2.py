import pandas as pd
from IPython.display import display
import requests
import json
import csv

import openai
import os

def getID_cidade(cidade, estado):
    global iUrl, iToken 
    response = requests.get(f"{iUrl}{cidade.title()}&state={estado.upper()}&token={iToken}")
    return json.loads(response.text) if response.status_code == 200 else None
    # print(json.loads(response.text))

def getTemperatura_cidade(id):
    global iTemp, iToken
    response = requests.get(f"{iTemp}{id}/current?token={iToken}")
    # print(f"{iTemp}{id}?token={iToken}")
    return json.loads(response.text) if response.status_code == 200 else None
    # print(response.status_code)    

def getRegister_cidade(registrar):
    global iRegToken, iToken
    payload = {"localeId[]":f"{registrar}"}
    # print(payload)
    headers = {'Content-Type':'application/x-www-form-urlencoded'}
    response = requests.put(f"{iRegToken}", data=payload, headers=headers)
    return json.loads(response.text) if response.status_code == 200 else None
    # print(response) 

def generate_ia_dicas(cidade, estado, temperatura):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k-0613",
        # model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "Você é um especialista em Turismo."
            },
            {
                "role": "user",
                "content": f"Fale um passeio na cidade {cidade} no estado {estado}, quando a temperatura for {temperatura} (máximo de 100 caracteres)"
            }
        ]  
    )

    return completion.choices[0].message.content.strip('\"') 
   

####################################
############## EXTRACT / TRANSFORM - INICIO
####################################
# Extrair os IDs do arquivo CSV.
df = pd.read_csv('C:/Users/danil/Documents/DIO BOOTCAMP/Explorando_IA_Generativa_ETL/Codigos/Projeto/lista_cidades.csv')
# display(df)

base_cidades = df.values.tolist()

# print(cidades)
# Obter os dados de cada ID da cidade usando a API da clima tempo.
iToken = '5509f25710074c1374f27113524f4828'
# URL idCidade > "http://apiadvisor.climatempo.com.br/api/v1/locale/city?name=São Paulo&state=SP&token=your-app-token"
iUrl = f"http://apiadvisor.climatempo.com.br/api/v1/locale/city?name="
# print(iUrl)
# URL Temp Cidad > "http://apiadvisor.climatempo.com.br/api/v1/climate/temperature/locale/3477?token=your-app-token"
# http://apiadvisor.climatempo.com.br/api/v1/weather/locale/3477/current?token=your-app-token
iTemp = f"http://apiadvisor.climatempo.com.br/api/v1/weather/locale/"
# URL Register token city > 'http://apiadvisor.climatempo.com.br/api-manager/user-token/:your-app-token/locales' \
#          -H 'Content-Type: application/x-www-form-urlencoded' \
#          -d 'localeId[]=3477'
iRegToken = f"http://apiadvisor.climatempo.com.br/api-manager/user-token/{iToken}/locales"
openai_api_key = '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'

openai.api_key = openai_api_key


for cidades in base_cidades:
    # print(cidades)
    cidade = cidades[0].title()
    estado = cidades[1].upper()
    # print(cidade, estado)
    
    infoCidade = getID_cidade(cidade, estado)
    # print(infoCidade[0]['id'])    
    
    registro = getRegister_cidade(infoCidade[0]['id'])
    # print(registro)
    
    temperaturaCidade = getTemperatura_cidade(infoCidade[0]['id'])
    # print(temperaturaCidade)
    # print(temperaturaCidade['name']," ", temperaturaCidade['state'], " ", temperaturaCidade['data']['temperature'])

    dicas = generate_ia_dicas(cidade=temperaturaCidade['name'],estado=temperaturaCidade['state'],temperatura=temperaturaCidade['data']['temperature'])
    # print(dicas)

    guia_turismo_cidades = {
        "cidade": cidade,
        "estado": estado,       

    }

    if guia_turismo_cidades.get('dicas'):
        if len(guia_turismo_cidades['dicas']) != 0:
            id_new = len(guia_turismo_cidades['dicas']) + 1
        else:
            id_new = 1
    else:
        id_new = 1

    # print(guia_turismo_cidades)

    guia_turismo_cidades['dicas']=({
        "id": id_new,
        "description": dicas
    })

    # print(guia_turismo_cidades.items())

####################################
############## LOAD - INICIO
####################################

    arquivo ="C:/Users/danil/Documents/DIO BOOTCAMP/Explorando_IA_Generativa_ETL/Codigos/Projeto/guiaTuristo.txt"  

    with open(arquivo, 'w', encoding='utf-8') as file:
     file.write(json.dumps(guia_turismo_cidades)) # use `json.loads` to do the reverse

    print(f"Dica da cidade de {guia_turismo_cidades['cidade']} cadastrado e pronto para uso!")




 




