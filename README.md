# 🔬 AI MEV Fiber Analyzer (Análise Automatizada de Fibras)

Um sistema open-source impulsionado por Inteligência Artificial (YOLOv11) desenvolvido para automatizar a extração e medição de diâmetros de fibras em imagens de Microscopia Eletrônica de Varredura (MEV).

## 📖 O que é este projeto e qual o seu intuito?

Na pesquisa de Ciência dos Materiais e Engenharia, medir o diâmetro de dezenas ou centenas de fibras em imagens de MEV é um processo extremamente tedioso, repetitivo e manual. Pesquisadores perdem horas utilizando softwares genéricos de imagem para traçar retas e fazer médias.

O **AI MEV Fiber Analyzer** foi criado para resolver esse problema. O intuito é **automatizar 100% da medição**. Você insere uma imagem (ou uma pasta com centenas delas) e o sistema faz tudo sozinho: ele lê a escala geométrica da foto, encontra cada fibra, calcula as medidas matemáticas reais (em micrômetros) e gera um relatório estatístico completo em segundos.

### ✨ O que ele faz exatamente?
1. **Detecção e Segmentação (YOLOv11-Seg):** A IA localiza as fibras e recorta o contorno exato de cada uma delas na imagem.
2. **Leitura Inteligente da Escala (OCR):** A IA localiza a barra de escala no rodapé da imagem (ex: `1 µm`) e um sistema de Reconhecimento Óptico de Caracteres lê o valor. Assim, o programa calcula matematicamente quantos pixels equivalem a 1 micrômetro naquela foto específica.
3. **Cálculo de Espessura (Esqueletização):** Usando processamento de imagens (OpenCV), o sistema traça uma "espinha dorsal" matemática no centro da fibra recortada e calcula a distância até as bordas, garantindo uma medida de diâmetro precisa.
4. **Exportação de Dados:** Gera gráficos de distribuição e relatórios consolidados em `.pdf`, `.csv` e `.xlsx`.

---

## 🚀 Como usar o sistema (Para Usuários)

Para pessoas que desejam apenas utilizar o software pronto no Windows:

1. **Primeiro Uso em Computador Novo:**
   - Dê dois cliques no arquivo **`PRIMEIRO_USO_NO_PC_NOVO.bat`**.
   - Ele vai criar o ambiente virtual e instalar todas as dependências automaticamente (Requer Python instalado).
2. **Iniciando o Programa Diariamente:**
   - Dê dois cliques em **`INICIAR_PROGRAMA.bat`**. 
   - O aplicativo será aberto no seu navegador automaticamente.

---

## 💻 Instalação (Para Desenvolvedores / Linux / Mac)

Se você quiser rodar via terminal padrão:

```bash
# Clone o repositório
git clone https://github.com/PatrickAssarian/AI-MEV-Fiber-Analyzer.git
cd AI-MEV-Fiber-Analyzer

# Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate

# Instale os requisitos
pip install -r requirements.txt

# Inicie o aplicativo Streamlit
streamlit run interface/app.py
```

---

## 🧠 Como "Ensinar" a IA (Atualizar Banco de Dados)

Se o modelo não estiver identificando bem um tipo específico de fibra, você pode treiná-lo com novas imagens:

### 1. Anotação de Dados no Roboflow
* Faça o upload de novas fotos.
* **Barra de Escala:** Crie a classe exatamente com o nome **ScaleBar** e desenhe um Retângulo englobando a barra preta e o número.
* **Fibras:** Crie a classe exatamente com o nome **Fiber** e desenhe Polígonos ao redor das fibras (acompanhando o tubo de forma lisa).
* **⚠️ Nomes Obrigatórios:** O computador procura por esses nomes exatos em inglês (`ScaleBar` e `Fiber`). Não traduza para o português.

### 2. Treinamento
1. No Roboflow, gere uma nova versão do dataset e exporte como `.zip` (Formato YOLO).
2. Extraia o conteúdo dentro da pasta `dataset/` no projeto (substituindo a antiga).
3. Dê **dois cliques** em **`TREINAR_NOVA_IA.bat`** (ou rode `python train.py`).
4. A máquina vai treinar o novo modelo, salvar e atualizar o aplicativo automaticamente!

---
*Este software automatiza semanas de trabalho manual, permitindo foco na ciência e pesquisa ao invés da medição de rotina. Aproveite!*
