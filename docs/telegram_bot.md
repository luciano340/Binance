# Tutorial: Criando um Bot no Telegram e Obtendo o ID de um Grupo

Neste tutorial, vamos aprender como criar um bot no Telegram e como obter o ID de um grupo no Telegram. Isso é útil para diversos propósitos, como desenvolver bots personalizados, integrar serviços externos ou automatizar tarefas.

## Passo 1: Criando um Bot no Telegram

1. Abra o Telegram e procure por "@BotFather" na barra de pesquisa.
2. Inicie uma conversa com o BotFather e clique em "Start" ou envie o comando `/start`.
3. Envie o comando `/newbot` para criar um novo bot. O BotFather irá solicitar um nome para o seu bot. Escolha um nome e envie.
4. Em seguida, o BotFather solicitará um username para o seu bot. Escolha um username único que termine com "bot" (por exemplo, "meubot_telegram_bot") e envie.
5. Após enviar o username, o BotFather fornecerá um token de acesso para o seu bot. Guarde este token com segurança, pois será usado para autenticar o seu bot nas interações com a API do Telegram.

## Passo 2: Obtendo o ID de um Grupo no Telegram

1. Abra o Telegram e vá para o grupo do qual você deseja obter o ID.
2. Adicione o seu bot ao grupo. Você pode fazer isso procurando pelo username do seu bot na barra de pesquisa e clicando em "Adicionar ao grupo".
3. Após adicionar o bot ao grupo, envie uma mensagem qualquer no grupo.
4. Abra o navegador e acesse o link `https://api.telegram.org/bot<YOUR_BOT_TOKEN_HERE>/getUpdates`, substituindo `<YOUR_BOT_TOKEN_HERE>` pelo token de acesso do seu bot.
5. Na página que se abre, você verá um JSON contendo informações sobre as mensagens recentes do grupo, incluindo o ID do chat. Procure pelo ID correspondente ao grupo desejado.

Pronto! Agora você criou com sucesso um bot no Telegram e obteve o ID de um grupo no Telegram.

Este tutorial é apenas um ponto de partida e existem muitas possibilidades para explorar a partir daqui, como desenvolver funcionalidades personalizadas para o seu bot ou integrá-lo com outros serviços. Divirta-se explorando e criando com o seu bot no Telegram!


## Comandos do bot

Este bot fornece funcionalidades de automação de negociação de criptomoedas. Abaixo estão os comandos disponíveis e como usá-los:

## /check_positions
Este comando é usado para recuperar todas as criptomoedas que foram compradas pelo bot e estão aguardando venda.

Você pode especificar a criptomoeda que deseja verificar imediatamente após o comando para que o bot forneça informações apenas para essa criptomoeda. Se o comando for passado sem nenhuma informação, o bot retornará todas as posições.

**Uso:** `/check_positions [criptomoeda]`

## /check_running_coins
Este comando informa o usuário sobre quais criptomoedas estão atualmente sendo monitoradas pelo bot para automação.

**Uso:** `/check_running_coins`

Sinta-se à vontade para entrar em contato com o bot com esses comandos para gerenciar sua negociação de criptomoedas de forma eficiente!




