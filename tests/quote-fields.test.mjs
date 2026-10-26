import {test} from 'node:test';
import assert from 'node:assert/strict';
import {formatPhone,formatPhoneInput,phoneDigits} from '../assets/quote-fields.js';
import {whatsappQuoteUrl} from '../assets/quote-message.js';
import {readFile} from 'node:fs/promises';

test('telefone se forma a cada digito, aceita fixo e celular e nao perde numeros',()=>{
  for(const [raw,expected] of [['',''],['1','(1'],['11','(11)'],['119','(11) 9'],['1197556','(11) 9755-6'],['1134567890','(11) 3456-7890'],['11975563037','(11) 97556-3037']]) assert.equal(formatPhone(raw),expected);
  const excess='(11) 97556-30378';assert.equal(phoneDigits(formatPhone(excess)),'119755630378');
});

test('colagem com pais 55 e diferenciada de DDD 55 nacional',()=>{
  for(const raw of ['+55 (11) 97556-3037','5511975563037']) assert.equal(formatPhone(raw),'(11) 97556-3037');
  assert.equal(formatPhone('55999990000'),'(55) 99999-0000');
  assert.equal(phoneDigits('(55) 99999-00001'),'559999900001');
});

test('edicao conserva posicao entre digitos e fim do telefone',()=>{
  assert.deepEqual(formatPhoneInput('11975563037',11),{value:'(11) 97556-3037',caret:15});
  assert.equal(formatPhoneInput('(11) 97556-3037',8).caret,8);
  assert.equal(formatPhoneInput('+55 (11) 97556-3037',10).caret,6);
  assert.equal(formatPhoneInput('(11) 97556-3037',0).caret,0);
});

test('link do WhatsApp leva resumo completo e protocolo sem exigir copiar',()=>{
  const summary='Serviço: Reforma\nPeça: Sofá\nNome: Teste & exemplo\nObservações: azul #2 + cinza';
  const url=new URL(whatsappQuoteUrl('5511975563037',summary,'ST-26-0001'));
  assert.equal(url.origin,'https://wa.me');assert.equal(url.pathname,'/5511975563037');
  assert.equal(url.searchParams.get('text'),'Projeto enviado pelo site · Protocolo: ST-26-0001\n\n'+summary);
  assert.equal(new URL(whatsappQuoteUrl('5511975563037',summary)).searchParams.get('text'),summary);
  assert.throws(()=>whatsappQuoteUrl('numero-invalido',summary));
});

test('cidades locais pertencem a cada UF e preservam os acentos do IBGE',async()=>{
  const data=JSON.parse(await readFile(new URL('../data/cities-br.json',import.meta.url),'utf8'));
  assert.equal(data.source,'https://servicodados.ibge.gov.br/api/v1/localidades');
  assert.equal(Object.keys(data.states).length,27);
  assert.ok(data.states.SP.cities.includes('São Paulo'));
  assert.ok(data.states.SP.cities.includes('São Sebastião'));
  assert.ok(data.states.RJ.cities.includes('Rio de Janeiro'));
  assert.equal(data.states.RJ.cities.includes('São Paulo'),false);
  for(const state of Object.values(data.states)) assert.equal(new Set(state.cities).size,state.cities.length);
});
