// Tudo o que costuma mudar no vídeo fica aqui: textos, cores, tempos e arquivos.
// Os tempos estão em segundos e são convertidos para frames dentro dos componentes.

export const VIDEO = {
  width: 1920,
  height: 1080,
  fps: 30,
  // a duração total é calculada a partir do ritmo de leitura (DURATION_IN_SECONDS, abaixo)
};

// Ritmo de leitura. Os tempos de cada teste são calculados a partir do número de palavras
// de cada texto. Para deixar tudo mais lento, diminua as palavras por segundo.
export const READING = {
  userWordsPerSecond: 3.6, // mensagens do usuário (as mais longas)
  patiWordsPerSecond: 3, // cada bloco da resposta da PATI
  minBlockSeconds: 1.6, // tempo mínimo de um bloco curto na tela
  pauseSeconds: 0.35, // pausa entre um bloco e o próximo
  userSettleSeconds: 0.8, // folga depois de ler a mensagem do usuário
  finalHoldSeconds: 2.2, // tempo extra na recomendação final de cada teste
  closingSeconds: 3, // encerramento (o último 1,5 s fica estático)
};

// Arquivos em public/. Para trocar uma imagem, substitua o arquivo mantendo o nome
// ou altere o caminho aqui.
export const ASSETS = {
  storyImage: "luis-justo-story.png",
  storyAspect: 1368 / 771, // largura / altura da miniatura
  artImage: "mockup-evento.png",
  artAspect: 1,
  music: "audio/trilha.m4a", // base contínua (cortada no encerramento)
  musicEnd: "audio/trilha-final.m4a", // acorde final
  sfxClick: "audio/clique.wav",
  sfxSend: "audio/envio.wav",
  sfxReveal: "audio/revela.wav",
};

// Áreas da imagem do teste 1 que ficam desfocadas e cobertas (em % da imagem).
// A imagem atual é só o slide, sem nome, foto ou @ de quem postou, então nada é coberto.
// Se usar um print do story com a interface do Instagram, cubra o topo e a base, por exemplo:
//   { left: 0, top: 0, width: 100, height: 10 }, // barra de progresso, foto e nome de usuário
//   { left: 0, top: 91, width: 100, height: 9 },  // campo de resposta
export const STORY_PRIVACY_MASKS: {
  left: number;
  top: number;
  width: number;
  height: number;
}[] = [];

export const VOLUME = {
  music: 0.65,
  click: 0.5,
  send: 0.45,
  reveal: 0.35,
};

export const COLORS = {
  desk: "#E9E7E2",
  window: "#FFFFFF",
  chrome: "#F1F0ED",
  chromeLine: "#E2E0DC",
  sidebar: "#F7F7F5",
  line: "#E6E5E1",
  text: "#161616",
  textSoft: "#4A4A48",
  textMuted: "#8A8984",
  userBubble: "#EFEFEC",
  accent: "#1F4D3A", // verde escuro da PATI
  accentSoft: "#E3EEE7", // fundo de recomendações
  mark: "#CFE3D6", // marcação editorial nos trechos destacados
  veil: "rgba(240, 239, 235, 0.62)",
};

export const FONT_FAMILY = "Inter";

export const TEXTS = {
  appName: "PATI - Persona para Análise, Teste e Insights",
  tabTitle: "PATI",
  address: "pati / nova conversa",
  composerPlaceholder: "Pergunte à PATI",
  disclaimer:
    "A PATI é uma persona de teste. Use as análises para decidir com o time.",
  sidebarNew: "Nova conversa",
  sidebarSection: "Análises",
  sidebarFooter: "Grupo Gestão RH",

  intro: {
    title: "Conheça a PATI",
    subtitle: "Persona para Análise, Teste e Insights",
  },

  whatSheDoes: {
    line1: "Ela pensa como uma liderança sênior de RH.",
    line2: "E tensiona ideias antes que elas cheguem ao público.",
    criteria: ["Relevância.", "Credibilidade.", "Aplicação."],
  },

  test1: {
    chapter: "Teste 1 de 3",
    chapterTitle: "Gancho de palestra",
    sidebar: "Gancho da palestra",
    user: "Pati, no evento de ontem o Luis Justo, CEO do Rock In Rio tinha esse slide e uma das convidadas postou justo esse story, imaginei por dados que poderia ser um gancho pra uma aspas ou um post da palestra, o que acha?",
    userMarks: ["poderia ser um gancho", "uma aspas ou um post"],
    reply1: "Eu pararia nesse gancho.",
    reply2:
      "Mas a frase sozinha pode virar apenas mais uma inspiração de evento.",
    reco: "Mostre o que sustenta a provocação e qual decisão ela movimenta no RH.",
    recoEmphasis: ["sustenta", "decisão"],
  },

  test2: {
    chapter: "Teste 2 de 3",
    chapterTitle: "Assunto de e-mail",
    sidebar: "Assunto do e-mail",
    userIntro:
      "Estamos com dúvida entre esses dois assuntos pro e-mail da semana:",
    optionA: { label: "Assunto A", text: "IA & RH" },
    optionB: {
      label: "Assunto B",
      text: "O RH pode não estar pronto pra aplicar IA e pouco se fala disso",
    },
    reply1: "‘IA & RH’ é amplo e previsível.",
    reply2: "O assunto B tem tensão, mas antecipa uma conclusão.",
    solutionLabel: "Assunto sugerido",
    solution: "O que precisa estar pronto antes de aplicar IA no RH",
    solutionNote: "Promete utilidade concreta sem subestimar quem lê.",
  },

  test3: {
    chapter: "Teste 3 de 3",
    chapterTitle: "Arte do evento",
    sidebar: "Post do evento",
    user: "e essa arte, o que você acha? ignore o fato de ser IA. é só um mockup",
    reply1: "A arte chama atenção, mas ‘incrível’ é subjetivo.",
    reply2: "A GRH deve mostrar a relevância do encontro, não se autoelogiar.",
    reco: "Menos adjetivos, mais evidências.",
    recoEmphasis: ["evidências."],
  },

  closing: {
    line1: "Agentes que conhecem o público ajudam a decidir melhor.",
    line2: ["Antes de publicar.", "Antes de convidar.", "Antes de investir."],
    signature: "PATI | Grupo Gestão RH",
  },
};

// Linha do tempo, em segundos (absolutos no vídeo).
// A apresentação (0–9 s) tem tempos fixos. Os testes são montados em sequência a partir do
// ritmo de leitura em READING: cada bloco só entra depois que o anterior pode ser lido.
const words = (text: string) => text.split(/\s+/).filter(Boolean).length;
const read = (text: string, wordsPerSecond = READING.patiWordsPerSecond) =>
  Math.max(READING.minBlockSeconds, words(text) / wordsPerSecond);
const userRead = (text: string) =>
  words(text) / READING.userWordsPerSecond + READING.userSettleSeconds;
// momento em que o leitor chega a um trecho da mensagem do usuário (para a marcação acompanhar)
const reachAt = (text: string, phrase: string) =>
  words(text.slice(0, Math.max(0, text.indexOf(phrase)))) /
  READING.userWordsPerSecond;
const round = (n: number) => Math.round(n * 100) / 100;
const roundAll = <T extends Record<string, number>>(o: T) =>
  Object.fromEntries(Object.entries(o).map(([k, v]) => [k, round(v)])) as T;

const buildTest1 = (start: number) => {
  const x = TEXTS.test1;
  const send = start + 1.35;
  const thinking = send + userRead(x.user);
  const reply1 = thinking + 0.4;
  const reply2 = reply1 + read(x.reply1) + READING.pauseSeconds;
  const reco = reply2 + read(x.reply2) + READING.pauseSeconds;
  const end = reco + read(x.reco) + READING.finalHoldSeconds;
  return {
    timing: roundAll({
      start,
      cursorIn: start,
      attachClick: start + 0.5,
      composerText: start + 0.75,
      sendClick: start + 1.25,
      send,
      mark1: send + reachAt(x.user, x.userMarks[0]),
      mark2: send + reachAt(x.user, x.userMarks[1]),
      thinking,
      reply1,
      reply2,
      reco,
    }),
    end,
  };
};

const buildTest2 = (start: number) => {
  const x = TEXTS.test2;
  const user = [
    x.userIntro,
    x.optionA.label,
    x.optionA.text,
    x.optionB.label,
    x.optionB.text,
  ].join(" ");
  const send = start + 0.85;
  const thinking = send + userRead(user);
  const reply1 = thinking + 0.4;
  const reply2 = reply1 + read(x.reply1) + READING.pauseSeconds;
  const solution = reply2 + read(x.reply2) + READING.pauseSeconds;
  const solutionNote = solution + read(x.solution) + READING.pauseSeconds;
  const end = solutionNote + read(x.solutionNote) + READING.finalHoldSeconds;
  return {
    timing: roundAll({
      start,
      cursorIn: start + 0.25,
      composerText: start + 0.2,
      sendClick: start + 0.75,
      send,
      thinking,
      reply1,
      reply2,
      solution,
      solutionNote,
    }),
    end,
  };
};

const buildTest3 = (start: number) => {
  const x = TEXTS.test3;
  const send = start + 1.35;
  const thinking = send + userRead(x.user);
  const reply1 = thinking + 0.4;
  const reply2 = reply1 + read(x.reply1) + READING.pauseSeconds;
  const reco = reply2 + read(x.reply2) + READING.pauseSeconds;
  const end = reco + read(x.reco) + READING.finalHoldSeconds;
  return {
    timing: roundAll({
      start,
      cursorIn: start,
      attachClick: start + 0.5,
      composerText: start + 0.75,
      sendClick: start + 1.25,
      send,
      thinking,
      reply1,
      reply2,
      reco,
    }),
    end,
  };
};

const test1 = buildTest1(9);
const test2 = buildTest2(round(test1.end));
const test3 = buildTest3(round(test2.end));
const closingStart = round(test3.end);

export const TIMING = {
  browserIn: 0,
  introTitle: 0.4,
  introSubtitle: 0.75,
  introToHeader: 2.2, // texto central sobe e se integra ao cabeçalho

  whatLine1: 3.2,
  whatLine2: 4.4,
  criteria: 5.8, // as três palavras entram com 0,4 s entre elas
  scrollToTest1: 7.9,

  test1: test1.timing,
  test2: test2.timing,
  test3: test3.timing,
  closing: {
    start: closingStart,
    line1: closingStart + 0.3,
    line2: closingStart + 0.7, // três partes com 0,2 s entre elas
    signature: closingStart + 0.9,
    // tudo termina até 1,5 s depois do início: o restante fica estático
  },
};

export const DURATION_IN_SECONDS =
  Math.ceil((closingStart + READING.closingSeconds) * VIDEO.fps) / VIDEO.fps;

// Medidas da interface (em pixels do quadro, antes do zoom da câmera).
export const LAYOUT = {
  window: { x: 60, y: 48, width: 1800, height: 984, radius: 16 },
  chromeHeight: 52,
  sidebarWidth: 272,
  headerHeight: 64,
  columnWidth: 960,
  composerBottom: 20, // distância do composer até a linha de aviso
  disclaimerHeight: 30,
  composerIdleHeight: 112,
  // fonte base dos balões; o ajuste automático reduz até o mínimo se o texto não couber
  userFont: 25,
  userFontMin: 19,
  userBubbleMaxWidth: 720,
  userBubbleMaxHeightRatio: 0.55, // fração da área visível da conversa
  patiFont: 26,
  storyThumbHeight: 250,
  artThumbHeight: 300,
};

// Enquadramento: [segundo, zoom, foco x, foco y]. O foco é o ponto do quadro (antes do zoom)
// que fica no centro da tela; ele é limitado para nunca mostrar além da janela do navegador.
// Os keyframes acompanham TIMING, então mudar um tempo lá move a câmera junto.
const testCamera = (
  t: { send: number; reply1: number; reco?: number; solution?: number },
  next: number,
): [number, number, number, number][] => {
  const highlight = t.reco ?? t.solution ?? t.reply1;
  return [
    [t.send + 0.15, 1.08, 1096, 540],
    [t.send + 0.75, 1.12, 1250, 470], // leitura do prompt, com aproximação lenta
    [t.reply1 - 0.3, 1.16, 1250, 470],
    [t.reply1 + 0.4, 1.1, 1000, 600], // resposta da PATI
    [highlight - 0.7, 1.1, 1000, 600],
    [highlight, 1.15, 1000, 650], // recomendação
    [next - 0.4, 1.17, 1000, 650],
  ];
};

export const CAMERA: [number, number, number, number][] = [
  [0, 1, 960, 540],
  [TIMING.scrollToTest1, 1, 960, 540],
  [TIMING.scrollToTest1 + 1, 1.08, 1096, 540],
  ...testCamera(TIMING.test1, TIMING.test2.start),
  [TIMING.test2.start + 0.2, 1.08, 1096, 540],
  ...testCamera(TIMING.test2, TIMING.test3.start),
  [TIMING.test3.start + 0.2, 1.08, 1096, 540],
  ...testCamera(TIMING.test3, TIMING.closing.start + 0.4),
  [TIMING.closing.start + 1, 0.9, 960, 540], // o chat se afasta no encerramento
];
