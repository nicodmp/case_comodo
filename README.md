# Desafio Tecnico Comodo - Nicolas de Melo Proença

Parte 1:
Para desenvolver este script, devido a minha familiaridade limitada com o funcionamento da API do Github, inseri a documentacao da API em um Gemini Notebook, e apos um overview do funcionamento da autenticacao e endpoints para obter informacoes de repos, prossegui com o desenvolvimento em colaboracao com a IA dentro do proprio Gemini Notebook. Testei as funcionalidades do script de forma incremental executando o codigo em ambiente Google Colab, com o access token mantido separado do codigo usando a funcionalidade de secret do Colab.

O script pode ser encontrado na pasta "parte_1", e tem como alvo os repos do usuario "microsoft", conforme sugerido no enunciado do case. Para a execuçao automatica, inseri a ultima versao do script em um workflow n8n, que esta disponivel no arquivo "githubscraper.json". O token access do github deve ser inserido como uma credential no n8n. Caso ele nao seja encontrado durante a execucao, o script funciona da mesma forma, apenas com um rate limit menor.

O script tem dois outputs: um arquivo CSV "{usuario}_repos_{data}.csv", e um arquivo sqlite3 ""{usuario}_repos_{data} .db". Optei por gerar ambos arquivos para possibilitar uma consulta visual facil e rapida por um usuario humano atraves do arquivo CSV, e um historico consolidado e recuperavel no banco de dados sqlite3. Nao produzi um output em .jsonl pois, no momento, o resultado nao sera utilizado por uma IA, mas essa funcionalidade pode ser adicionada ao mesmo script sem interferir com o output existente. 

Para o proposito deste desafio, a execuçao automatica do script acontece atraves de um cron job, cujo script tambem esta disponivel dentro da pasta "parte_1". Nesse caso, deve ser utilizado o arquivo "script_github_cron" com uma variavel de ambiente na mesma pasta, conforme exemplo disponivel em env.example. E possivel utilizar um n8n self-hosted para execucao automatizada do script, mas considero uma camada desnecessaria dada a baixa complexidade do script e custo e trabalho adicional envolvido para o deploy com n8n. 

Notebook no Google Colab:
https://colab.research.google.com/drive/1vee0T_Z1PdpAxYBrZ10nNAJyv_xln0nZ?usp=sharing

Parte 2:
As queries podem ser encontradas na pasta "parte_2". Claude Code utilizado para modelar o banco de dados baseado nos CSV fornecidos, e testar consultas em db PostgreSQL local.
Inserir schema db

Parte 3:
Possiveis pontos de melhoria para esse script seriam chamadas assincronas, limite de concorrencia, backoff exponencial, cache de conversas, logging mais robusto e separaçao de funcionalidades em diferentes arquivos. Para o escopo deste desafio e o volume de processamento mencionado no case (4000 conversas em 3 meses) considero que uma arquitetura contemplando os pontos mencionados acima seria overengineering nesse momento, mas podem ser implementados caso o script precisa escalar em quantidade de conversas processadas no futuro.
