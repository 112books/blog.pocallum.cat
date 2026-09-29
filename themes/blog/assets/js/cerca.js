window.addEventListener('DOMContentLoaded', () => {
  document.getElementById('js-cerca-nojs').hidden = true;
  new PagefindUI({
    element: '#js-cerca',
    showSubResults: true,
    showImages: true,
    excerptLength: 25,
    translations: {
      placeholder: 'Cerca al blog…',
      zero_results: 'Cap resultat per a [SEARCH_TERM]'
    }
  });

  const params = new URLSearchParams(window.location.search);
  const q = params.get('q');
  if (q) {
    const input = document.querySelector('.pagefind-ui__search-input');
    if (input) { input.value = q; input.dispatchEvent(new Event('input')); }
  }
});
