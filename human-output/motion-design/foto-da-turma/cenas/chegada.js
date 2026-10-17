/* chegada — "A turma chega"
   Ideia: Espalhados, conversando em duplas e trios, eles se juntam para a foto.
   A coreografia mora em _comum.js (Turma): a cena só aplica o tempo do filme, então o estado das
   pessoas, da câmera e da moldura atravessa as cenas sem costura. */
Motion.cena('chegada', {
  render: (c) => Turma.render(c),
  montar(el, api) { Turma.montar(el, api); },
  quadro(t, el, api) { Turma.aplicar(api.cena.inicio + t, el, api); },
});
