#!/usr/bin/env python3
"""Extract the municipality's public polling-place fields from the TSE ZIP.

Usage: python3 prepare_register.py /path/to/eleitorado_local_votacao_2026.zip
The archive is downloadable from the URL printed with --help.
"""
from pathlib import Path
import argparse,csv,io,json,zipfile
URL='https://cdn.tse.jus.br/estatistica/sead/odsele/eleitorado_locais_votacao/eleitorado_local_votacao_2026.zip'
FIELDS=['NR_TURNO','CD_MUNICIPIO','NM_MUNICIPIO','NR_ZONA','NR_SECAO','NR_SECAO_PRINCIPAL','DS_TIPO_SECAO_AGREGADA','NR_LOCAL_VOTACAO','NM_LOCAL_VOTACAO','DS_ENDERECO','NM_BAIRRO','NR_LATITUDE','NR_LONGITUDE','DS_TIPO_LOCAL','QT_ELEITOR_SECAO','QT_ELEITOR_ELEICAO_FEDERAL','QT_ELEITOR_ELEICAO_ESTADUAL','DS_SITU_SECAO','NR_LOCAL_VOTACAO_ORIGINAL','NM_LOCAL_VOTACAO_ORIGINAL']
ap=argparse.ArgumentParser(description=URL);ap.add_argument('zip',type=Path);ap.add_argument('--output',type=Path,default=Path(__file__).resolve().parent/'cadastro-florianopolis.json');args=ap.parse_args()
with zipfile.ZipFile(args.zip) as z:
    name=next(n for n in z.namelist() if n.endswith('_SC.csv'))
    with z.open(name) as raw:
        rows=[{k:r[k] for k in FIELDS} for r in csv.DictReader(io.TextIOWrapper(raw,encoding='latin1'),delimiter=';') if r['CD_MUNICIPIO']=='81051' and r['NR_TURNO']=='1']
args.output.write_text(json.dumps(rows,ensure_ascii=False,indent=2))
print(f'{len(rows)} registration rows written to {args.output}')
