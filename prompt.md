# Refatoração: estados em arquivo único e Info Popup

Refatore este repositório para eliminar os markdowns de `Pages/` e documentar cada estado dentro do próprio HTML, por meio de Info Popups.

Leia o `README.md` antes de começar. As regras dele continuam valendo, exceto pelas mudanças da seção 4.

## 1. Estrutura

Cada estado passa a ser um único arquivo HTML, e nenhum markdown existirá mais em `Pages/`.

```text
Antes                                      Depois
Pages/Tasks/description.md                 (removido)
Pages/Tasks/states/initial/description.md  (removido)
Pages/Tasks/states/initial/index.html      Pages/Tasks/initial.html
Pages/Tasks/states/done/description.md     (removido)
Pages/Tasks/states/done/index.html         Pages/Tasks/done.html
```

- Aplique a mudança aos 60 estados das 21 páginas, usando `git mv` para preservar o histórico.
- O endereço de um estado continua sendo `<Page>/<state>`.
- Atualize tudo que depende do caminho antigo: os links dos estados, `address()` em `Assets/js/app.js`, o redirect do `index.html` da raiz e os caminhos para `Assets/`.

## 2. Info Popup

É um botão ao lado de um componente que, ao ser clicado, abre um popup explicando aquele componente: o que a ação faz e para quais estados ela leva.

### Arquivos

Crie dois arquivos independentes de `app.js` e `app.css`, para que outro projeto possa reutilizá-los sozinhos:

- `Assets/js/info-popup.js`: script clássico e sem dependências, porque os estados precisam funcionar em `file://`.
- `Assets/css/info-popup.css`: toda a estilização do botão e do popup.

### Como adicionar

O padrão deve ser o mais fácil possível de implementar. Em cada estado, carregue os dois arquivos:

```html
<link rel="stylesheet" href="../../Assets/css/info-popup.css">
<script src="../../Assets/js/info-popup.js"></script>
```

Depois, coloque um `<template data-info-popup>` imediatamente após o componente, com o texto do popup dentro. Como `<template>` não renderiza nada, o estado funciona igual mesmo sem o script.

```html
<button class="btn btn-primary btn-block">Log in</button>
<template data-info-popup>
    <ul>
        <li>if email or password is empty → LoginScreen/required_fields</li>
        <li>if email is user@example.com and password is password123 → Home/initial</li>
        <li>else → LoginScreen/invalid_credentials</li>
    </ul>
</template>
```

### Botão

Uma interrogação pequena e branca, dentro de um círculo preenchido de verde.

### Comportamento

- O script cria um botão `?` para cada template e o exibe ao lado do componente, sem quebrar o layout. Isso inclui componentes de largura total, como `.btn-block` e `.task-row`.
- O botão nunca fica dentro de um link e é `type="button"`. Clicar nele não navega nem envia formulário.
- O popup fecha com um botão ×, com Esc e com clique fora dele.
- Abrir ou fechar o popup não redireciona e não altera o resto da tela. Valores digitados nos campos são mantidos.
- O botão e o popup funcionam por teclado, e o botão tem um `aria-label`.
- O script respeita a regra 2: não usa storage, parâmetros de URL nem requisições.

### Conteúdo

- Escreva em inglês, como o resto do app.
- Use apenas texto, sem links, botões ou formulários. Todo link continua no próprio estado.
- Use a notação dos atuais `description.md`, com uma linha por caminho: `if <condition> → <Page>/<state>`, terminando em `else → <Page>/<state>`. Um link simples tem só uma linha: `→ <Page>/<state>`.
- O texto deve corresponder ao comportamento real, ou seja, ao `href` do link ou às condições em `Assets/js/<Page>.js`.

## 3. Onde usar

Migre os `description.md` para Info Popups antes de removê-los, sem perder informação:

| Origem | Destino |
| --- | --- |
| Item com ação (link, botão ou submit) | Info Popup ao lado do componente, em todos os estados onde ele aparece |
| Frase da página e frase do estado | Info Popup ao lado do `<h1>` do estado, com uma frase em cada parágrafo |
| Item sem ação (campo, texto, mensagem de erro) | Nenhum, pois já está visível na tela |

Hoje os estados têm 439 links, 42 botões e 60 `<h1>`, totalizando 541 Info Popups. Você pode usar um script descartável para a migração, mas não o deixe no repositório, porque a arquitetura não tem etapa de build.

## 4. README

Atualize o `README.md`, em inglês. Estas são as únicas mudanças de regra autorizadas. Se outra parecer necessária, pergunte antes.

- **Structure:** mostre a nova árvore, com `Pages/<Page>/<state>.html` e os arquivos `info-popup`.
- **Nova regra:** toda ação da regra 3 tem um Info Popup ao lado, e todo estado tem um ao lado do `<h1>`.
- **Regra 3:** abrir ou fechar um Info Popup não é uma ação. Ele documenta o protótipo e não faz parte da tela. Um modal do produto continua sendo outro estado.
- **Regra 5:** troque `index.html` por `<state>.html`. `info-popup.js` passa a ser o único arquivo compartilhado que adiciona markup à tela, limitado ao botão `?` e ao popup, e sem links. Os arquivos do Info Popup podem ser carregados da URL pública abaixo.
- **Documents:** substitua a seção e seus templates por uma seção **Info Popup**, com o padrão de uso, as regras de conteúdo e o exemplo do login.

A seção Info Popup deve apontar para a implementação deste repositório, que é público, para quem quiser usá-la em vez de criar a sua. Ofereça duas formas: copiar os dois arquivos para o próprio `Assets/`, ou carregá-los por esta URL (só responde depois do push):

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/NEWMOLJUD/Arquiproto_provisorio@main/Assets/css/info-popup.css">
<script src="https://cdn.jsdelivr.net/gh/NEWMOLJUD/Arquiproto_provisorio@main/Assets/js/info-popup.js"></script>
```

Não use `raw.githubusercontent.com`, porque o navegador bloqueia o script servido como `text/plain`. O app de exemplo usa os arquivos locais, para continuar funcionando offline.

## 5. Fora do escopo

Não altere o visual dos estados, os fluxos, os textos da tela, os nomes de páginas e estados nem o login de demonstração. A única mudança visível na tela é a presença dos botões `?`.

## 6. Critérios de aceite

Verifique cada item antes de concluir, e relate o que falhar.

**Estrutura**

- `find Pages -name '*.md'` e `find Pages -type d -name states` não retornam nada.
- `find Pages -name '*.html' | wc -l` retorna 60.
- Todo `href` dos estados e todo endereço em `Assets/js/*.js` apontam para um arquivo existente.
- O `README.md` não menciona mais `description.md` nem `states/`.

**Info Popups** (verifique com um script)

- Todo link, todo botão e todo `<h1>` dos estados são seguidos por um `<template data-info-popup>`.
- O destino escrito em cada popup de link é igual ao `href` do link.
- Os caminhos escritos em cada popup de formulário são iguais aos de `Assets/js/<Page>.js`.

**Navegador** (abrindo os arquivos por `file://`)

- Os três caminhos do login continuam funcionando.
- O `?` do botão de login abre o popup sem enviar o formulário e mantém os valores digitados.
- O `?` de um `.task-row` abre o popup sem navegar.
- O popup fecha com ×, com Esc e com clique fora dele.
- `LoginScreen/initial` e `Tasks/done` não têm erros no console nem layout quebrado, em largura de desktop e de celular.
