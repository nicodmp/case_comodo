import json
import os
import sys
from typing import Literal

from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError

MODEL = "gpt-5-mini"
INPUT_FILE = "input.json"
OUTPUT_FILE = "output.json"
MAX_RETRIES = 3

class Classificacao(BaseModel):
    conversa_id: str
    classificacao: Literal[
        "quente",
        "morno",
        "frio",
        "fora_do_perfil"
    ]
    prioridade: int = Field(ge=1, le=5)
    sinais: list[str]
    proxima_acao: str
    resumo_para_o_vendedor: str

SYSTEM_PROMPT = """
Você é um especialista em qualificação de leads para uma empresa
de móveis planejados.

Sua tarefa é analisar uma conversa entre um lead e um atendente e
classificar o potencial comercial do lead.

Classificações possíveis:

- quente:
  Lead com alta intenção de compra, projeto relativamente definido,
  orçamento compatível e/ou prazo próximo. Pode estar pronto para
  avançar para visita, medição, proposta ou fechamento.

- morno:
  Existe interesse real e potencial comercial, mas falta algum
  elemento importante como prazo, orçamento, definição do projeto
  ou intenção de compra mais imediata.

- frio:
  Interesse muito inicial, pesquisa, prazo muito distante, pouca
  informação ou baixa intenção de avançar no momento.

- fora_do_perfil:
  O pedido não corresponde ao serviço/produto oferecido pela empresa,
  ou existe outro motivo claro que torna o lead inadequado.

Prioridade:

1 = prioridade máxima
2 = alta
3 = média
4 = baixa
5 = mínima

A prioridade deve considerar principalmente:
- intenção de compra;
- proximidade do prazo;
- orçamento;
- tamanho/valor potencial do projeto;
- disponibilidade para próxima etapa;
- urgência;
- sinais explícitos de fechamento.

"Sinais" deve conter evidências objetivas encontradas na conversa.

"proxima_acao" deve ser uma ação prática que o vendedor deve tomar.

"resumo_para_o_vendedor" deve ser curto e útil para alguém que
precisa assumir essa conversa rapidamente.

Não invente informações que não estejam na conversa.
"""

def fallback_classificacao(conversa_id: str, erro: str) -> dict:
    """
    Retorna uma estrutura válida mesmo quando a API falha.
    """

    return {
        "conversa_id": conversa_id,
        "classificacao": "frio",
        "prioridade": 5,
        "sinais": [
            "Não foi possível realizar a classificação automática."
        ],
        "proxima_acao": "Revisar a conversa manualmente.",
        "resumo_para_o_vendedor": (
            f"Falha na classificação automática: {erro}"
        )
    }

def classificar_conversa(
    client: OpenAI,
    conversa: dict
) -> dict:

    conversa_id = conversa.get("conversa_id", "UNKNOWN")

    conversa_texto = json.dumps(
        conversa,
        ensure_ascii=False,
        indent=2
    )

    for tentativa in range(1, MAX_RETRIES + 1):

        try:
            response = client.responses.parse(
                model=MODEL,
                input=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": (
                            "Classifique a seguinte conversa:\n\n"
                            + conversa_texto
                        )
                    }
                ],
                text_format=Classificacao,
            )

            resultado = response.output_parsed

            if resultado is None:
                raise ValueError(
                    "O modelo não retornou uma resposta estruturada."
                )

            return resultado.model_dump()

        except ValidationError as e:
            erro = f"Erro de validação: {e}"

        except Exception as e:
            erro = f"{type(e).__name__}: {e}"

        print(
            f"[WARN] {conversa_id}: tentativa "
            f"{tentativa}/{MAX_RETRIES} falhou: {erro}",
            file=sys.stderr
        )

    return fallback_classificacao(conversa_id, erro)

def main():
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print(
            "Erro: variável de ambiente OPENAI_API_KEY não encontrada.",
            file=sys.stderr
        )
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            conversas = json.load(f)

    except FileNotFoundError:
        print(
            f"Erro: arquivo {INPUT_FILE} não encontrado.",
            file=sys.stderr
        )
        sys.exit(1)

    except json.JSONDecodeError as e:
        print(
            f"Erro: {INPUT_FILE} não contém JSON válido: {e}",
            file=sys.stderr
        )
        sys.exit(1)

    if not isinstance(conversas, list):
        print(
            "Erro: o JSON de entrada deve ser uma lista de conversas.",
            file=sys.stderr
        )
        sys.exit(1)

    resultados = []

    total = len(conversas)

    for index, conversa in enumerate(conversas, start=1):

        conversa_id = conversa.get("conversa_id", f"UNKNOWN_{index}")

        print(
            f"[INFO] Processando {index}/{total}: {conversa_id}"
        )

        try:
            resultado = classificar_conversa(
                client,
                conversa
            )

        except Exception as e:
            resultado = fallback_classificacao(
                conversa_id,
                f"{type(e).__name__}: {e}"
            )

        resultados.append(resultado)

    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(
                resultados,
                f,
                ensure_ascii=False,
                indent=2
            )

    except OSError as e:
        print(
            f"Erro ao salvar {OUTPUT_FILE}: {e}",
            file=sys.stderr
        )
        sys.exit(1)

    print(
        f"[INFO] Finalizado. {total} conversas processadas."
    )
    print(
        f"[INFO] Resultado salvo em {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()

