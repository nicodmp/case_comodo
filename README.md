# Desafio Técnico Comodo - Nicolas de Melo Proença

Parte 1:
Para desenvolver este script, devido à minha familiaridade limitada com o funcionamento da API do Github, inseri a documentação da API em um Gemini Notebook, e após estudar o funcionamento da autenticação e endpoints necessários para obter informações de repos, prossegui com o desenvolvimento em colaboração com a IA dentro do próprio Gemini Notebook. Testei as funcionalidades do script de forma incremental executando o código em ambiente Google Colab, com o access token mantido isolado do código usando a funcionalidade de Secrets do Colab.

O script pode ser encontrado na pasta "parte_1", e tem como alvo os repos da organização "microsoft", conforme sugerido no enunciado do case. Para a execução automática, adaptei a ultima versao do script para rodar com um cron job. Caso o access não token nao seja encontrado durante a execução, o script funciona da mesma forma, apenas com um rate limit menor.

O script tem dois outputs: um arquivo CSV "{usuario}_repos_{data}.csv", e um arquivo sqlite3 ""{usuario}_repos_{data} .db". Optei por gerar ambos arquivos para possibilitar uma consulta visual fácil e rápida por um usuário humano atraves do arquivo CSV, e um historico consolidado e recuperável no banco de dados sqlite3. Não produzi um output em .jsonl pois, no momento, o resultado não será analisado por uma IA, que seria a principal motivação para produzir um output nesse formato.

Para o propósito deste desafio, a execução automática do script acontece através de um cron job, cujo script tambem está disponivel dentro da pasta "parte_1". Seria possivel utilizar um n8n self-hosted para execução automatizada do script, mas considero uma camada desnecessária dada a baixa complexidade do script e custo e trabalho adicional envolvido para o deploy e manutenção de uma instância de n8n self-hosted. 

Notebook no Google Colab:
https://colab.research.google.com/drive/1vee0T_Z1PdpAxYBrZ10nNAJyv_xln0nZ?usp=sharing

Parte 2:
As queries podem ser encontradas na pasta "parte_2". Claude Code utilizado para modelar o banco de dados baseado nos CSV fornecidos, e testar consultas em db PostgreSQL local.

TODO Inserir schema db
TODO Inserir resultados de queries

Parte 3:
Possíveis pontos de melhoria para esse script seriam:
- Chamadas assíncronas;
- Limite de concorrência;
- Backoff exponencial;
- Cache de conversas;
- Logging mais robusto;
- Separação de funcionalidades em diferentes arquivos.

Para o escopo deste desafio e o volume de processamento mencionado no case (4000 conversas em 3 meses), considero que uma arquitetura contemplando os pontos mencionados acima seria overengineering nesse momento, mas podem ser implementados caso o script precisa escalar em quantidade de conversas processadas no futuro.
