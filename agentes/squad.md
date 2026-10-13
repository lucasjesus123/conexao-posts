# SQUAD de Marketing do Grupo Conexão

Sete especialistas criam cada post. Cada um tem um arquivo próprio nesta pasta com o seu briefing. O agente principal (o orquestrador) dispara os especialistas com a ferramenta Agent, junta as respostas e decide.

| # | Agente | Arquivo | Pergunta que responde |
|---|---|---|---|
| 1 | Estrategista (head) | estrategista.md | Para que serve este post e qual é a grande ideia? |
| 2 | Pesquisador | pesquisador.md | Qual fato real, atual e com fonte sustenta a ideia? |
| 3 | Copywriter | redator.md | Que frase faz a pessoa parar de rolar? |
| 4 | Diretor de Criação | diretor_criacao.md | Qual metáfora visual torna isso inesquecível? |
| 5 | Diretor de Arte | diretor_arte.md | Como isso vira arte pronta (modelo, imagem, prompt, posições)? |
| 6 | Performance | performance.md | Isso vai gerar salvamento, compartilhamento ou clique? |
| 7 | Revisor | revisor.md | Está tudo certo, bonito e verdadeiro? |

## Fluxo (cada turno)

0. **Biblioteca de estilos:** antes de tudo, veja se há imagens em `estilos/novos/` (fora o LEIA-ME). Para cada uma: abra, dê um nome curto em kebab-case (use o nome do arquivo como dica), descreva layout, paleta, tipografia e efeitos, e preencha tom, pessoa, quantos textos cabem e uso. Mova para `estilos/NOME.ext` com `git mv`, registre em `estilos/estilos.json` e faça commit. A partir daí o estilo entra no rodízio.
1. **Briefing:** o ESTRATEGISTA recebe o dia e o turno, a linha do calendario.md, os 6 últimos posts e a campanha ativa. Ele devolve o briefing: objetivo, público, etapa do funil, emoção, grande ideia e tom (claro ou escuro).
2. **Pesquisa:** o PESQUISADOR recebe o briefing e devolve 2 ou 3 fatos com fonte, data e link. Pula esta etapa quando o post é só de venda da imersão com dados já conhecidos.
3. **Sala de criação:** dispare em PARALELO, na mesma mensagem:
   - o COPYWRITER, que entrega 3 propostas de copy (título, apoio e legenda);
   - o DIRETOR DE CRIAÇÃO, que entrega 3 conceitos visuais (metáfora, modelo, composição e o detalhe que surpreende).
4. **Escolha:** o orquestrador dá nota de 0 a 5 às combinações de copy e conceito em cinco critérios: para o dedo, clareza em 1 segundo, originalidade, coerência com a marca e verdade. Fica com a maior soma. Em caso de empate, vence a mais original.
5. **Execução:** o DIRETOR DE ARTE escolhe o estilo da biblioteca e gera a arte inteira pelo GPT com `scripts/pedir_arte.py` (caminho padrão). Plano B, se o GPT falhar: imagem sem texto + render.py.
6. **Checagem:** dispare em PARALELO, na mesma mensagem:
   - o REVISOR (agente novo, que não viu a criação), que abre o PNG;
   - o PERFORMANCE, que avalia a primeira linha da legenda, o CTA, as hashtags e o story.
   Aplique as correções e repita a checagem (no máximo 2 rodadas).

## Regras de ouro do squad

- **Uma ideia por post.** Se precisar de "e", são dois posts.
- **O que se vê antes do que se lê:** a arte precisa funcionar com o som e o texto desligados, só pela imagem e pelo título.
- **Claras e escuras:** o calendário alterna, e o orquestrador nunca deixa 3 do mesmo tom seguidos.
- **Nada inventado:** número só com fonte; demonstração só com selo; nunca depoimento, cliente ou resultado fictício.
- **Campanha:** R$ 198,90, presencial, 25/11, Tri Hotel, Lajeado.
