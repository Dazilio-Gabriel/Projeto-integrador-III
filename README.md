# 🚦 Análise de Acidentes de Trânsito na Grande Vitória – ES

> **Projeto Integrador III** · Ciência da Computação · Centro Universitário FAESA  
> Parceria: Mentor Educação e Tecnologia LTDA

---

## 📌 Descrição

Este repositório reúne o código-fonte, análises e documentação do **Projeto Integrador III**, que aplica técnicas de **Ciência de Dados**, **Machine Learning** e **Business Intelligence** para investigar padrões de acidentes de trânsito na Grande Vitória e em rodovias federais do Espírito Santo.

Os dados utilizados são públicos e abertos, fornecidos pela **Polícia Rodoviária Federal (PRF)**.

---

## 🎯 Objetivo

Analisar dados de acidentes de trânsito para identificar padrões **temporais**, **espaciais** e **causais**, indo além da estatística descritiva ao aplicar:

- Modelos de **Machine Learning** para classificação de risco
- **Painéis de BI** interativos para suporte à tomada de decisão de gestores públicos

---

## 🌍 Impacto Social & ODS

O projeto está alinhado aos seguintes **Objetivos de Desenvolvimento Sustentável da ONU**:

| ODS | Descrição |
|-----|-----------|
| **ODS 3** | Saúde e Bem-Estar — prevenção e redução de sinistros |
| **ODS 9** | Indústria, Inovação e Infraestrutura |
| **ODS 11** | Cidades e Comunidades Sustentáveis |

---

## 👥 Equipe

Estudantes do **6º período de Ciência da Computação** – FAESA:

- **Gabriel Dazilio Fanchiotti**
- **Devandro Munaldi Junior**
- **Ramiro Biazatti Rocha**

**Orientadores:** Prof. Howard Roatti · Prof. Wesley Pereira da Silva

---

## 🛠️ Tecnologias

| Área | Ferramentas |
|------|------------|
| Linguagem | Python 3.x |
| Manipulação de dados | Pandas, NumPy |
| Machine Learning | Scikit-Learn |
| Visualização | Matplotlib, Seaborn |
| Business Intelligence | Power BI / Metabase *(a definir)* |
| Frontend (dashboard) | React, TypeScript, Vite, Tailwind CSS |
| Versionamento | Git & GitHub |

---

## 📁 Estrutura do Repositório

```
📦 Projeto-integrador-III
├── 📂 data/               # Dados brutos e processados
│   └── datatran2025.csv   # Base da PRF (2025)
├── 📂 notebooks/          # Jupyter Notebooks (EDA, modelos)
├── 📂 src/                # Scripts Python de limpeza e ML
├── 📂 docs/               # Relatórios das entregas
│   └── Projeto_Transito.pdf
├── 📂 dashboard/          # Aplicação web React (visualização interativa)
└── README.md
```

---

## 🚀 Como Rodar o Projeto

### Pré-requisitos

- [Python 3.10+](https://python.org)
- [Node.js 18+](https://nodejs.org)
- [Git](https://git-scm.com)

---

### 1. Clonar o repositório

```bash
git clone https://github.com/Dazilio-Gabriel/Projeto-integrador-III.git
cd Projeto-integrador-III
```

---

### 2. Análise em Python (notebooks / scripts)

```bash
# Criar e ativar ambiente virtual
python3 -m venv venv
source venv/bin/activate          # Mac/Linux
# venv\Scripts\activate           # Windows

# Instalar dependências
pip install pandas numpy matplotlib seaborn scikit-learn jupyter

# Abrir os notebooks
jupyter notebook notebooks/
```

---

### 3. Dashboard React (visualização interativa)

> Se o dashboard estiver em um repositório separado, clone-o primeiro:
>
> ```bash
> git clone https://github.com/devandro1/An-lise-de-Acidentes-de-Tr-nsito-na-Grande-Vit-ria---ES.git
> cd An-lise-de-Acidentes-de-Tr-nsito-na-Grande-Vit-ria---ES
> ```

```bash
# Instalar dependências
npm install

# Rodar em modo desenvolvimento
npm run dev
```

Acesse em: **http://localhost:8080**

---

## 📅 Cronograma de Entregas

| Entrega | Período | Descrição | Status |
|---------|---------|-----------|--------|
| **Entrega 1** | 01/04 – 05/04 | Escopo, justificativa, metodologia e plano de trabalho | ✅ Concluída |
| **Entrega 2** | 06/05 – 10/05 | Protótipo funcional com EDA e modelos preliminares | ⚙️ Em andamento |
| **Entrega 3** | 17/06 – 21/06 | MVP final com demonstração e documentação técnica | 🎯 Planejada |

---

## 📄 Documentação

O documento completo do projeto está disponível em [`Projeto_Transito.pdf`](./Projeto_Transito.pdf).

---

## 📜 Licença

Projeto acadêmico desenvolvido para fins educacionais.  
Dados utilizados são de domínio público (PRF / dados.gov.br).
