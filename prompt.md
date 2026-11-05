refatore a arquitetura do projeto para:


## Estrtura
- pages/Tasks/done.html
- pages/Tasks/initial.html 

- nenhum markdown existirá mais em pages 
- as descriçoes devem ser embutidas na própria página através de Infos PopPup


## Mecanica Infos PopPup
### Descrição básica
é um botão que fica  ao  lado do  componente alvo e quando clicado abre um popup de informações, sobre aquela ação, quais estados altera, etc .. 

### botão InfoPopup 
uma interrogação pequena branca circulada por um prenchimento circular verde.

### Exemplo de Info PopPup 
ao lado do botão do login, ha um infopopup, quando clicado , ele abre um popup dizendo:

```text
- se o usuario for user_autenticated@user.com  e a senha for 12345, sera logado e redirecionado para /home/ 
```

### Fontes de Info popup
deve ser criado nesse repo (que é público) um script js que faz o info popup, assim como um css com sua estilizização, a ideia é ser o mais facil o possivel para alguem implementar ele.

Ele deve estar nas regras da arquitetura, que um sistema de info popup deve estar presente nas ações que mudam o estado da aplicação.  Apontando para se quiser usar o do proprio projeto.

Deve se haver uma padronização para criaão de infopopup, tipo onde no html coloca os textos, como adiciona ele, etc.. 

