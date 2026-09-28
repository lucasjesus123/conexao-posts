# conexao-posts

Posts do Instagram do **Grupo Conexão**. A rotina diária do Claude cria a arte e a legenda e salva aqui. O GitHub publica no Instagram pela API oficial da Meta no horário marcado, no feed e no story.

## Como funciona

```
posts/AAAA-MM-DD/
  feed.jpg     arte do feed (1080x1350)
  story.jpg    arte do story (1080x1920)
  post.json    horário, legenda e status
```

`post.json`:

```json
{
  "publicar_em": "2026-09-28T18:00:00-03:00",
  "legenda": "texto do post…",
  "story": true,
  "status": "agendado"
}
```

A cada 15 minutos o workflow **Publicar no Instagram** procura posts `agendado` cujo horário já chegou. Ele publica o feed e o story e muda o status para `publicado`. Se der erro, o status vira `erro` e a mensagem da Meta fica gravada no campo `erro`.

Para cancelar um post, troque o status para `cancelado`. Para mudar o horário, edite `publicar_em`.

## Configuração da Meta (uma vez)

Você precisa de: Instagram **profissional** (Empresa ou Criador) ligado a uma **página do Facebook**, e as duas dentro do seu **Gerenciador de Negócios** (business.facebook.com).

1. **Criar o app.** Em developers.facebook.com, vá em Meus apps, crie um app do tipo **Empresa** e vincule ao seu Gerenciador de Negócios.
2. **Criar o usuário do sistema.** Em business.facebook.com, abra Configurações do negócio > Usuários > **Usuários do sistema**. Clique em Adicionar, dê um nome (ex.: "publicador") e escolha a função **Administrador**.
3. **Dar acesso aos ativos.** No usuário do sistema, clique em **Atribuir ativos** e dê controle total a três coisas: o **app**, a **página do Facebook** e a **conta do Instagram** do Grupo Conexão.
4. **Gerar o token.** Ainda no usuário do sistema, clique em **Gerar novo token**. Escolha o app, marque a validade **Nunca** e selecione estas permissões:
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_show_list`
   - `pages_read_engagement`
   - `business_management`

   Copie o token.
5. **Colar no GitHub.** Neste repositório, abra Settings > Secrets and variables > **Actions** > New repository secret e crie `META_TOKEN` com o token copiado.
6. **Descobrir o ID do Instagram.** Abra a aba **Actions** > **Publicar no Instagram** > **Run workflow** e marque "Só testar a conexão". O log mostra cada página com o `IG_USER_ID` do Instagram ligado a ela. Crie um segundo segredo `IG_USER_ID` com esse número.
7. **Testar de novo.** Rode o mesmo teste. Deve aparecer `Conectado: @seu_instagram`.

Pronto: daí em diante os posts saem sozinhos.

> O token de usuário do sistema não expira. Se um dia a Meta pedir revisão do app, as permissões acima são as únicas usadas.

## Novo cliente

Cada cliente tem o próprio repositório, cópia deste, com o próprio `META_TOKEN` e o próprio `IG_USER_ID`. Nada se mistura entre clientes.
