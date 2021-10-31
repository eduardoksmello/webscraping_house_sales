#!/usr/bin/env python
# coding: utf-8

# # Objetivo
# 
# Realizar processo de coleta de dados estruturados da web de maneira automatizada (web scraping) de site de imóveis residenciais de Curitiba (Brasil).

# # Procedimentos
# - Importar bibliotecas
# - Estabelecer conexão com o site 'portalimoveiscuritiba.com.br'
# - Coletas de dados
# - Criação de ficheiro

# # Bibliotecas

# In[1]:


# importando bibliotecas
from urllib.request import urlopen, urlretrieve, Request
from urllib.error import URLError, HTTPError
import urllib.request as urllib_request
from bs4 import BeautifulSoup
import pandas as pd


# # Conexão com o site

# In[2]:


# atribuindo site para variável
url = "https://portalimoveiscuritiba.com.br/imoveis?nidtbxfin=1&nidtbxtpi=1&nidtagbac=&nidtbxloc="

# teste de erros
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'}

try:
    req = Request(url, headers = headers)
    response = urlopen(req, timeout=20)
    print(response.read())

except HTTPError as e:
    print(e.status, e.reason)

except URLError as e:
    print(e.reason)


# A conexão foi estabelecida sem erros.

# # Scraping

# In[5]:


# obtendo dados da HTML
response = urlopen(url, timeout=20) 
html = response.read().decode('utf-8') 

# tratamento de dados da html: eliminar espaços entre as TAGs
html = " ".join(html.split()).replace('> <', '><')

# criação do objeto BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')
pages = int(soup.find('div', class_='pagerfanta').get_text().split()[-1].split('...')[-1])

# declarando variável cards que armazenará conteúdo do dataset
cards = []

# iterando todas as páginas do site
for i in range(pages):
    
    # obtendo o HTML
    response = urlopen('https://portalimoveiscuritiba.com.br/imoveis?nidtbxfin=1&nidtbxtpi=1&nidtagbac=&nidtbxloc=&page=' + str(i + 1))
    html = response.read().decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    
    # obtendo as TAGs de interesse: todos os imóveis anunciados
    ads = soup.find('div', class_="tl-filterOuter").findAll('div', class_="row")
    
    for ad in ads:
        card = {}

        # Valor
        card['price'] = ad.find('h3', {'class': 'price'}).getText()

        # Localização
        address = ad.find('span', {'class': 'address'}).getText().split(' - ')
        card['city'] = address[0].lower()
        card['neighborhood'] = address[-1].lower()
        
        # Quartos e Garagens
        info = ad.find('ul', {'class': 'tl-meta-listed'}).get_text().split()
        card['bedrooms'] = info[1]
        card['garage'] = info[-1]
        
        # Adicionando resultado à lista cards
        cards.append(card)    


# # Ficheiro CSV

# In[6]:


# criando um DataFrame com os resultados
dataset = pd.DataFrame(cards)

# tratando os dados: registros ausentes no site serão padronizados para None
dataset['bedrooms'][dataset['bedrooms'] == 'Garagens'] = None
dataset['garage'][dataset['garage'] == 'Garagens'] = None


# In[7]:


# quantidade de cards obtidos 
len(cards)


# In[8]:


# quantidade de linhas e colunas do dataset
dataset.shape


# In[9]:


# visualização do dataset
dataset


# In[10]:


# informações sobre o dataset
dataset.info()


# In[11]:


# estatísticas descritivas do dataset
dataset.describe()


# In[21]:


# salvando o dataset em um ficheiro CSV
dataset.to_csv('./dataset_imoveis.csv', sep=';', index = False, encoding = 'utf-8-sig')

