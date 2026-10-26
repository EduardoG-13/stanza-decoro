// O link preenche a conversa; o envio no WhatsApp continua sendo confirmado pela pessoa.
export function whatsappQuoteUrl(number, summary, protocol = '') {
  if (!/^\d{10,15}$/.test(number)) throw new Error('Contato de WhatsApp invalido.');
  const text = protocol
    ? 'Projeto enviado pelo site · Protocolo: ' + protocol + '\n\n' + summary
    : summary;
  return 'https://wa.me/' + number + '?text=' + encodeURIComponent(text);
}
