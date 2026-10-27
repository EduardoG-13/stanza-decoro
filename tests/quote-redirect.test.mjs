import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFileSync} from 'node:fs';
const source=readFileSync(new URL('../assets/quote-redirect.js',import.meta.url),'utf8');
function redirect(search,hostedUrl='https://stanza-atendimento-820e4.web.app/orcamento.html'){
 const link={href:''};let target;
 const data={'#quote-config':{hostedUrl},'#catalog-references':{'sofa-organico':{},'sofa-contorno-marcado':{},'sofa-reto':{}},'#portfolio-references':['projeto-1','#nunca','projeto-48'],'#sofa-options':{modelId:'stanza-organic-01',fabrics:{linen:'Trama plana','boucle-mescla':'Bouclé mescla'},colors:{oliva:'Oliva',gelo:'Cinza gelo'},studies:{'stanza-organic-01':'sofa-organico','stanza-straight-01':'sofa-reto'}}};
 vm.runInNewContext(source,{URL,URLSearchParams,document:{querySelector:s=>s==='#open-secure-quote'?link:{textContent:JSON.stringify(data[s])}},location:{search,replace:url=>{target=url;}}});
 return target?new URL(target):null;
}
test('encaminha a referencia e a reforma sem levar dados pessoais ou parametros livres',()=>{
 const target=redirect('?referencia=sofa-contorno-marcado&servico=reforma&name=Pessoa&email=pessoa%40example.com&token=segredo');
 assert.equal(target.origin,'https://stanza-atendimento-820e4.web.app');
 assert.deepEqual([...target.searchParams], [['referencia','sofa-contorno-marcado'],['servico','reforma']]);
});
test('preserva apenas opcoes reconhecidas do estudo e ignora alteracoes arbitrarias',()=>{
 const target=redirect('?referencia=sofa-organico&estudo=stanza-organic-01&tecido=linen&cor=oliva&projeto=projeto-48');
 assert.equal(target.searchParams.get('tecido'),'linen');assert.equal(target.searchParams.get('cor'),'oliva');
 assert.equal(redirect('?referencia=sofa-organico&estudo=stanza-organic-01&tecido=__proto__&cor=constructor').searchParams.has('tecido'),false);
});
test('referencias e projetos desconhecidos nao sao encaminhados',()=>{
 assert.equal(redirect('?referencia=__proto__&projeto=projeto-999&servico=qualquer').search,'');
});
test('nao redireciona para outro dominio ou caminho',()=>{
 assert.equal(redirect('','https://example.invalid/orcamento.html'),null);
 assert.equal(redirect('','https://stanza-atendimento-820e4.web.app/qualquer'),null);
});
test('estudo 3D de outro modelo registrado segue com sua referencia; combinacoes trocadas sao descartadas',()=>{
 const t=redirect('?referencia=sofa-reto&estudo=stanza-straight-01&tecido=boucle-mescla&cor=gelo');
 assert.deepEqual([...t.searchParams],[['referencia','sofa-reto'],['estudo','stanza-straight-01'],['tecido','boucle-mescla'],['cor','gelo']]);
 const wrong=redirect('?referencia=sofa-organico&estudo=stanza-straight-01&tecido=linen&cor=oliva');
 assert.equal(wrong.searchParams.has('estudo'),false);assert.equal(wrong.searchParams.has('tecido'),false);
});
