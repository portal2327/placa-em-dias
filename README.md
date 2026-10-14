# Placar em Dia — portal esportivo automático

Projeto inicial gratuito que cria uma página estática com manchetes e links para fontes originais de futebol e outros esportes. O GitHub Actions executa o script cinco vezes ao dia e atualiza `index.html`.

## O que ele faz
- Consulta feeds RSS de pesquisa do Google News para cinco temas esportivos.
- Mostra manchete, categoria, data, fonte e link para a publicação original.
- Remove manchetes duplicadas dentro da atualização.
- Não copia o texto completo dos artigos nem precisa de chave de API.
- Pode ser hospedado gratuitamente no GitHub Pages.

## Instalação
1. Crie uma conta no GitHub, se ainda não tiver.
2. Crie um repositório **público** chamado `placar-em-dia` (público ajuda a usar Actions sem consumir minutos pagos).
3. Envie todos os arquivos desta pasta para a raiz do repositório, incluindo a pasta `.github/workflows`.
4. Abra **Settings → Pages** e escolha **Deploy from a branch**, branch `main`, pasta `/ (root)`. Salve.
5. Abra **Actions** e permita workflows se o GitHub pedir.
6. Abra o workflow **Atualizar portal esportivo** e clique em **Run workflow** para testar a primeira atualização.
7. Aguarde o Pages publicar e abra a URL exibida em **Settings → Pages**.

## Horários
O workflow roda às 10h, 13h, 16h, 19h e 22h UTC — aproximadamente 07h, 10h, 13h, 16h e 19h no horário de Brasília. Agendamentos do GitHub podem atrasar; não são garantidos no minuto exato.

## Rodar no computador
Requer Python 3.10 ou superior:
```bash
python atualizar.py
```
Isso gera `index.html`. Abra o arquivo no navegador.

## Limitações e responsabilidade editorial
- RSS e resultados podem mudar, falhar, atrasar ou apresentar manchetes repetidas.
- O site lista manchetes e links; não confirma por conta própria a veracidade de cada notícia. Confira as fontes antes de publicar alegações importantes.
- Para resultados e classificações oficiais, integre depois uma API esportiva confiável e respeite suas cotas/licenças.
- O projeto não usa IA generativa: evita inventar notícias e não reproduz matérias completas.
- Não há garantia de tráfego nem de receita. Para monetizar, o site precisa oferecer valor próprio e cumprir os requisitos do programa de anúncios.
- Antes de adicionar publicidade, analytics ou formulários, revise a política de privacidade.
- Não use logos, fotos, escudos ou marcas de clubes sem verificar os direitos de uso.
