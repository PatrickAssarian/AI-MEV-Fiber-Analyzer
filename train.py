import os
import glob
from ultralytics import YOLO

def encontrar_dataset_mais_recente():
    # Procura na pasta dataset por qualquer data.yaml
    caminhos_yaml = glob.glob(os.path.join("dataset", "**", "data.yaml"), recursive=True)
    if not caminhos_yaml:
        return None
    
    # Se tiver mais de um (ex: v6 e v7), pega o modificado mais recentemente
    caminho_mais_recente = max(caminhos_yaml, key=os.path.getmtime)
    
    # Retorna o caminho absoluto
    return os.path.abspath(caminho_mais_recente)

def iniciar_treinamento():
    print("========================================")
    print("PROCURANDO BANCO DE DADOS ATUALIZADO...")
    print("========================================")
    
    data_yaml = encontrar_dataset_mais_recente()
    
    if data_yaml is None:
        print("ERRO: Nenhuma pasta com arquivo data.yaml foi encontrada dentro de 'dataset'.")
        print("Siga o manual para baixar o zip do Roboflow e extrair na pasta 'dataset'.")
        return
        
    print(f"Gabarito encontrado: {data_yaml}")
    
    # Corrige o data.yaml automaticamente para inserir o caminho absoluto (evita erro do YOLO)
    dataset_dir = os.path.dirname(data_yaml)
    with open(data_yaml, 'r', encoding='utf-8') as f:
        linhas = f.readlines()
    
    ja_tem_path = any(linha.startswith('path:') for linha in linhas)
    if not ja_tem_path:
        with open(data_yaml, 'w', encoding='utf-8') as f:
            # Substitui as contra-barras por barras normais
            caminho_correto = dataset_dir.replace('\\', '/')
            f.write(f"path: {caminho_correto}\n")
            f.writelines(linhas)
            
    print("Iniciando o estudo da Inteligencia Artificial. Isso pode demorar...")
    
    # Inicia o modelo pre-treinado
    model = YOLO("yolo11n-seg.pt")
    
    # Roda o treinamento. 
    # Salvamos sempre com o mesmo nome (segmenter_atual) com exist_ok=True 
    # para ele substituir o antigo automaticamente.
    model.train(
        data=data_yaml,
        epochs=50,
        batch=4,
        project="models",
        name="segmenter_atual",
        exist_ok=True,
        save=True,
        plots=True,
        task='segment',
        patience=15
    )
    
    print("\nO treinamento foi um sucesso! O modelo 'segmenter_atual' foi atualizado.")

if __name__ == "__main__":
    iniciar_treinamento()
