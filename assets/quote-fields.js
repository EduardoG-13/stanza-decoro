// Apenas dados publicos de municipios sao carregados; nenhum contato e enviado aqui.
function parsePhone(value) {
  const digits = String(value).replace(/\D/g, '');
  const country = !String(value).trimStart().startsWith('(') && digits.startsWith('55') && (digits.length === 12 || digits.length === 13);
  return {digits: country ? digits.slice(2) : digits, removed: country ? 2 : 0};
}

export const phoneDigits = value => parsePhone(value).digits;

export function formatPhone(value) {
  const digits = phoneDigits(value);
  if (!digits) return '';
  if (digits.length < 2) return '(' + digits;
  const area = '(' + digits.slice(0, 2) + ')';
  const number = digits.slice(2);
  if (!number) return area;
  const split = number.length > 8 ? 5 : 4;
  return area + ' ' + number.slice(0, split) + (number.length > split ? '-' + number.slice(split) : '');
}

export function formatPhoneInput(value, caret = value.length) {
  const formatted = formatPhone(value);
  if (caret === value.length) return {value: formatted, caret: formatted.length};
  const count = Math.max(0, value.slice(0, caret).replace(/\D/g, '').length - parsePhone(value).removed);
  let position = 0, seen = 0;
  while (position < formatted.length && seen < count) {
    if (/\d/.test(formatted[position])) seen++;
    position++;
  }
  return {value: formatted, caret: position};
}

export function initializeQuoteFields(form) {
  const phone = form.elements.namedItem('phone');
  const apply = () => {
    const result = formatPhoneInput(phone.value, phone.selectionStart ?? phone.value.length);
    phone.value = result.value;
    phone.setSelectionRange(result.caret, result.caret);
  };
  phone.addEventListener('input', event => { if (!event.isComposing) apply(); });
  phone.addEventListener('compositionend', apply);
  phone.addEventListener('beforeinput', event => {
    if (!['deleteContentBackward','deleteContentForward'].includes(event.inputType) || phone.selectionStart !== phone.selectionEnd) return;
    const backward = event.inputType === 'deleteContentBackward';
    const cursor = phone.selectionStart;
    let index = backward ? cursor - 1 : cursor;
    if (index < 0 || index >= phone.value.length || /\d/.test(phone.value[index])) return;
    while (index >= 0 && index < phone.value.length && !/\d/.test(phone.value[index])) index += backward ? -1 : 1;
    if (index < 0 || index >= phone.value.length) return;
    event.preventDefault();
    const result = formatPhoneInput(phone.value.slice(0,index) + phone.value.slice(index+1), backward ? index : cursor);
    phone.value = result.value;
    phone.setSelectionRange(result.caret,result.caret);
    phone.dispatchEvent(new Event('input',{bubbles:true}));
  });
  apply();

  const state = form.elements.namedItem('state');
  const city = form.elements.namedItem('city');
  const list = form.querySelector('#quote-cities');
  const note = form.querySelector('#city-note');
  if (!list || !note) return; // Compatibilidade com paginas abertas antes desta versao.
  let previous = state.value, request = 0;
  const cache = new Map();
  async function loadCities(clear) {
    const current = state.value, version = ++request;
    list.replaceChildren();
    if (clear && current !== previous) { city.value = ''; city.setCustomValidity(''); }
    previous = current;
    if (!/^[A-Z]{2}$/.test(current)) {
      note.textContent = 'Escolha o estado para ver suas cidades.';
      return;
    }
    note.textContent = 'Carregando cidades de ' + current + '…';
    try {
      if (!cache.has(current)) cache.set(current, fetch('/assets/cities/' + current + '.json', {credentials:'omit'}).then(async response => {
        if (!response.ok) throw new Error('Cidades indisponiveis');
        const cities = await response.json();
        if (!Array.isArray(cities) || !cities.length || cities.some(name => typeof name !== 'string' || !name.trim())) throw new Error('Lista invalida');
        return cities;
      }).catch(error => {cache.delete(current);throw error;}));
      const cities = await cache.get(current);
      if (version !== request) return;
      const fragment = document.createDocumentFragment();
      for (const name of cities) { const option = document.createElement('option');option.value = name;fragment.append(option); }
      list.append(fragment);
      note.textContent = 'Cidades de ' + current + ' disponíveis. Digite para encontrar ou informe sua localidade.';
    } catch {
      if (version === request) note.textContent = 'Não foi possível carregar a lista. Você pode digitar a cidade normalmente.';
    }
  }
  state.addEventListener('change', () => loadCities(true));
  loadCities(false);
}
