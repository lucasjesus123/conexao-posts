# Catálogo de criativos do Grupo Conexão

Todos os modelos estão no `render.py` do kit. A arte é 1080x1350. O story sai automático.

## Regra do grid (o mais importante)

O perfil é visto em grade de 3 colunas. Antes de escolher o modelo, olhe os 5 posts mais recentes (status publicado ou agendado):

- **Tom:** alterne claro e escuro. Nunca 3 escuros seguidos. "Claro" = papel, numero claro, nota clara, popout, revista.
- **Modelo:** nunca o mesmo dos 3 últimos posts.
- **Foto do Lucas:** no máximo 1 a cada 3 posts.
- **Azul chapado (modelo palavra):** no máximo 1 a cada 9 posts.
- **Venda direta:** no máximo 1 a cada 3 posts. Os outros entregam algo: opinião, dado, guia ou demonstração.

## Modelos

### Editoriais (respiro)

| modelo | tom | quando usar | campos principais |
|---|---|---|---|
| papel | claro | opinião, frase forte, método | kicker, num, titulo ({itálico}, \| quebra), subtitulo, tam |
| numero | claro ou escuro (tema) | dado com fonte | numero, texto, fonte, kicker, tam |
| nota | claro ou escuro (tema) | pergunta ou opinião no estilo post de rede social | texto, rodape |
| carrossel | claro ou escuro | guia em slides (capa = slide 0) | numero, titulo, kicker; slides: slide, total, titulo, texto |
| palavra | azul chapado | quebrar o ritmo, 1 a cada 9 | titulo (1 palavra), subtitulo, kicker, fundo |
| foto | escuro | respiro, bastidor, robô | imagem, legenda, frase |

### Com a foto do Lucas (premium)

| modelo | tom | quando usar | campos principais |
|---|---|---|---|
| revista | claro em cima e escuro embaixo | venda da imersão, autoridade | recorte, palavra (atrás da cabeça), kicker, titulo, info, x, y, w |
| popout | claro | palestra, bastidor, convite | imagem, recorte, titulo, kicker, x, y, w |
| retrato | escuro, P&B | opinião forte do Lucas | imagem, frase, kicker |
| flutuante | escuro | venda com cards de vidro flutuando à frente e atrás dele | recorte, titulo ([gradiente]), subtitulo, cards_atras, cards_frente, x, y, w |

### Compostos (Photoshop: 3D, mockup, imagem sobre imagem)

Todos aceitam `"tema": "claro"` (fundo papel, vidro branco, celular prata) ou escuro (padrão). Use um composto por dia, alternando claro e escuro, conforme agentes/calendario.md.


| modelo | quando usar | campos principais |
|---|---|---|
| celular3d | demonstrar IA no WhatsApp, atendimento, automação | tag, titulo ([gradiente]), subtitulo, conversa [[quem, texto]...], pop_html (última mensagem com `<span class="mk">` de marca-texto), pop_rodape, cta, selo |
| painel3d | sistemas, painéis, gestão, a imersão | titulo, subtitulo, chips [[icone, texto]] x4, cards [[icone, valor, rótulo]] x3, objeto (imagem 3D), cta, nota, selo |

Ícones disponíveis: relogio, chat, grafico, escudo, raio, alvo, calendario, pin, lista, cerebro.

Modelos antigos (cinema, impacto, capa, dado, manchete, chat, frase, lista, evento) continuam existindo, mas só entram se a vaga do grid pedir algo que os novos não cobrem.

## Biblioteca de imagens (campanhas/assets/)

- `lucas_estudio.jpg` / `lucas_estudio_recorte.png`: retrato de estúdio, braços cruzados (revista, flutuante)
- `lucas_palestra.jpg` / `lucas_palestra_recorte.png`: palestrando com microfone (popout)
- `lucas_pb.jpg`: retrato P&B pensativo (retrato)
- `chip3d.png`: chip de IA 3D já recortado com brilho (objeto padrão do painel3d). Objetos novos: gere em fundo escuro liso e recorte com `python3 scripts/recorte_brilho.py entrada.jpg campanhas/assets/nome.png`
- `robo2.jpg`, `lucas_holo.jpg`: robôs e cena holográfica

Foto nova: o Diretor de Arte escreve o prompt completo e gera no Kairogen. Recorte com rembg (`pip install "rembg[cpu]" --break-system-packages`, sessão `isnet-general-use`). Salve no repositório em campanhas/assets/ para reusar depois.

## Dados ilustrativos

Conversas no celular e números de painel são **demonstração**: sempre com o selo "SIMULAÇÃO" ou "PAINEL ILUSTRATIVO". Nunca escreva depoimento, nome de cliente real, resultado ou porcentagem de ganho como se fosse fato.
