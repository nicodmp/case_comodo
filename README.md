# Desafio Técnico Comodo - Nicolas de Melo Proença

## Parte 1:
Para desenvolver este script, devido à minha familiaridade limitada com o funcionamento da API do Github, inseri a documentação da API em um **Gemini Notebook**, e após estudar o funcionamento da autenticação e endpoints necessários para obter informações de repos, prossegui com o desenvolvimento em colaboração com a IA dentro do próprio Gemini Notebook. Testei as funcionalidades do script de forma incremental executando o código em ambiente **Google Colab**, com o access token mantido isolado do código usando a funcionalidade de **Secrets** do Colab.

O script pode ser encontrado na pasta "parte_1", e tem como alvo os repos da organização "microsoft", conforme sugerido no enunciado do case. Para a execução automática, refatorei a última versão do script para rodar com um cron job. Caso o access token não seja encontrado durante a execução, o script funciona da mesma forma, apenas com um rate limit menor.

O script tem dois outputs: um arquivo CSV `{usuario}_repos_{data}.csv`, e um arquivo sqlite3 `{usuario}_repos.db`. Optei por gerar ambos arquivos para possibilitar uma consulta visual fácil e rápida por um usuário humano atraves do arquivo CSV, e um historico consolidado e recuperável no banco de dados sqlite3. Não produzi um output em .jsonl pois, no momento, o resultado não será analisado por uma IA, que seria a principal motivação para produzir um output nesse formato.

Para o propósito deste desafio, a execução automática do script acontece através de um **cron job**, cujo script tambem está disponivel dentro da pasta "parte_1". Supondo que o projeto será hospedado em uma VM Linux, basta adicionar o cron conforme arquivo fornecido ao crontab. Seria possível utilizar um n8n self-hosted para execução automatizada do script, mas considero uma camada desnecessária dada a baixa complexidade do script e custo e trabalho adicional envolvido para o deploy e manutenção de uma instância de n8n self-hosted. 

Notebook no Google Colab:
https://colab.research.google.com/drive/1vee0T_Z1PdpAxYBrZ10nNAJyv_xln0nZ?usp=sharing

## Parte 2:
As queries podem ser encontradas na pasta "parte_2". Modelei as tabelas manualmente em padrão SQL, e foi utilizado **Claude Code** para modelar o banco de dados baseado nos CSV fornecidos, e testar consultas em DB **PostgreSQL** local.

Tabelas criadas:
```
CREATE TABLE vendas (
  venda_id VARCHAR(50) PRIMARY KEY, 
  lead_id VARCHAR(50) NOT NULL, 
  data_fechamento DATE, 
  valor_contrato DECIMAL(12,2),
  
  FOREIGN KEY (lead_id) REFERENCES leads(lead_id)
  );
```
```
CREATE TABLE leads (
  lead_id VARCHAR(50) PRIMARY KEY, 
  nome VARCHAR(255), 
  telefone VARCHAR(20), 
  criado_em TIMESTAMP, 
  campanha_id VARCHAR(50), 
  etapa_atual VARCHAR(100)
  );
```
```
CREATE TABLE investimento_midia (
  data DATE, 
  campanha_id VARCHAR(50), 
  plataforma VARCHAR(50), 
  nome_campanha VARCHAR(255), 
  gasto DECIMAL(12,2), 
  impressoes INTEGER, 
  clique INTEGER
  );
```

Para organização do README, os resultados das queries podem ser encontrados nos arquivos CSV disponíveis na pasta "parte_2".

As justificativas de como cada número foi alcançado estão descritas nos comentários de cada query.

A única consulta na qual não tenho confiança é a 2, pois não consegui encontrar um histórico por lead significando por quais etapas cada lead já passou, nem há leads duplicados na tabela, impossibilitando um cálculo preciso que contemple todos os leads e o percentual de perda real entre etapas. Acredito que a forma mais prática de obter essa informação seria permitindo a duplicação de leads a cada nova etapa alcançada no funil, com timestamps, permitindo distinguir a quantidade real de leads perdidos a cada etapa.

## Parte 3:
Script desenvolvido iterativamente com **Claude Code**.

Possíveis pontos de melhoria para esse script seriam:
- Chamadas assíncronas;
- Limite de concorrência;
- Backoff exponencial;
- Cache de conversas;
- Logging mais robusto;
- Separação de funcionalidades em diferentes arquivos.

Para o escopo deste desafio e o volume de processamento mencionado no case (4000 conversas em 3 meses), considero que uma arquitetura contemplando os pontos mencionados acima seria _overengineering_tal nesse momento, mas podem ser implementados caso o script precisa escalar em quantidade de conversas processadas no futuro.

Para definir se a classificação está funcionando bem ou não, o primeiro e mais crucial passo é inserir um conjunto de referência humano, selecionar aleatoriamente uma amostra de 20 a 30% das conversas, e classificar por um profissional humano, comparando com os resultados da IA para a mesma conversa. Dividir os resultados iguais pelo total de conversas fornecerá a métrica de precisão do processo.

A partir disso, é possível refinar os resultados dando pesos diferentes de acordo com a prioridade. Saber a taxa de precisão para leads classificados como "quentes" por um humano é mais crucial que apenas a precisão do volume total. Além disso, a distância na avaliação da IA e do agente humano fornece uma média mais precisa do que uma avaliação binária de "certo" ou "errado".

Já para os campos qualitativos, como `sinais`, `proxima_acao` e `resumo_para_o_vendedor`, eu solicitaria uma avaliação humana focada não apenas na correção dos dados, mas também no que faltou ou pode ser melhor descrito, factualidade e relevância para a equipe de Vendas.

Após 3 meses, também será possível comparar no mundo real a classificação de leads pela IA com a taxa de conversão, portanto, caso a conversão de leads quentes > leads mornos > leads frios, isso é um sinal de que a classificação está performando conforme o esperado.