# Felipe Barcellos em Florianópolis — dados e reprodução

Primeiro turno de 2026, deputado federal de Santa Catarina. Felipe Barcellos Monte Raso concorreu pelo MISSÃO, número 1414. Foram 28.807 votos no estado e 3.587 em Florianópolis.

## Recorte e resultados da conferência

- Município TSE: 81051, Florianópolis; eleição 6259; pleito 3220; cargo 6.
- 1.207 seções principais / boletins totalizados, cobrindo 100% do resultado municipal.
- 1.093 seções principais registraram ao menos um voto no candidato; 114 registraram zero.
- 1.211 seções cadastradas: 1.207 principais e 4 agregadas. Seções agregadas já estão incluídas no boletim da principal.
- 139 locais de votação, 62 nomes de bairros/localidades, sem nenhum voto ou seção sem vínculo territorial.
- 20 seções apresentam remanejamento de local; o código original no boletim foi conferido com o código original no cadastro e o bairro é o do local atual.
- 5 bairros/localidades com votação zero foram mantidos: Caieira da Barra do Sul, Costa da Lagoa, Morro da Caixa, Retiro da Lagoa e Serrinha.
- Conferência exata da soma de votos de **cada candidato**, **cada legenda** e dos totais municipais de válidos, nominais, legenda, brancos, nulos, nulos técnicos, anulados sub judice, comparecimento, eleitorado e seções.

## O que significa bairro

O agrupamento utiliza o campo `NM_BAIRRO` do local de votação no cadastro eleitoral do TSE. **Não identifica a residência dos eleitores.** São preservados os nomes originais do cadastro, inclusive localidades e subdivisões: JURERÊ, JURERÊ TRADICIONAL e JURERÊ INTERNACIONAL, por exemplo, permanecem separados. Não houve geocodificação, estimativa de votação ou redistribuição proporcional de votos.

A ligação é exata por município + zona + seção. As coordenadas são do local cadastrado e permitem localizar as urnas em mapa, sem afirmar que representam limites territoriais de bairros.

## Datas e fontes

Consulta aos resultados oficiais municipais e estaduais: **6 de outubro de 2026**. Resultado municipal gerado pelo TSE em 04/10/2026 às 21:56:30, estadual às 21:56:38. Cadastro gerado em 05/10/2026 às 06:29:34. Boletins oficiais previamente baixados em 05/10/2026 e reutilizados, com o SHA-256 local conferido para cada arquivo; a soma foi reconciliada novamente com a totalização oficial consultada em 06/10/2026. Os endereços oficiais de cada boletim estão no manifesto. A conferência de hash verifica integridade do arquivo reutilizado; não é uma verificação criptográfica da assinatura eleitoral.

- [Resultado oficial municipal](https://resultados.tse.jus.br/oficial/ele2026/6259/dados/sc/sc81051-c0006-e006259-u.json)
- [Resultado oficial estadual](https://resultados.tse.jus.br/oficial/ele2026/6259/dados/sc/sc-c0006-e006259-u.json)
- [Cadastro oficial de locais/seções 2026 — ZIP](https://cdn.tse.jus.br/estatistica/sead/odsele/eleitorado_locais_votacao/eleitorado_local_votacao_2026.zip)
- [Portal de dados abertos — eleitorado 2026](https://dadosabertos.tse.jus.br/dataset/eleitorado-2026)
- [Configuração oficial das seções](https://resultados.tse.jus.br/oficial/ele2026/arquivo-urna/3220/config/sc/sc-p003220-cs.json)
- [Documentação da divulgação oficial](https://www.tse.jus.br/eleicoes/informacoes-tecnicas-sobre-a-divulgacao-de-resultados)

O painel é uma fotografia dos dados consultados. Não tem atualização automática.

## Percentuais

`shareOfCandidateCityVotes`: votos de Felipe Barcellos no bairro divididos pelos 3.587 votos do candidato no município, multiplicado por 100.

`shareOfValidVotes`: votos do candidato divididos pela soma dos votos nominais e de legenda **válidos** para deputado federal no mesmo recorte, multiplicado por 100.

O percentual oficial do candidato, preservado separadamente em `candidate.cityOfficialPercentage`, usa o denominador de votos concorrentes do TSE (309.712), que inclui 203 votos anulados sub judice. Ele não deve ser confundido com os 309.509 votos válidos. `nullVotes` já inclui `technicalNullVotes`; não somar os dois campos.

## Arquivos

- `data.json`: base pronta para o site, com candidato, pleito, cobertura, totais, bairros, locais, coordenadas, fontes e metodologia.
- `bairros.csv`: 62 linhas de bairros/localidades, UTF-8 com BOM, separador ponto e vírgula.
- `secoes.json` e `secoes.csv`: resultados das 1.207 seções principais, links dos boletins e hashes.
- `auditoria.json`: totais esperados e calculados, conferências, remanejamentos, seções agregadas e bairros com zero.
- `manifesto-boletins.json`: endereço oficial e SHA-256 de cada boletim usado.
- `cadastro-florianopolis.json`: somente as linhas/campos de locais e seções relevantes de Florianópolis, extraídos do ZIP do TSE.
- `municipio-oficial.json` e `estado-oficial.json`: cópias dos resultados oficiais consultados.
- `prepare_register.py` e `build_data.py`: reprodução usando apenas a biblioteca padrão do Python 3.

## Reprodução

Mantenha os scripts e os quatro arquivos de entrada (`manifesto-boletins.json`, `cadastro-florianopolis.json`, `municipio-oficial.json`, `estado-oficial.json`) no mesmo diretório.

Para baixar os boletins públicos que ainda não estão presentes e refazer toda a agregação e conferência:

```sh
python3 build_data.py --bu-dir boletins --download
```

Para usar boletins já baixados:

```sh
python3 build_data.py --bu-dir /caminho/dos/boletins
```

Para reextrair o cadastro a partir do ZIP original do TSE:

```sh
python3 prepare_register.py /caminho/eleitorado_local_votacao_2026.zip
```

A extração do cadastro foi repetida diretamente do ZIP oficial e o resultado foi idêntico ao insumo da agregação. O arquivo SC dentro do ZIP consultado possui SHA-256 `aefca9d6828d655fe88bf40ab9833932a89ff45e23ed8f3c42ea434eb4b27529`. Se o TSE substituir o conteúdo dos endpoints em atualizações posteriores, os hashes ou conferências podem falhar; preserve a fotografia original para repetir exatamente esta consulta.
