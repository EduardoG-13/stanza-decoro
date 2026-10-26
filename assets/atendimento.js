import { initializeApp } from 'https://www.gstatic.com/firebasejs/13.0.0/firebase-app.js';
import { getAuth, setPersistence, inMemoryPersistence, signInWithEmailAndPassword, signOut, onAuthStateChanged } from 'https://www.gstatic.com/firebasejs/13.0.0/firebase-auth.js';
import { getFunctions, httpsCallable } from 'https://www.gstatic.com/firebasejs/13.0.0/firebase-functions.js';
document.documentElement.classList.add('js');
const $=s=>document.querySelector(s);
const config=await fetch('/assets/atendimento-publico.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('Configuração indisponível.');return r.json();});
const app=initializeApp(config.firebase,'stanza-atendimento'),auth=getAuth(app),functions=getFunctions(app,'southamerica-east1');
await setPersistence(auth,inMemoryPersistence);
const situations={novo:'Novo',em_atendimento:'Em atendimento',aguardando_cliente:'Aguardando cliente',proposta_preparada:'Proposta preparada',encerrado:'Encerrado'};
let cursor=null,version=0,photoUrl='',photoTrigger=null;
const call=async(name,data)=>(await httpsCallable(functions,name)(data)).data;
function node(tag,text,className){const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(className)e.className=className;return e;}
function error(message=''){$('#erro').textContent=message;$('#erro').hidden=!message;}
function status(message){$('#status').textContent=message;}
function closePhoto(){if($('#foto').open)$('#foto').close();$('#imagem').removeAttribute('src');if(photoUrl)URL.revokeObjectURL(photoUrl);photoUrl='';if(photoTrigger?.isConnected)photoTrigger.focus();photoTrigger=null;}
$('#fechar-foto').addEventListener('click',closePhoto);
$('#foto').addEventListener('cancel',e=>{e.preventDefault();closePhoto();});
onAuthStateChanged(auth,user=>{
 version++;closePhoto();$('#lista').replaceChildren();$('#detalhe').replaceChildren();$('#detalhe').hidden=true;error();status('');
 $('#login').hidden=!!user;$('#painel').hidden=!user;$('#sair').hidden=!user;
 if(user){$('#pessoa').textContent='ATENDIMENTO · '+(user.displayName||'Stanza');void list(false);}
});
$('#login-form').addEventListener('submit',async e=>{
 e.preventDefault();const form=e.currentTarget,button=form.querySelector('button');button.disabled=true;error();status('Verificando acesso…');
 try{const data=new FormData(form);await signInWithEmailAndPassword(auth,String(data.get('email')).trim(),String(data.get('password')));form.reset();}
 catch{error('Não foi possível entrar. Confira o e-mail, a senha e se o acesso está ativo.');status('');}
 finally{button.disabled=false;form.elements.password.value='';}
});
$('#sair').addEventListener('click',async()=>{await signOut(auth);});
async function list(more){
 const current=++version;if(!auth.currentUser)return;error();status('Carregando projetos…');$('#mais').disabled=true;
 if(!more){cursor=null;$('#lista').replaceChildren();$('#mais').hidden=true;}
 const data=new FormData($('#pesquisa'));
 try{
  const response=await call('listarPedidosSite',{...(data.get('situacao')?{situacao:data.get('situacao')}:{}),...(data.get('protocolo')?.trim()?{protocolo:data.get('protocolo').trim().toUpperCase()}:{}),...(more&&cursor?{cursor}:{})});
  if(current!==version||!auth.currentUser)return;
  for(const item of response.itens){
   const button=node('button',undefined,'pedido-card');button.type='button';
   button.append(node('strong',item.protocolo),node('span',item.nome,'pedido-nome'),node('span',item.servico+' · '+item.peca),node('span',item.cidade+'/'+item.uf),node('span',(situations[item.situacao]||item.situacao)+' · '+new Date(item.criadoEm).toLocaleString('pt-BR')));
   button.addEventListener('click',()=>void detail(item.id));$('#lista').append(button);
  }
  cursor=response.cursor;$('#mais').hidden=!cursor;status($('#lista').childElementCount?'Selecione um protocolo para ver o projeto e as fotos.':'Nenhum pedido encontrado com este filtro.');
 }catch(e){if(current===version){error(e.code==='functions/permission-denied'?'Este acesso não tem permissão para consultar os pedidos do site.':e.code==='functions/invalid-argument'?'Digite o protocolo completo, por exemplo ST-26-0001.':'Não foi possível carregar. Tente atualizar a lista.');status('');}}
 finally{$('#mais').disabled=false;}
}
$('#pesquisa').addEventListener('submit',e=>{e.preventDefault();void list(false);});
$('#atualizar').addEventListener('click',()=>void list(false));
$('#mais').addEventListener('click',()=>void list(true));
async function detail(id){
 const current=++version;error();status('Abrindo projeto…');closePhoto();
 try{
  const p=await call('obterPedidoSite',{id});if(current!==version||!auth.currentUser)return;
  const d=p.dados,container=$('#detalhe');container.replaceChildren();
  container.append(node('span','PROJETO · '+p.protocolo,'eyebrow'),node('h2',d.name),node('p',(situations[p.situacao]||p.situacao)+' · Recebido em '+new Date(p.criadoEm).toLocaleString('pt-BR')));
  const dl=node('dl');
  for(const [label,value] of [['Serviço',d.service],['Peça',d.piece],['Referência',d.reference],['Medidas aproximadas',d.dimensions],['Cidade',d.city+'/'+d.state],['Período desejado',d.period],['WhatsApp',d.phone],['E-mail',d.email],['Observações',d.details]]){
   const item=node('div');item.append(node('dt',label),node('dd',value||'Não informado'));dl.append(item);
  }container.append(dl);
  const actions=node('div',undefined,'actions');
  for(const [label,href] of [['Conversar no WhatsApp ↗','https://wa.me/55'+d.phone.replace(/\D/g,'').replace(/^55(?=\d{10,11}$)/,'')+'?text='+encodeURIComponent('Olá, '+d.name+'! Somos da Stanza Decoro. Recebemos seu projeto '+p.protocolo+'.')],['Abrir e-mail ↗','mailto:'+d.email]]){
   const a=node('a',label,'button button-outline');a.href=href;a.target='_blank';a.rel='noopener noreferrer';actions.append(a);
  }container.append(actions,node('h3','Fotos enviadas'));
  const photos=node('div',undefined,'actions');
  if(!p.fotos.length)photos.append(node('p','Este pedido foi enviado sem fotos.'));
  p.fotos.forEach((photo,index)=>{
   const button=node('button','Abrir foto '+(index+1),'button button-outline');button.type='button';
   button.addEventListener('click',async()=>{
    const photoVersion=version;button.disabled=true;error();status('Carregando foto privada…');
    try{
     const image=await call('obterFotoPedidoSite',{id,indice:index});if(photoVersion!==version||!auth.currentUser)return;
     closePhoto();const binary=atob(image.conteudo),bytes=Uint8Array.from(binary,c=>c.charCodeAt(0));
     photoUrl=URL.createObjectURL(new Blob([bytes],{type:'image/jpeg'}));photoTrigger=button;
     $('#foto-titulo').textContent='Foto '+(index+1)+' · '+p.protocolo;$('#imagem').alt='Foto '+(index+1)+' enviada com o projeto '+p.protocolo;$('#imagem').src=photoUrl;$('#foto').showModal();status('');
    }catch{if(photoVersion===version){error('Não foi possível abrir a foto. Entre novamente se a sessão tiver terminado.');status('');}}
    finally{button.disabled=false;}
   });photos.append(button);
  });container.append(photos);
  const email={pendente:'Aviso por e-mail na fila.',aceito_pelo_servidor:'Aviso aceito pelo servidor de e-mail.',falha:'O aviso por e-mail falhou. O pedido continua registrado.'};
  container.append(node('p',email[p.aviso]||'Aviso por e-mail aguardando processamento.','field-note'));
  container.hidden=false;container.focus();container.scrollIntoView({behavior:'instant',block:'start'});status('');
 }catch{if(current===version){error('Não foi possível abrir o projeto. Atualize a lista e tente novamente.');status('');}}
}

$('#login-fields').disabled=false;
