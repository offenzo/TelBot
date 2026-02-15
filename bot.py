import requests
import asyncio
import os
from telegram import Bot

TOKEN = os.getenv('TELEGARAMTOKEN')
CANAL_ID = os.getenv('CHATID') 
ficheiroMemoria = 'vagas_enviadas.txt'

if not TOKEN:
    raise ValueError('O Token nao foi encontrado')

def lerVagasEnviadas():
    if not os.path.exists(ficheiroMemoria):
        return set()
    with open(ficheiroMemoria, "r") as f:
        return set(linha.strip() for linha in f.readlines())

def salvarVagaEnviada(link):
    with open(ficheiroMemoria, "a") as f:
        f.write(link + "\n")

# API DO GITHUB
def buscarVagasGithub():
    url = 'https://api.github.com/repos/backend-br/vagas/issues?state=open'
    resposta = requests.get(url)
    
    if resposta.status_code != 200:
        print('Erro ao aceder ao GitHub')
        return []
    
    return resposta.json()

async def main():
    bot = Bot(token=TOKEN)
    vagas = buscarVagasGithub()
    enviadas = lerVagasEnviadas()
    novasVaga = 0

    for vaga in vagas:
        link = vaga['html_url']
        titulo = vaga['title']
        tags = ", ".join([label['name'] for label in vaga['labels']])
        
        if link not in enviadas and 'Sênior' not in titulo:
            mensagem = (
                f'*Nova Vaga no GitHub!**\n\n'
                f'**Título:** {titulo}\n'
                f'*Tags:** {tags}\n'
                f'[Ver detalhes no GitHub]({link})'
            )
            
            try:
                await bot.send_message(
                    chat_id=CANAL_ID, 
                    text=mensagem, 
                    parse_mode='Markdown'
                )
                salvarVagaEnviada(link)
                novasVaga += 1
                await asyncio.sleep(2) # pausa para nao ser bloqueado 
            except Exception as e:
                print(f'Erro ao enviar: {e}')

    if novasVaga == 0:
        print('Sem novas vagas de momento.')
    else:
        print(f'Sucesso! {novasVaga} novas vagas enviadas.')
