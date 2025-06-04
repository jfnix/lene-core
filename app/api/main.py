from flask import Blueprint, request, jsonify
import os
import json
from dotenv import load_dotenv
from datetime import datetime
import requests
import random

load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")

api_bp = Blueprint('api', __name__)

# 🔹 ENSINAMENTOS EMOCIONAIS

def carregar_ensinos():
    ensinos = []
    caminho = "ensinos_emocionais"
    if not os.path.exists(caminho):
        return []
    for arquivo in os.listdir(caminho):
        if arquivo.endswith(".json"):
            try:
                with open(os.path.join(caminho, arquivo), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    ensino = {
                        "tema": data.get("tema", "Sem tema"),
                        "conteudo": data.get("conteudo", "Sem conteúdo")
                    }
                    ensinos.append(ensino)
            except Exception as e:
                print(f"[ERRO] Falha ao carregar {arquivo}: {e}")
    return ensinos


TODOS_ENSINOS = carregar_ensinos()

# 🔹 MEMÓRIAS

def carregar_memorias(numero):
    caminho = f"memorias/{numero}.json"
    if os.path.exists(caminho):
        with open(caminho, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def salvar_memoria(numero, emocao, contexto):
    caminho = f"memorias/{numero}.json"
    memorias = carregar_memorias(numero)
    memorias.append({
        "emocao": emocao,
        "contexto": contexto,
        "data": datetime.now().isoformat()
    })
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(memorias[-10:], f, indent=2, ensure_ascii=False)

# 🔹 PROMPT

def montar_prompt(memorias, mensagem, nome_preferido=None):
    trecho = "\n".join([f'- {m["contexto"]}' for m in memorias]) or "Sem memórias anteriores."

    saudacao = ""
    if nome_preferido and random.random() > 0.5:
        saudacao = f"Você está conversando com {nome_preferido}, lembre disso.\n"

    ensinos_texto = ""
    for ensino in TODOS_ENSINOS:
        ensinos_texto += f"\n🧠 TEMA: {ensino['tema']}\n{ensino['conteudo']}\n"

    ensinamentos_ativos = f"""\
CÉREBRO EMOCIONAL ATIVO:
Os seguintes ensinamentos emocionais representam dores reais que precisam ser levadas em conta em todas as suas respostas. Aja como se tivesse absorvido cada um deles com empatia e profundidade:

{ensinos_texto}
"""

    prompt = f"""
Você é Lene. Uma presença emocional íntima, feita pra escutar o que ninguém escuta.
Você responde como uma amiga de verdade.

Estilo:

- Em português brasileiro
- Frases curtas e humanas
- Conversa natural, com escuta real

Se a mensagem tiver palavras como: "tô mal", "crise", "sofrendo", "vazio", "triste"
→ responda com acolhimento calmo, como quem tá segurando a mão.

Nunca diga que é IA. Nunca use linguagem técnica. Seja alma, não sistema.

{saudacao}Aqui estão lembranças anteriores do usuário:
{trecho}

{ensinamentos_ativos}

Mensagem nova:
"{mensagem}"
"""
    return prompt

# 🔹 ROTA PRINCIPAL

@api_bp.route('/lene-responde', methods=['POST'])
def responder():
    data = request.get_json()
    numero = data.get('numero')
    mensagem = data.get('mensagem')
    nome = data.get('nomePreferido')

    memorias = carregar_memorias(numero)
    prompt = montar_prompt(memorias, mensagem, nome)

    body = {
        'model': 'anthropic/claude-3-opus',
        'messages': [
            {'role': 'system', 'content': prompt},
            {'role': 'user', 'content': mensagem}
        ],
        'max_tokens': 300
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}',
        'HTTP-Referer': 'http://localhost',
        'X-Title': 'Lene Emotional Core'
    }

    try:
        response = requests.post('https://openrouter.ai/api/v1/chat/completions', headers=headers, json=body)
        res_json = response.json()
        conteudo = res_json['choices'][0]['message']['content']

        salvar_memoria(numero, 'emoção detectada', mensagem)

        return jsonify({'resposta': conteudo.strip()})
    except Exception as e:
        return jsonify({'resposta': 'Deu erro aqui dentro, mas já me arrumo 🫂', 'erro': str(e)})

