# Felipe Barcellos · Florianópolis

**[Abrir o site](https://bernardo30001.github.io/felipe-barcellos-florianopolis/)**

Votação oficial de Felipe Barcellos (MISSÃO, 1414), candidato a deputado federal em Santa Catarina, no primeiro turno de 2026. Consulta aos dados do TSE em 6 de outubro de 2026.

O site mostra **3.587 votos em Florianópolis**, distribuídos por **62 bairros e localidades**, **139 locais de votação** e **1.207 seções apuradas**. Inclui busca, ordenação, detalhamento por local, exportação CSV e fontes.

## Critério territorial

“Bairro” é o campo `NM_BAIRRO` do local de votação no cadastro TSE, **não a residência dos eleitores**. Os nomes do cadastro são preservados, sem reunir localidades distintas. Seções agregadas não duplicam votos. As 20 seções remanejadas usam o local atual do cadastro, conferido com o código original no boletim.

O percentual exibido no ranking representa a parcela dos **3.587 votos do candidato na cidade** proveniente do bairro. Os cinco bairros/localidades com zero voto permanecem na lista.

## Fontes e reprodução

- [Resultado municipal oficial](https://resultados.tse.jus.br/oficial/ele2026/6259/dados/sc/sc81051-c0006-e006259-u.json)
- [Resultado estadual oficial](https://resultados.tse.jus.br/oficial/ele2026/6259/dados/sc/sc-c0006-e006259-u.json)
- [Cadastro de locais de votação 2026](https://cdn.tse.jus.br/estatistica/sead/odsele/eleitorado_locais_votacao/eleitorado_local_votacao_2026.zip)
- [Metodologia detalhada e reprodução dos boletins](research/README-dados.md)

`research/` contém insumos oficiais e scripts de reprodução. `site/secoes.json` preserva os votos e a fonte de cada boletim. `site/auditoria.json` contém a reconciliação dos totais. Os boletins foram decodificados e todas as candidaturas e legendas conferidas com o resultado municipal. As somas foram verificadas novamente em revisão independente.

Os dados são uma fotografia da consulta, sem atualização automática. Não há vínculo com o candidato ou com a Justiça Eleitoral.

## Desenvolvimento e publicação

Site estático em HTML, CSS e JavaScript, sem instalação de dependências. Para visualizar:

```sh
python3 -m http.server 8768 --directory site
```

Para conferir integridade:

```sh
python3 scripts/validate.py
node --check site/app.js
```

GitHub Pages publica `site/` pela ação definida em `.github/workflows/pages.yml` após cada atualização da branch `main`.
