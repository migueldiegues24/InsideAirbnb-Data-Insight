# InsideAirbnb Data Insight

Aplicação web desenvolvida destinada à visualização e análise dos dados disponibilizados pelo projeto InsideAirbnb. O objetivo é permitir uma exploração clara, acessível e eficaz de informação sobre alojamento local, preços, disponibilidade, ocupação e impacto urbano, adaptada a diferentes tipos de utilizadores.

---

## Objetivos do Projeto

- Prototipar e implementar uma interface focada em usabilidade, clareza visual e fluidez de navegação.
- Apoiar três perfis de utilizadores:
  - Investigadores → filtros avançados, análise temporal, exportação.
  - Decisores públicos → dashboards executivos, alertas e mapas.
  - Ativistas → gráficos simples e comparativos para comunicação social.
- Desenvolver a implementação final em Vue.js, integrando a mock API da fase 2.

---

## Funcionalidades Principais

Exploração de dados:
- Visualização de listagens e propriedades.
- Filtros por tipo de alojamento, localização, preço e ocupação.

Análise detalhada:
- Séries temporais dos últimos 12 meses.
- KPIs como preços médios, taxas de ocupação e tendências.
- Gráficos comparativos simples e partilháveis.

Mapa de zonas:
- Representação interativa de bairros e regiões.
- Destaque das áreas com maior densidade de alojamento local.

Alertas:
- Identificação de propriedades com ocupação anual excessiva.
- Deteção de anomalias úteis para auditorias municipais.

Exportação:
- Exportação para ficheiros CSV e JSON.

Gestão de utilizador:
- Login e registo.
- Perfil, preferências e personalização básica.

---

## Estrutura do Projeto

```text
.
├── db/
│   ├── data/
│   ├── build_jsondb.py
│   └── node_modules/
│
├── src/
│   ├── assets/
│   ├── components/
│   ├── App.vue
│   ├── main.css
│   └── main.js
│
├── .gitignore
├── db.json
├── index.html
├── package-lock.json
├── package.json
├── README.md
├── Relatório fase1.pdf
├── VideoGrupo24.mp4
└── vite.config.js
```
---

## Tecnologias Utilizadas

- Vue.js 3
- HTML5 / CSS3
- Mock API (fase 2)
- Figma para prototipagem
- Datasets InsideAirbnb

---

## Prototipagem e Usabilidade

O protótipo Figma foi criado com base em princípios fundamentais de usabilidade, incluindo:

- Visibilidade do estado do sistema  
- Consistência e padrões  
- Redução da carga cognitiva  
- Acessibilidade e legibilidade  
- Preferência por reconhecimento em vez de memorização  

Cada perfil de utilizador foi integrado nas decisões de design:
- Investigador → análises profundas e exportações  
- Vereadora → dashboards e alertas  
- Ativista → gráficos simples e diretos  

Link para o protótipo Figma — adicionar quando estiver disponível.

---

## Como Executar o Projeto

Instalar dependências:
npm install

Executar em modo desenvolvimento:
npm run dev

Compilar para produção:
npm run build

---

## Apresentação Final

O vídeo final inclui:
- Apresentação do protótipo
- Avaliação e melhoria
- Demonstração da implementação
- Análise crítica  

---

