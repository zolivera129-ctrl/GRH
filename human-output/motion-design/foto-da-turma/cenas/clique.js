/* clique — "O clique"
   Ideia: O flash congela a turma; a foto revela a cor e a moldura chega com as estrelas.
   A coreografia mora em _comum.js (Turma): a cena só aplica o tempo do filme, então o estado das
   pessoas, da câmera e da moldura atravessa as cenas sem costura. */
Motion.cena('clique', {
  render: (c) => Turma.render(c),
  montar(el, api) { Turma.montar(el, api); },
  quadro(t, el, api) { Turma.aplicar(api.cena.inicio + t, el, api); },
});
