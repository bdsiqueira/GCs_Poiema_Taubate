# Aplicação de Mapeamento de GCs Poima Churn

## Sobre a Aplicação
Esta aplicação Streamlit permite visualizar GCs em um mapa, encontrar o GC mais próximo de um endereço e consultar a lista completa de GCs.

## Funcionalidades
- **Página Home**: Visualização de mapa com todos os GCs e busca pelo GC mais próximo
- **Página Lista de GC**: Visualização tabulada de todos os GCs com filtros e opção de download

## Estrutura de Arquivos
- `main.py` - Arquivo principal da aplicação (Página Home)
- `pages/lista_gc.py` - Página de listagem dos GCs
- `constantes.py` - Constantes utilizadas na aplicação
- `layout.py` - Configurações de layout e navegação
- `diamante_branco.jpg` - Imagem de logo
- `lista_gc.csv` - Dados dos GCs

## Requisitos
Para executar a aplicação, você precisa ter Python instalado junto com as bibliotecas listadas em requirements.txt.

## Instruções de Uso
1. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

2. Execute a aplicação:
   ```
   streamlit run main.py
   ```

3. O arquivo CSV com os dados dos GCs deve estar na mesma pasta da aplicação.
