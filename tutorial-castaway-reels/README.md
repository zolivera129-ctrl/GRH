# Reels: como se candidatar no site da Cast-A-Way (mobile)

Vídeo: `castaway-como-aplicar-reels.mp4` (1080×1920, 9:16, 30 fps, H.264 + AAC, cerca de 48 s)

## Por que este vídeo existe

No post do @castawayhiring, a maioria dos comentários pergunta a mesma coisa: *"How to apply?"*. O vídeo responde a isso com uma simulação de navegação no celular, do endereço do site até o envio do currículo. Ele mostra o preenchimento da nacionalidade e do prefixo do país (para a equipe saber de onde a pessoa está falando) e tem um trecho só para o **código de campanha**, que identifica a vaga e dá mais visibilidade à candidatura com os recrutadores.

Os textos de tela estão em inglês, como o site e os comentários do público.

## Roteiro

| Tempo (s) | Cena |
|---|---|
| 0,0 – 3,5 | **Gancho.** "You asked:" e os balões de comentário ("How to apply?", "I am interested!"…) entram um a um. Eles se dissolvem e aparecem o logo e o título **HOW TO APPLY at Cast-A-Way · 6 easy steps · on your phone**. |
| 3,3 – 7,0 | **Passo 1: abrir cast-a-way.com.** O celular entra em perspectiva. Zoom na barra de endereço, onde o endereço é digitado (a tecla `.com` é tocada) e o site carrega. Zoom out. |
| 7,0 – 10,5 | **Passo 2: abrir o menu.** Zoom no ☰, que vira ✕, e o menu desce. A câmera desce até **Apply Now!** e o toque abre a página do formulário. |
| 10,5 – 25,2 | **Passo 3: contatos.** Nome e sobrenome digitados no teclado do iPhone. **Nacionalidade**: o seletor rola até *Philippines*. E-mail. **Prefixo do país**: o seletor rola até *Philippines (+63)*, seguido de um zoom forte com destaque amarelo ("so we know where you're calling from"). Telefone (WhatsApp/Telegram) no teclado numérico. |
| 25,2 – 29,2 | **Passo 4: demais seções.** Zoom out com o celular inclinado. A página rola rápido e um checklist entra ao lado: 02 Consents, 03 Resume (PDF com foto), 04 Survey, 05 até 3 cargos, 06 Languages. |
| 29,2 – 38,6 | **Passo 5: código de campanha ("DON'T SKIP IT").** Impacto sonoro e luz amarela no fundo. Zoom forte no campo *Campaign code*, com o resto da tela escurecido. Um anúncio de vaga ("NOW HIRING · BARTENDER") entra, o código sai do anúncio e voa até o campo. Depois entram os três motivos: mostra para qual vaga a pessoa está se candidatando, a candidatura pode ter prioridade e ganha mais visibilidade com os recrutadores. |
| 38,6 – 44,8 | **Passo 6: enviar.** "How did you hear about us?" → Instagram. "I'm not a robot" (carregando → ✓). Toque em **SEND YOUR RESUME**, confirmação "Application sent!" e confete. |
| 44,3 – 48,3 | **Encerramento.** Logo, "Apply now at **cast-a-way.com**", o lembrete amarelo "Don't forget the campaign code!" e "Save this video / Send it to a friend". |

As áreas do Reels que ficam sob a interface do Instagram (topo, rodapé e coluna de botões à direita) não têm informação essencial.

## O que conferir antes de postar

- **Código de campanha de exemplo**: o vídeo usa `CW-2026`. Troque pelo formato real dos anúncios em `src/theme.ts` (`COPY.campaignCode`) e renderize de novo. O cargo do anúncio (`COPY.jobTitle`) fica no mesmo arquivo.
- **Logo**: é uma releitura em vetor feita a partir do print do site (`src/components/Logo.tsx`). Se tiver o arquivo oficial, vale substituir.
- **Dados fictícios**: Maria Santos, Filipinas, `maria@email.com`. A tela "Application sent!" é uma simulação, e a mensagem real do site pode ser outra.
- **Áudio**: o vídeo tem só efeitos sonoros (toques, teclas, whoosh, sino), sintetizados por `scripts/make_sfx.py`, sem licença de terceiros. Não há música: adicione uma trilha pelo próprio Instagram e baixe o volume do áudio original se precisar.

## Legenda sugerida para o post

> You asked "How to apply?" 👇 Here's the step-by-step on your phone:
> 1️⃣ Go to cast-a-way.com
> 2️⃣ Menu → Apply Now!
> 3️⃣ Fill in your contacts (nationality + country prefix)
> 4️⃣ Upload your resume (PDF with photo) and answer every section
> 5️⃣ ⚠️ Add the CAMPAIGN CODE from the job post: it shows which job you're applying for and may give your application priority
> 6️⃣ Tick "I'm not a robot" and tap SEND YOUR RESUME
> Save this video and share it with a friend who dreams of working at sea 🌊🚢

## Como editar e renderizar

Projeto em [Remotion](https://www.remotion.dev) (React → vídeo).

```bash
npm i
npm run dev        # Remotion Studio, para pré-visualizar e ajustar
npm run render     # gera castaway-como-aplicar-reels.mp4
```

Num ambiente sem acesso ao download do Chrome do Remotion, aponte para um Chromium local, por exemplo:
`npm run render -- --browser-executable=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell`

Quadros avulsos para conferência: `node scripts/stills.mjs Walkthrough 300 880` (saída em `out/stills/`; use a variável `REMOTION_BROWSER` para indicar o Chromium).

### Estrutura

- `src/Tutorial.tsx`: sequência completa (gancho → navegação → encerramento, com fades).
- `src/scenes/Walkthrough.tsx`: a navegação. A tabela `T` define o frame de cada toque, digitação e seleção; `CAM_KEYS` guarda os keyframes da câmera (zoom e foco); `SFX` lista os sons.
- `src/scenes/Hook.tsx` e `src/scenes/Outro.tsx`: abertura e encerramento.
- `src/site/`: as telas simuladas do site (cabeçalho, home, menu e formulário "Apply Now" com as seções 01–07), no navegador escuro do vídeo de referência.
- `src/components/`: celular, teclado do iPhone (texto, e-mail, URL e numérico), seletor de país, indicador de toque, legendas dos passos, fundo animado e logo.
- `src/theme.ts`: cores medidas no site e todos os textos/dados do formulário.
- `public/`: fontes (Raleway, Open Sans, Oswald, Inter; licença OFL), foto do navio recortada do vídeo de referência e efeitos sonoros.
