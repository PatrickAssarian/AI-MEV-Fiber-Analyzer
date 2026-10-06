# 🔬 Sistema de Análise de Fibras em MEV (Inteligência Artificial)

Bem-vindo(a) ao **Sistema Automático de Medição de Fibras**. Este projeto foi desenvolvido para analisar imagens de Microscopia Eletrônica de Varredura (MEV), encontrar as fibras automaticamente usando Inteligência Artificial (IA) e medir a espessura delas de forma extremamente rápida.

Este manual foi escrito de forma simples para que qualquer pessoa consiga usar, entender e até mesmo melhorar a Inteligência Artificial no futuro!

---

## 🚀 1. Como Iniciar o Programa

Para ligar o sistema, você **não precisa saber programar**. Siga apenas estes passos:

1. Abra a pasta do projeto (`PROJETO_MATERIAIS`) no seu computador.
2. Dê **dois cliques** no arquivo chamado **`INICIAR_PROGRAMA.bat`**.
3. Uma tela preta vai aparecer (não se assuste, é o motor do programa ligando). Em poucos segundos, uma página vai se abrir automaticamente no seu navegador de internet (geralmente no endereço `http://localhost:8501`).
4. **Pronto!** O sistema está rodando. *(Importante: Não feche a tela preta enquanto estiver usando o programa, pois ela é quem mantém o site no ar).*

---

## 📊 2. Como Usar o Sistema

Na tela do aplicativo, você verá opções muito simples no menu lateral esquerdo:

1. **Imagem Única:** Use esta opção se quiser enviar apenas uma foto para ver o resultado na tela imediatamente. Você pode enviar a foto e o programa vai:
   - Ler a barra de escala lá embaixo na foto.
   - Pintar as fibras de verde e azul.
   - Gerar gráficos e tabelas com as espessuras.
   - Liberar um botão para baixar um **Relatório em PDF** e a planilha em **Excel**.
2. **Lote (Macarrão):** Use esta opção se você tiver uma pasta inteira cheia de fotos e quiser analisar todas elas de uma vez só! Basta digitar o caminho da pasta e ele vai trabalhar sozinho e gerar um Excel gigante com o resumo de tudo.

---

## 🧠 3. Como o Sistema Funciona (Sem complicações)

Como o computador consegue olhar para uma imagem e medir as fibras? Ele faz isso em três grandes etapas:

1. **A IA lê a foto (YOLOv11):** Nós ensinamos uma IA a reconhecer dois objetos: **Fibras** e a **Barra de Escala**. Ela olha a foto e recorta onde estão esses itens.
2. **O leitor de texto (OCR):** A máquina pega o recorte da barra de escala, lê o número que está escrito ali (ex: `1 µm`) e calcula exatamente qual é o tamanho real de cada pixel da imagem.
3. **A régua matemática (Esqueletização):** Com as fibras pintadas pela IA, um algoritmo matemático entra em ação. Ele desenha uma "espinha dorsal" no meio de cada fibra e mede a distância do meio até as bordas. É assim que ele calcula a espessura sem errar.

---

## 🎓 4. Como "Ensinar" a IA e Atualizar o Banco de Dados

Se você notar que a IA está errando (esquecendo de marcar algumas fibras, ou errando a leitura da barra de escala), significa que ela **precisa estudar mais**. Para deixá-la mais inteligente, siga estes passos:

### Passo A: Enviar novas fotos para o Roboflow
O **Roboflow** é o site onde criamos o "gabarito" para a IA estudar.
1. Acesse seu projeto no Roboflow.
2. Suba novas fotos (faça o upload de imagens de MEV inéditas).

### Passo B: Fazer o Contorno (Anotação)
Você precisa desenhar nas fotos para ensinar a máquina.
* **Barra de Escala:** Crie a classe exatamente com o nome **ScaleBar** e desenhe um Retângulo englobando a barra preta e o número.
* **Fibras:** Crie a classe exatamente com o nome **Fiber** e desenhe Polígonos ao redor das fibras.
* **⚠️ Nomes Obrigatórios:** O computador procura por esses nomes exatos em inglês (`ScaleBar` e `Fiber`). Se você digitar "Fibra" ou "Escala", o sistema pode falhar!
* **Dica de Ouro:** Não contorne calombos pequenos ou sujeiras. Desenhe o contorno acompanhando o tubo da fibra da forma mais lisa possível.
* **Outra Dica:** Se a foto for um emaranhado muito confuso, anote a barra de escala e contorne pelo menos umas 5 fibras claras na foto, ignorando as muito borradas.

### Passo C: Baixar o "Gabarito" Atualizado
1. No Roboflow, clique em **Add to Dataset**.
2. Vá no menu esquerdo e clique em **Versions** (ou Generate).
3. Clique em **Generate New Version** para criar o pacote atualizado.
4. Clique em **Export Dataset**, escolha o formato **YOLOv8** (ou YOLOv11) e escolha **Download zip to computer**.
5. Extraia o arquivo `.zip` baixado dentro da pasta `dataset/` aqui no projeto. Apague a versão velha e deixe só a nova. (Vai ficar uma pasta chamada, por exemplo, `MEV-Fibers.v7i.yolov8`).

### Passo D: Treinar a nova versão da IA
1. Na pasta do projeto, dê **dois cliques** no arquivo chamado **`TREINAR_NOVA_IA.bat`**.
2. Uma tela preta vai aparecer informando que o computador está "estudando". Quando ele terminar, ele vai salvar automaticamente um modelo novo e mais inteligente na pasta `models/` e fechar sozinho!

### 🖥️ 5. Como Instalar em Outro Computador (Compartilhar o Projeto)
Se você compactar (zipar) essa pasta e enviar para um colega ou professor, o computador dele precisará reconfigurar as ferramentas. O arquivo `INICIAR_PROGRAMA.bat` vai dar erro no computador de outra pessoa.

Para resolver isso, quando colocar o projeto em um computador novo pela **primeira vez**, siga estes passos:
1. Certifique-se de que o computador novo tem o **Python** instalado (na hora de instalar o Python, marque a caixa *"Add Python to PATH"*).
2. Dê dois cliques no arquivo **`PRIMEIRO_USO_NO_PC_NOVO.bat`**.
3. Aguarde alguns minutos. Ele vai baixar todos os "motores" necessários, configurar tudo sozinho e abrir o programa no final!
4. A partir da segunda vez em diante, a pessoa pode voltar a usar o **`INICIAR_PROGRAMA.bat`** normalmente.

---
*Este software automatiza semanas de trabalho manual, permitindo foco na ciência e pesquisa ao invés da medição de rotina. Aproveite!*
