#!/usr/bin/env python3
"""Rebuild neighborhood totals from TSE ballot files and polling-place register.

Usage: python3 build_data.py --bu-dir PATH
Missing BUs are downloaded from manifesto-boletins.json when --download is set.
Only Python standard library is required. Output is written beside this script.
"""
from pathlib import Path
import argparse, collections, csv, hashlib, json, urllib.request

ROOT=Path(__file__).resolve().parent
CITY='81051'; NUMBER=1414; OFFICE=6
COUNT_FIELDS=['votes','validVotes','nominalValidVotes','partyVotes','blankVotes','nullVotes','technicalNullVotes','subJudiceVotes','otherInvalidVotes','turnout','electorate','sections','sectionsWithCandidateVotes']

def read(name): return json.loads((ROOT/name).read_text())
def write(name,value): (ROOT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def parse(data):
    out=[];i=0
    while i<len(data):
        tag=data[i];i+=1;n=data[i];i+=1
        if n&128:
            nb=n&127
            if not nb: raise ValueError('Indefinite ASN.1 lengths are unsupported')
            n=int.from_bytes(data[i:i+nb]);i+=nb
        val=data[i:i+n];i+=n
        if len(val)!=n: raise ValueError('Truncated ASN.1 value')
        if tag&32: val=parse(val)
        elif tag in (2,10,129,130,131): val=int.from_bytes(val,signed=True)
        elif tag==27: val=val.decode()
        out.append((tag,val))
    return out

def decode(data):
    root=parse(data)[0][1]
    assert root[1]==(10,2),'Nonofficial envelope'
    inner=parse(next(v for k,v in root if k==4))[0][1]
    assert inner[1]==(10,2),'Nonofficial ballot'
    ident=inner[3][1];mz=ident[0][1]
    meta={'municipality':mz[0][1],'zone':mz[1][1],'originalLocationCode':ident[1][1],'section':ident[2][1],'emittedAt':inner[4][1]}
    election_lists=[v for k,v in inner if k==48 and v and isinstance(v[0][1],list) and v[0][1] and v[0][1][0][0]==2 and v[0][1][0][1] in (6257,6259)]
    assert len(election_lists)==1
    ele=next(v for k,v in election_lists[0] if v[0]==(2,6259))
    meta['electorate']=ele[1][1]
    results=next(v for k,v in ele if k==48)
    cargo=[]
    for _,v in results:
        for _,c in v[2][1]:
            if c[0]==(129,OFFICE): cargo.append(c);meta['turnout']=v[1][1]
    assert len(cargo)==1,meta
    votes=[]
    for _,v in cargo[0][2][1]:
        ident=next((val for tag,val in v if tag==163),None)
        votes.append({'kind':v[0][1],'votes':v[1][1],'party':ident[0][1] if ident else None,'number':ident[1][1] if ident else None})
    return meta,votes

def add(target,row):
    for k in COUNT_FIELDS: target[k]=target.get(k,0)+row[k]
def coordinate(value):
    try:
        n=float(value.replace(',','.'));return None if n in (-1,-3) else n
    except (ValueError,AttributeError): return None

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--bu-dir',type=Path,default=ROOT/'boletins');ap.add_argument('--download',action='store_true');args=ap.parse_args()
    regs=read('cadastro-florianopolis.json');manifest=read('manifesto-boletins.json');official=read('municipio-oficial.json');state=read('estado-oficial.json')
    parties=[p for a in official['carg'][0]['agr'] for p in a['par']]
    candidates={int(c['n']):c for p in parties for c in p['cand']}
    valid_parties={int(p['n']) for p in parties if p['dvt']=='Válido (legenda)'}
    candidate=candidates[NUMBER]
    state_party,state_candidate=next((p,c) for a in state['carg'][0]['agr'] for p in a['par'] for c in p['cand'] if c['n']==str(NUMBER))
    register={(int(r['NR_ZONA']),int(r['NR_SECAO'])):r for r in regs}
    assert len(register)==len(regs),'Duplicate registration keys'
    neighborhoods={};locations={};aggregates=collections.defaultdict(list)
    for r in regs:
        assert r['CD_MUNICIPIO']==CITY and r['NR_TURNO']=='1'
        neighborhood=r['NM_BAIRRO'];zone=int(r['NR_ZONA']);local=int(r['NR_LOCAL_VOTACAO']);lid=f'{zone}-{local}'
        if r['DS_TIPO_SECAO_AGREGADA']=='Agregada': aggregates[(zone,int(r['NR_SECAO_PRINCIPAL']))].append(int(r['NR_SECAO']))
        if neighborhood not in neighborhoods:
            neighborhoods[neighborhood]={'name':neighborhood,**{k:0 for k in COUNT_FIELDS},'registeredSections':0,'locationIds':set()}
        nb=neighborhoods[neighborhood];nb['registeredSections']+=1;nb['locationIds'].add(lid)
        if lid not in locations:
            locations[lid]={'id':lid,'name':r['NM_LOCAL_VOTACAO'],'zone':zone,'number':local,'neighborhood':neighborhood,'address':r['DS_ENDERECO'],'latitude':coordinate(r['NR_LATITUDE']),'longitude':coordinate(r['NR_LONGITUDE']),**{k:0 for k in COUNT_FIELDS},'sectionNumbers':[],'aggregatedSectionNumbers':[],'registeredSections':0}
        assert locations[lid]['neighborhood']==neighborhood,'Conflicting location neighborhood'
        locations[lid]['registeredSections']+=1
    seen=set();section_rows=[];seen_candidate=collections.Counter();seen_party=collections.Counter();missing=[];relocated=[]
    for m in manifest:
        key=(m['zona'],m['secao']);assert key not in seen,'Duplicate ballot';seen.add(key)
        path=args.bu_dir/m['arquivo']
        if not path.exists() and args.download:
            path.parent.mkdir(parents=True,exist_ok=True)
            urllib.request.urlretrieve(m['url'],path)
        raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==m['sha256'],f'Hash mismatch {path.name}'
        bu,votes=decode(raw)
        assert (bu['municipality'],bu['zone'],bu['section'])==(int(CITY),*key)
        if key not in register: missing.append(m);continue
        reg=register[key];assert reg['DS_TIPO_SECAO_AGREGADA']=='Principal'
        lid=f"{bu['zone']}-{int(reg['NR_LOCAL_VOTACAO'])}";lc=locations[lid]
        is_relocated=bu['originalLocationCode']!=lc['number']
        assert not is_relocated or bu['originalLocationCode']==int(reg['NR_LOCAL_VOTACAO_ORIGINAL'])
        row={k:0 for k in COUNT_FIELDS}
        row.update({'zone':bu['zone'],'section':bu['section'],'locationId':lid,'location':lc['name'],'neighborhood':lc['neighborhood'],'originalLocationCode':bu['originalLocationCode'],'relocated':is_relocated,'turnout':bu['turnout'],'electorate':bu['electorate'],'sections':1,'aggregatedSections':sorted(aggregates[key]),'source':m['url'],'sha256':m['sha256'],'emittedAt':bu['emittedAt']})
        for v in votes:
            kind,n,q,p=v['kind'],v['number'],v['votes'],v['party']
            if kind==1:
                seen_candidate[n]+=q
                if n in candidates and candidates[n]['dvt']=='Válido':
                    row['nominalValidVotes']+=q
                    if n==NUMBER: row['votes']+=q
                elif n not in candidates: row['technicalNullVotes']+=q
                elif candidates[n]['dvt']=='Anulado sub judice': row['subJudiceVotes']+=q
                else: row['otherInvalidVotes']+=q
            elif kind==2: row['blankVotes']+=q
            elif kind==3: row['nullVotes']+=q
            elif kind==4:
                seen_party[p]+=q
                if p in valid_parties: row['partyVotes']+=q
                else: row['otherInvalidVotes']+=q
            else: raise ValueError(f'Unknown vote kind {kind}')
        row['validVotes']=row['nominalValidVotes']+row['partyVotes'];row['nullVotes']+=row['technicalNullVotes'];row['sectionsWithCandidateVotes']=int(row['votes']>0)
        assert row['turnout']==sum(row[k] for k in ('validVotes','blankVotes','nullVotes','subJudiceVotes','otherInvalidVotes')),(key,'Ballot totals')
        add(lc,row);add(neighborhoods[row['neighborhood']],row)
        lc['sectionNumbers'].append(row['section']);lc['aggregatedSectionNumbers'].extend(row['aggregatedSections'])
        section_rows.append(row)
        if is_relocated: relocated.append({'zone':key[0],'section':key[1],'oldLocation':bu['originalLocationCode'],'currentLocation':lc['number'],'neighborhood':lc['neighborhood']})
    assert not missing,missing
    expected_principals={(int(r['NR_ZONA']),int(r['NR_SECAO'])) for r in regs if r['DS_TIPO_SECAO_AGREGADA']=='Principal'}
    assert seen==expected_principals,('Registration/ballot coverage',len(seen),len(expected_principals),seen^expected_principals)
    totals={k:sum(s[k] for s in section_rows) for k in COUNT_FIELDS}
    expected={'votes':int(candidate['vap']),'validVotes':int(official['v']['vv']),'nominalValidVotes':int(official['v']['vnom']),'partyVotes':int(official['v']['vl']),'blankVotes':int(official['v']['vb']),'nullVotes':int(official['v']['tvn']),'technicalNullVotes':int(official['v']['vnt']),'subJudiceVotes':int(official['v']['vansj']),'turnout':int(official['e']['c']),'electorate':int(official['e']['te']),'sections':int(official['s']['st'])}
    assert all(totals[k]==v for k,v in expected.items()),(totals,expected)
    for n,c in candidates.items(): assert seen_candidate[n]==int(c['vap']),(n,seen_candidate[n],c['vap'])
    for p in parties: assert seen_party[int(p['n'])]==int(p['tvtl']),(p['n'],seen_party[int(p['n'])],p['tvtl'])
    for lc in locations.values():
        lc['sectionNumbers'].sort();lc['aggregatedSectionNumbers'].sort()
        lc['shareOfCandidateCityVotes']=lc['votes']/totals['votes']*100
        lc['shareOfValidVotes']=lc['votes']/lc['validVotes']*100 if lc['validVotes'] else 0
    for nb in neighborhoods.values():
        nb['locations']=[locations[i] for i in sorted(nb.pop('locationIds'),key=lambda i:(-locations[i]['votes'],locations[i]['name']))]
        nb['locationCount']=len(nb['locations'])
        nb['shareOfCandidateCityVotes']=nb['votes']/totals['votes']*100
        nb['shareOfValidVotes']=nb['votes']/nb['validVotes']*100 if nb['validVotes'] else 0
    sources=[
      {'title':'TSE · Resultado oficial de deputado federal em Florianópolis','url':'https://resultados.tse.jus.br/oficial/ele2026/6259/dados/sc/sc81051-c0006-e006259-u.json'},
      {'title':'TSE · Resultado oficial de deputado federal em Santa Catarina','url':'https://resultados.tse.jus.br/oficial/ele2026/6259/dados/sc/sc-c0006-e006259-u.json'},
      {'title':'TSE · Cadastro de locais e seções eleitorais de 2026','url':'https://cdn.tse.jus.br/estatistica/sead/odsele/eleitorado_locais_votacao/eleitorado_local_votacao_2026.zip'},
      {'title':'TSE · Portal de dados abertos — eleitorado 2026','url':'https://dadosabertos.tse.jus.br/dataset/eleitorado-2026'},
      {'title':'TSE · Configuração de seções de Santa Catarina','url':'https://resultados.tse.jus.br/oficial/ele2026/arquivo-urna/3220/config/sc/sc-p003220-cs.json'},
      {'title':'TSE · Documentação de divulgação de resultados','url':'https://www.tse.jus.br/eleicoes/informacoes-tecnicas-sobre-a-divulgacao-de-resultados'}]
    methodology=[
      'Os votos de Felipe Barcellos (1414) foram extraídos dos boletins de urna oficiais totalizados do primeiro turno de 2026, cargo 6 (deputado federal), eleição 6259, pleito 3220.',
      'Bairro é o nome do bairro ou localidade do local de votação informado no cadastro eleitoral do TSE. Não é o bairro de residência do eleitor e pode não coincidir com divisões administrativas municipais.',
      'A ligação entre urna e cadastro usa município + zona eleitoral + seção. Quando há remanejamento, utiliza-se o local atual do cadastro, conferindo o código original do local no boletim de urna.',
      'Cada boletim corresponde a uma seção principal. Os votos das seções agregadas já estão no boletim da seção principal e não são somados novamente.',
      'Todos os bairros/localidades com locais no cadastro do município foram incluídos, mesmo quando a soma de votos no candidato é zero. Seções apuradas incluem as que não registraram votos nele.',
      'Participação na votação municipal do candidato = votos no bairro / 3.587. Percentual dos votos válidos no bairro = votos do candidato / votos nominais e de legenda válidos naquele bairro.',
      'O percentual divulgado no resultado oficial do TSE usa votos concorrentes, que também incluem votos anulados sub judice; por isso pode diferir do percentual sobre votos válidos calculado neste painel.',
      'A soma das 1.207 urnas foi conferida com o resultado oficial municipal para cada candidatura, legendas, comparecimento, eleitorado, válidos, brancos e nulos. Os arquivos são uma fotografia da consulta, sem atualização automática.'
    ]
    output={'candidate':{'name':candidate['nmu'],'fullName':candidate['nm'],'number':NUMBER,'party':state_party['sg'],'year':2026,'office':'Deputado federal','state':'Santa Catarina','stateAbbreviation':'SC','stateVotes':int(state_candidate['vap']),'cityVotes':int(candidate['vap']),'status':state_candidate['st'],'cityOfficialPercentage':float(candidate['pvapn'].replace(',','.')),'stateOfficialPercentage':float(state_candidate['pvapn'].replace(',','.'))},
      'election':{'date':'2026-10-04','round':1,'year':2026,'code':6259,'officeCode':OFFICE,'pollCode':3220,'updatedAt':'2026-10-04T21:56:30-03:00','consultedAt':'2026-10-06','registrationGeneratedAt':'2026-10-05T06:29:34-03:00','municipality':'Florianópolis','municipalityCode':CITY},
      'coverage':{'sectionCount':len(section_rows),'sectionsWithCandidateVotes':totals['sectionsWithCandidateVotes'],'registeredSectionCount':len(regs),'aggregatedSectionCount':len(regs)-len(section_rows),'locationCount':len(locations),'neighborhoodCount':len(neighborhoods),'unmatchedVotes':0,'unmatchedSections':0,'unmatchedLocations':0,'countedPercentage':100,'relocatedSections':len(relocated),'zeroVoteNeighborhoods':sum(n['votes']==0 for n in neighborhoods.values()),'allNeighborhoodsIncluded':True},
      'totals':totals,'neighborhoods':sorted(neighborhoods.values(),key=lambda n:(-n['votes'],n['name'])),'sources':sources,'methodology':methodology}
    write('data.json',output);write('secoes.json',sorted(section_rows,key=lambda r:(r['zone'],r['section'])))
    audit={'passed':True,'candidateVotes':totals['votes'],'officialCandidateVotes':int(candidate['vap']),'allCandidatesReconciled':len(candidates),'allPartiesReconciled':len(parties),'registrationKey':'municipality + zone + section','unmatchedSections':0,'sha256VerifiedBallots':len(manifest),'expectedTotals':expected,'actualTotals':totals,'relocatedSections':relocated,'aggregatedSections':[{'zone':k[0],'principal':k[1],'aggregated':sorted(v)} for k,v in aggregates.items() if v],'zeroVoteNeighborhoods':[n['name'] for n in neighborhoods.values() if n['votes']==0]}
    write('auditoria.json',audit)
    with (ROOT/'bairros.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.writer(f,delimiter=';');w.writerow(['bairro_localidade','votos_felipe_barcellos','participacao_votos_candidato_municipio_pct','votos_validos_bairro','percentual_validos_bairro','secoes_apuradas','secoes_com_votos_candidato','locais','ano','turno'])
        for n in output['neighborhoods']: w.writerow([n['name'],n['votes'],round(n['shareOfCandidateCityVotes'],6),n['validVotes'],round(n['shareOfValidVotes'],6),n['sections'],n['sectionsWithCandidateVotes'],n['locationCount'],2026,1])
    with (ROOT/'secoes.csv').open('w',newline='',encoding='utf-8-sig') as f:
        fields=['zone','section','neighborhood','location','votes','validVotes','turnout','electorate','relocated','source','sha256'];w=csv.DictWriter(f,fieldnames=fields,delimiter=';',extrasaction='ignore');w.writeheader();w.writerows(section_rows)
    print(json.dumps({'coverage':output['coverage'],'totals':totals,'top10':[(n['name'],n['votes']) for n in output['neighborhoods'][:10]],'auditPassed':True},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
