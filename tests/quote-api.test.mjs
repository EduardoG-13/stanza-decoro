import {test} from 'node:test';
import assert from 'node:assert/strict';
import {webcrypto} from 'node:crypto';
import {prepararEnvio,registrarEnvio} from '../assets/quote-api.js';
globalThis.location={hostname:'127.0.0.1'};
if(!globalThis.crypto)globalThis.crypto=webcrypto;
globalThis.FileReader=class {
  async readAsDataURL(file){this.result='data:image/png;base64,'+Buffer.from(await file.arrayBuffer()).toString('base64');this.onload();}
};
const config={mode:'emulator',endpoint:'http://127.0.0.1:5001/demo-stanza-pedidos/southamerica-east1/receberPedidoSite'};
test('preparação calcula hash, cria capacidade e conserva campos e fotos somente em memória',async()=>{
  const file={name:'peça.png',size:4,type:'image/png',arrayBuffer:async()=>Uint8Array.from([1,2,3,4]).buffer};
  const envio=await prepararEnvio({name:'Pessoa'},[file]);
  assert.equal(envio.token.length,64);assert.match(envio.chave,/^[a-f0-9-]{36}$/);assert.equal(envio.fotos[0].sha256,'9f64a747e1b97f131fabb6b447296c9b6f0201e79fb3c5356e6c77e89b6a806a');
  assert.equal(envio.files[0],file);assert.equal(envio.confirmacaoIniciada,false);
});
test('perda da resposta final usa a mesma identidade e recupera o recibo na repetição',async()=>{
  const envio=await prepararEnvio({name:'Pessoa'},[]);let concluiu=false;const identidades=[];
  globalThis.fetch=async(url,request)=>{
    const body=JSON.parse(request.body);identidades.push(body.entrada.chave);
    if(body.acao==='iniciar')return {ok:true,json:async()=>concluiu?{concluido:true,protocolo:'ST-2027-TESTE'}:{concluido:false}};
    concluiu=true;throw new TypeError('A conexão caiu depois do registro');
  };
  await assert.rejects(registrarEnvio(config,envio,()=>{}));assert.equal(envio.confirmacaoIniciada,true);
  const recibo=await registrarEnvio(config,envio,()=>{});assert.equal(recibo.protocolo,'ST-2027-TESTE');assert.equal(new Set(identidades).size,1);
});
test('modo de demonstração não permite enviar para um servidor real nem executar fora do computador local',async()=>{
  const envio=await prepararEnvio({},[]);
  await assert.rejects(registrarEnvio({...config,endpoint:'https://example.com'},envio,()=>{}));
  globalThis.location={hostname:'stanzadecoro.com.br'};
  await assert.rejects(registrarEnvio(config,envio,()=>{}));
  globalThis.location={hostname:'127.0.0.1'};
});
