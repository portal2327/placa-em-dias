# Placar em Dia v2

## O que faz
- Consulta feeds RSS sobre futebol e esportes.
- Guarda uma fila de novidades e publica no máximo uma manchete por execução.
- Limita publicações a cinco por dia no fuso de Brasília.
- Cria uma página HTML em `noticias/` para cada manchete.
- Mantém `state.json` para evitar duplicatas entre execuções.
- Não copia o texto completo das reportagens; cada página direciona à fonte original.

## Instalação
1. Baixe e extraia o ZIP.
2. Crie uma conta em https://github.com/ se precisar.
3. Crie um repositório **público** chamado `placar-em-dia`.
4. Envie os arquivos e pastas para a raiz do repositório, incluindo `.github/workflows/atualizar.yml`. Não envie apenas o ZIP compactado.
5. Vá a **Settings → Actions → General** e habilite **Read and write permissions** em Workflow permissions.
6. Vá a **Settings → Pages**, selecione **Deploy from a branch**, branch `main`, pasta `/ (root)`, e salve.
7. Abra **Actions → Atualizar portal esportivo → Run workflow** para testar.
8. Depois, em **Settings → Pages**, encontre o endereço público do site.

## Agenda e limites
O workflow executa às 10h, 13h, 16h, 19h e 22h UTC (aproximadamente 07h, 10h, 13h, 16h e 19h em Brasília). O GitHub pode atrasar os agendamentos. Se não houver novidades ou o feed falhar, o site pode publicar menos de cinco notícias naquele dia.

Não apague `state.json`: ele armazena a fila e o histórico para deduplicação. A deduplicação reduz repetição de títulos/links, mas não reconhece perfeitamente matérias reescritas sobre a mesma história.

## Testar localmente
Com Python 3.10+ e internet, execute `python atualizar.py`.

## Monetização e direitos
As páginas apresentam manchete, categoria, data e link para a fonte, não uma reportagem completa. Isso é uma base técnica e pode ser insuficiente para aprovação em programas de anúncios. Adicione análises próprias, contexto, estatísticas licenciadas e revisão editorial. Verifique os termos dos feeds antes de uso comercial; não copie reportagens, fotos, escudos ou logotipos sem autorização. Custo inicial previsto: R$ 0 dentro dos limites gratuitos; domínio próprio ou APIs podem custar. Receita não é garantida.
