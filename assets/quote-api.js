/* Registro opcional. O modo manual continua disponível sem Firebase no navegador. */
let appCheckPromise;
export function protocoloValido(valor) {
  // Recibos antigos continuam válidos quando uma resposta anterior precisa ser recuperada.
  if (typeof valor !== 'string' || /\s/.test(valor)) return false;
  if (/^ST-\d{2}-\d{4,16}$/.test(valor)) {
    const numero = Number(valor.slice(6));
    return Number.isSafeInteger(numero) && numero > 0 && String(numero).padStart(4,'0') === valor.slice(6);
  }
  return /^ST-\d{4}-[A-F0-9]{8}-[A-F0-9]{4}-4[A-F0-9]{3}-[89AB][A-F0-9]{3}-[A-F0-9]{12}$/.test(valor);
}
async function appCheckToken(config) {
  if (config.mode === 'emulator') {
    const url = new URL(config.endpoint);
    if (!['127.0.0.1','localhost'].includes(location.hostname) || !['127.0.0.1','localhost'].includes(url.hostname)
      || !/^\/demo-[^/]+\/southamerica-east1\/receberPedidoSite$/.test(url.pathname)) throw new Error('A demonstração exige o servidor local de testes.');
    return '';
  }
  if (config.mode !== 'firebase' || !config.firebase?.appId || !config.recaptchaSiteKey || new URL(config.endpoint).protocol !== 'https:') throw new Error('O recebimento pelo site ainda não está configurado. Continue pelo WhatsApp.');
  if (!appCheckPromise) appCheckPromise = Promise.all([
    import('https://www.gstatic.com/firebasejs/13.0.0/firebase-app.js'),
    import('https://www.gstatic.com/firebasejs/13.0.0/firebase-app-check.js'),
  ]).then(([sdk,check])=>{
    const app = sdk.initializeApp(config.firebase,'stanza-site');
    const instance = check.initializeAppCheck(app,{provider:new check.ReCaptchaEnterpriseProvider(config.recaptchaSiteKey),isTokenAutoRefreshEnabled:true});
    return {check,instance};
  }).catch(error=>{appCheckPromise=undefined;throw error;});
  const {check,instance} = await appCheckPromise;
  return (await check.getToken(instance)).token;
}
export async function prepararEnvio(dados,files) {
  const token = [...crypto.getRandomValues(new Uint8Array(32))].map(v=>v.toString(16).padStart(2,'0')).join('');
  const fotos = [];
  for (const file of files) {
    const bytes = new Uint8Array(await file.arrayBuffer());
    const sha = await crypto.subtle.digest('SHA-256',bytes);
    const sha256 = [...new Uint8Array(sha)].map(v=>v.toString(16).padStart(2,'0')).join('');
    fotos.push({nome:file.name,tamanho:file.size,mimeType:file.type,sha256});
  }
  return {chave:crypto.randomUUID(),token,dados,fotos,files,confirmacaoIniciada:false};
}
const base64 = file => new Promise((resolve,reject)=>{
  const reader=new FileReader();reader.onload=()=>resolve(String(reader.result).split(',')[1]);reader.onerror=()=>reject(new Error('Não foi possível ler a foto.'));reader.readAsDataURL(file);
});
export async function registrarEnvio(config,envio,progresso) {
  const chamar = async (acao,entrada) => {
    const token = await appCheckToken(config); const controller = new AbortController();
    const tempo = setTimeout(()=>controller.abort(),90000);
    try {
      const resposta=await fetch(config.endpoint,{method:'POST',credentials:'omit',cache:'no-store',signal:controller.signal,
        headers:{'Content-Type':'application/json',...(token?{'X-Firebase-AppCheck':token}:{})},body:JSON.stringify({acao,entrada})});
      const dados=await resposta.json();
      if(!resposta.ok)throw new Error(dados.erro||'O envio não foi confirmado. Tente novamente.');
      return dados;
    } finally {clearTimeout(tempo);}
  };
  progresso('Preparando o registro…');
  const inicio=await chamar('iniciar',{chave:envio.chave,token:envio.token,dados:envio.dados,fotos:envio.fotos});
  if(inicio.concluido)return inicio;
  for(let indice=0;indice<envio.files.length;indice++) {
    progresso(`Enviando foto ${indice+1} de ${envio.files.length}…`);
    await chamar('foto',{chave:envio.chave,token:envio.token,indice,conteudo:await base64(envio.files[indice])});
  }
  progresso('Confirmando o recebimento…');envio.confirmacaoIniciada=true;
  return chamar('concluir',{chave:envio.chave,token:envio.token});
}
