# Livraria Aoros

## Introdução

Sistema de livraria feito em python.

## Estrutura de pastas 

- static - armazena arquivos estáticos, ou seja, arquivos que não mudam dinamicamente no servidor 
- templates - arquivos HTML usados como modelos para renderizar as páginas
- meu_sistema_livraria - armazenamento dos dados da aplicação

## Setup

### Criar ambiente virtual

```bash
python -m venv .venv
```

### Ativar ambiente virtual

#### Unix
```bash
. .venv/bin/activate
```

#### Windows
```powershell
.\.venv\Scripts\Activate.ps1
```

### Baixar dependências
```bash
pip install -r requirements.txt
```

### Iniciar projeto 
```bash
python app.py
```
