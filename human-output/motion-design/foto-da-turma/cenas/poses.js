/* poses — "As poses"
   Ideia: Viram para a câmera, se apertam, tentam uma pose, outra, e assentam na pose final.
   A coreografia mora em _comum.js (Turma): a cena só aplica o tempo do filme, então o estado das
   pessoas, da câmera e da moldura atravessa as cenas sem costura. */
Motion.cena('poses', {
  render: (c) => Turma.render(c),
  montar(el, api) { Turma.montar(el, api); },
  quadro(t, el, api) { Turma.aplicar(api.cena.inicio + t, el, api); },
});
