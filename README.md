# Web Scraping with Selenium for EASJ_TJSP Collection

Este script Python demonstra como usar o **Selenium** para coletar dados de processos do site **TJ-SP (Tribunal de Justiça de São Paulo)**. Ele inclui funcionalidades para gerenciar sessões de navegador, extrair informações de processos e salvar os resultados em formato JSON.

## Requisitos

- **Python 3.x**
- **Selenium**: `pip install selenium`
- **ChromeDriver**: Certifique-se de que o ChromeDriver está instalado e acessível no seu PATH.
- **Google Chrome**: Necessário para rodar o Selenium com o navegador Chrome.

## Funcionalidade

### 1. **Gerenciamento de Sessão**  
   O script pode salvar e carregar os dados da sessão de navegador (cookies e local storage), o que ajuda a manter o estado da sessão entre diferentes execuções do script, evitando a necessidade de logar repetidamente.

   - `save_session_data(driver, session_file="session_data.json")`: Salva os dados da sessão (cookies e local storage) em um arquivo JSON.
   - `load_session_data(driver, session_file="session_data.json")`: Carrega os dados da sessão de um arquivo JSON e aplica à sessão atual do navegador.

### 2. **Extração de Dados de Processos**  
   O script coleta dados de processos nas páginas do site **TJ-SP**, extraindo informações relevantes como número do processo, jurisdição, partes envolvidas e movimentações do processo.

   - `extract_case_data(driver)`: Coleta os detalhes dos processos da página atual e os armazena em um formato estruturado.

### 3. **Formatação de Dados**  
   O script utiliza uma função auxiliar, `remove_prefix()`, para limpar valores de texto, removendo prefixos específicos e garantindo que os dados extraídos tenham um formato consistente.

### 4. **Fluxo de Trabalho de Web Scraping**  
   O script navega por múltiplas páginas de dados de processos (5 páginas por padrão), extrai as informações dos processos e salva os resultados no arquivo `processos.json`.

## Como Funciona

1. **Configuração do WebDriver do Selenium**  
   O script usa o Chrome em modo headless, ou seja, sem abrir uma janela visível do navegador. Isso é ideal para tarefas de scraping.

2. **Carregar Dados da Sessão**  
   O script tenta carregar os dados da sessão previamente salvos (cookies e local storage). Se não encontrar dados da sessão, ele continua sem restaurar o estado da sessão.

3. **Extrair Dados de Processos**  
   O script acessa as páginas que contêm informações sobre os processos e coleta os dados usando seletores XPath.

4. **Salvar Resultados**  
   Após a coleta, os dados dos processos são salvos no arquivo `processos.json`.

5. **Salvar Dados da Sessão**  
   Os dados da sessão são salvos novamente para preservar o estado para futuras execuções.

## Exemplo de Uso

Para rodar o script, basta executá-lo pelo terminal:

```bash
python scraper.py
