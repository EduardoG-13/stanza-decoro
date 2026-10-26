"""Atualiza a lista publica de municipios com a API oficial do IBGE.

Executar explicitamente; a compilacao normal e o formulario usam a copia local.
"""
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen
import gzip, json

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://servicodados.ibge.gov.br/api/v1/localidades'

def read(path):
    with urlopen(BASE + path, timeout=60) as response:
        payload = response.read()
        if payload.startswith(b'\x1f\x8b'):
            payload = gzip.decompress(payload)
        return json.loads(payload)

if __name__ == '__main__':
    states = read('/estados?orderBy=nome')
    cities = read('/municipios?orderBy=nome')
    assert len(states) == 27 and len({state['sigla'] for state in states}) == 27
    assert len({city['id'] for city in cities}) == len(cities)
    result = {}
    for state in states:
        names = [city['nome'] for city in cities if str(city['id']).startswith(str(state['id']))]
        assert names and len(names) == len(set(names)), state['sigla']
        result[state['sigla']] = {'name': state['nome'], 'cities': names}
    assert sum(len(state['cities']) for state in result.values()) == len(cities)
    snapshot = {'source': BASE, 'retrievedAt': datetime.now(timezone.utc).isoformat(), 'states': result}
    (ROOT/'data/cities-br.json').write_text(json.dumps(snapshot, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(f'IBGE: {len(result)} UFs, {len(cities)} municipios; copia local atualizada.')
