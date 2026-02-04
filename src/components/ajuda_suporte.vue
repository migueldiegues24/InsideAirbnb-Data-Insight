<script setup>
import { ref, reactive, inject } from 'vue';

const triggerToast = inject('triggerToast');
const triggerModal = inject('triggerModal');

const activeHelpTab = ref('faqs'); 

const faqs = [
  { 
    q: 'Como vejo propriedades com +300 dias ocupadas/ano?', 
    a: 'Vai a Alertas de Anomalias -> Filtro Tipo: Ocupação + Gravidade: Alta -> clica em Ver no mapa para ver localização.' 
  },
  { 
    q: 'Como filtro os alojamentos por zona ou freguesia?', 
    a: 'Em Mapa & Zonas, usa o dropdown Zona da Cidade. Combina com "Tipo de imóvel" e "Preço médio".' 
  },
  { 
    q: 'Como posso comparar séries temporais de diferentes períodos?', 
    a: 'Em Análise -> Séries Temporais, use o campo "Comparar com" e selecione o período (ex.: ano anterior).' 
  },
  { 
    q: 'Como exporto dados em CSV ou JSON?', 
    a: 'Vai a Exportar -> escolhe formato -> Gerar ficheiro. O sistema exporta apenas as colunas visíveis.' 
  },
  { 
    q: 'Como aplico múltiplos filtros em simultâneo?', 
    a: 'Em Filtrar & Explorar, combine o tipo de propriedade, localização, preço por noite e disponibilidade antes de clicar em Aplicar.' 
  },
  { 
    q: 'Como partilho um gráfico nas redes sociais?', 
    a: 'Clica Exportar -> Imagem 1080x1080 -> escolhe formato PNG e publica diretamente.' 
  },
  { 
    q: 'Como destaco os bairros com mais alojamentos?', 
    a: 'Em Análise -> Gráficos -> Comparações, o gráfico de barras mostra os Top Bairros automaticamente ordenados por número de alojamentos.' 
  }
];

const guides = [
  {
    title: 'Mapas e Zonas',
    steps: [
      'Escolhe o indicador que pretendes visualizar',
      'Escolhe o intervalo temporal',
      'Define se pretendes ver os dados por freguesia ou por uma área de 500',
      'Seleciona a zona e clica em "Aplicar" para atualizar o mapa.'
    ]
  },
  {
    title: 'Detetar Anomalias',
    steps: [
      'Abre Alertas de Anomalias',
      'Seleciona o tipo de alerta (ocupação, preço, etc.)',
      'Define a gravidade (alta, média, baixa)',
      'Clica no card → Ver no mapa para ver localização'
    ]
  },
  {
    title: 'Filtrar e explorar',
    steps: [
      'Selecione o tipo de propriedade e localização desejada',
      'Ajuste o intervalo de preço por noite e disponibilidade anual',
      'Para visualizar os dados clique em aplicar',
      'Utilize os separadores ("Distribuições", "Comparações") para explorar.'
    ]
  },
  {
    title: 'Gráficos / análise',
    steps: [
      'Selecione o tipo de analise (comparações, distribuições, relações)',
      'Observe os diferentes gráficos para identificar padrões',
      'Analise as métricas apresentadas (preço médio, ocupação).'
    ]
  },
  {
    title: 'Séries / análise',
    steps: [
      'Selecione a métrica que pretende analisar',
      'Defina a escala temporal e geográfica',
      'Escolha o período temporal e compare com outro intervalo',
      'Visualize os resultados no gráfico de evolução.'
    ]
  }
];

const contactForm = reactive({
  name: '',
  email: '',
  subject: '',
  message: ''
});

const submitForm = () => {
  if (!contactForm.name || !contactForm.email || !contactForm.message) {
    triggerToast("Por favor, preencha os campos obrigatórios.", "warning", "Formulário");
    return;
  }
  

  triggerModal({
    type: 'success',
    title: 'Mensagem Enviada',
    description: 'Agradecemos o seu contacto. A nossa equipa irá responder o mais brevemente possível.',
    primaryBtnText: 'Fechar'
  });
  
  contactForm.name = '';
  contactForm.email = '';
  contactForm.subject = '';
  contactForm.message = '';
};
</script>

<template>
    <div class="help-page-container">
        <div class="help-header">
            <h1 class="help-title"><span>Ajuda</span> & Suporte</h1>
        </div>

        <div class="help-tabs-container">
            <div class="help-tabs-wrapper">
                <button 
                    @click="activeHelpTab = 'faqs'" 
                    :class="['help-tab-btn', { active: activeHelpTab === 'faqs' }]">
                    FAQs
                </button>
                <button 
                    @click="activeHelpTab = 'guias'" 
                    :class="['help-tab-btn', { active: activeHelpTab === 'guias' }]">
                    Guias Rápidos
                </button>
                <button 
                    @click="activeHelpTab = 'contactos'" 
                    :class="['help-tab-btn', { active: activeHelpTab === 'contactos' }]">
                    Contactos
                </button>
            </div>
        </div>

        <div v-show="activeHelpTab === 'faqs'" class="faq-container">
            <div v-for="(item, index) in faqs" :key="index" class="faq-card">
                <h3 class="faq-question">{{ item.q }}</h3>
                <p class="faq-answer">{{ item.a }}</p>
            </div>
        </div>

        <div v-show="activeHelpTab === 'guias'" class="guides-container">
            <div v-for="(guide, index) in guides" :key="index" class="guide-card">
                <h3 class="guide-title">{{ guide.title }}</h3>
                <ol class="guide-steps">
                    <li v-for="(step, sIndex) in guide.steps" :key="sIndex">
                        {{ step }}
                    </li>
                </ol>
            </div>
        </div>

        <div v-show="activeHelpTab === 'contactos'" class="contacts-wrapper">
            
            <div class="contacts-header-text">
                <h2>Contactar Equipa InsideAirbnb</h2>
                <p>Estamos disponíveis para esclarecer dúvidas, receber sugestões ou resolver problemas técnicos.</p>
            </div>

            <div class="contacts-split-layout">
                
                <div class="contact-card form-section">
                    <h3>Preenche o Formulário</h3>
                    
                    <div class="form-group">
                        <label>Nome:</label>
                        <input type="text" v-model="contactForm.name" class="dark-input">
                    </div>

                    <div class="form-group">
                        <label>Email:</label>
                        <input type="email" v-model="contactForm.email" class="dark-input">
                    </div>

                    <div class="form-group">
                        <label>Seleciona o Assunto</label>
                        <select v-model="contactForm.subject" class="dark-input">
                            <option value="" disabled selected>Escolha uma opção</option>
                            <option value="suporte">Suporte Técnico</option>
                            <option value="sugestao">Sugestão</option>
                            <option value="dados">Dados Incorretos</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label>Mensagem:</label>
                        <textarea v-model="contactForm.message" class="dark-input" rows="6"></textarea>
                    </div>

                    <div class="form-footer">
                        <button class="submit-btn" @click="submitForm">Enviar mensagem</button>
                    </div>
                </div>

                <div class="contact-card info-section">
                    <h3>Informação de contacto</h3>
                    
                    <div class="info-list">
                        <div class="info-item">
                            <span class="icon">✉️</span>
                            <span>Email: suporte@insideairbnb.pt</span>
                        </div>
                        <div class="info-item">
                            <span class="icon">📞</span>
                            <span>Telefone: (+351) 220 999 123</span>
                        </div>
                        <div class="info-item">
                            <span class="icon">🕒</span>
                            <span>Horário: 09h – 18h (dias úteis)</span>
                        </div>
                        <div class="info-item">
                            <span class="icon">📍</span>
                            <span>Local: Câmara Municipal de Lisboa, Divisão de Urbanismo</span>
                        </div>
                    </div>

                    <div class="action-buttons-stack">
                        <button class="action-btn">
                            <span class="btn-title">Dar sugestão</span>
                            <span class="btn-desc">Tem ideias para melhorar o painel ou os filtros? Conta-nos</span>
                        </button>
                        <button class="action-btn">
                            <span class="btn-title">Reportar erro</span>
                            <span class="btn-desc">Encontrou um problema técnico ou informação incorreta?</span>
                        </button>
                        <button class="action-btn">
                            <span class="btn-title">Dados desatualizados</span>
                            <span class="btn-desc">Indica datasets que precisem de atualização</span>
                        </button>
                    </div>

                    <div class="card-bottom-info">
                        <p>Última atualização dos dados: 09/10/2025</p>
                        <p>Fonte: InsideAirbnb (Porto & Lisboa)</p>
                        <p>Equipa InsideAirbnb • Projeto IPM 2025/26</p>
                    </div>
                </div>

            </div>
        </div>
    </div>
</template>

<style scoped>

.help-page-container {
    background-color: var(--bg-escuro);
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center; 
    padding: 2rem;
    color: var(--texto-branco);
}

.help-header {
    margin-bottom: 2rem;
    text-align: center;
}

.help-title {
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--texto-branco);
}

.help-title span {
    color: var(--cor-primaria);
}

.help-tabs-container {
    width: 100%;
    display: flex;
    justify-content: center;
    margin-bottom: 3rem;
}

.help-tabs-wrapper {
    display: flex;
    gap: 30px;
}

.help-tab-btn {
    background-color: var(--bg-cartao);
    border: none;
    color: var(--texto-cinza); 
    padding: 0 12px;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.2s;
    font-size: 0.95rem;
    width: 200px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.help-tab-btn:hover {
    color: var(--texto-branco);
}

.help-tab-btn.active {
    background-color: var(--cor-primaria); 
    color: var(--texto-branco);
}

.faq-container {
    width: 100%;
    max-width: 900px;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    padding-bottom: 2rem;
}

.faq-card {
    background-color: var(--bg-cartao);
    padding: 1.25rem 1.5rem;
    border-radius: 6px;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    text-align: left;
    transition: transform 0.2s ease;
}

.faq-card:hover {
    background-color: var(--borda); 
}

.faq-question {
    color: var(--texto-branco);
    font-size: 1rem;
    font-weight: 700;
    margin: 0;
}

.faq-answer {
    color: var(--texto-muted); 
    font-size: 0.9rem;
    margin: 0;
    font-weight: 400;
    line-height: 1.4;
}

.empty-state {
    color: var(--texto-cinza);
    margin-top: 3rem;
}

.guides-container {
    width: 100%;
    max-width: 1100px; 
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); 
    gap: 1.5rem;
    padding-bottom: 2rem;
}

.guide-card {
    background-color: var(--cor-primaria);
    padding: 1.5rem;
    border-radius: 8px;
    color: var(--texto-branco);
    display: flex;
    flex-direction: column;
    gap: 1rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
    transition: transform 0.2s;
}

.guide-card:hover {
    transform: translateY(-3px);
    background-color: var(--cor-primaria-hover);
}

.guide-title {
    font-size: 1.25rem;
    font-weight: 700;
    margin: 0;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
    color: var(--texto-branco);
}

.guide-steps {
    margin: 0;
    padding-left: 1.2rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.guide-steps li {
    font-size: 0.9rem;
    line-height: 1.5;
    color: var(--texto-muted); 
}


.contacts-wrapper {
    width: 100%;
    max-width: 1200px;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.contacts-header-text {
    text-align: center;
    margin-bottom: 2rem;
}
.contacts-header-text h2 { font-size: 1.5rem; margin-bottom: 0.5rem; color: var(--texto-branco); }
.contacts-header-text p { color: var(--texto-cinza); font-size: 1rem; }


.contacts-split-layout {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
    width: 100%;
}

@media (max-width: 900px) {
    .contacts-split-layout { grid-template-columns: 1fr; }
}

.contact-card {
    background-color: var(--bg-cartao); 
    padding: 2rem;
    border-radius: 8px;
    border: 1px solid var(--borda);
    display: flex;
    flex-direction: column;
}

.contact-card h3 {
    text-align: center;
    margin-bottom: 2rem;
    color: var(--texto-branco);
    font-size: 1.2rem;
}

.form-group {
    margin-bottom: 1.2rem;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    color: var(--texto-muted);
    font-size: 0.95rem;
}

.dark-input {
    width: 100%;
    background-color: var(--bg-escuro); 
    border: 1px solid var(--borda);
    color: var(--texto-branco);
    padding: 0.8rem;
    border-radius: 4px;
    font-family: inherit;
}

.dark-input:focus {
    border-color: var(--cor-primaria);
    outline: none;
}

.form-footer {
    margin-top: auto;
    display: flex;
    justify-content: center;
    padding-top: 1rem;
}

.submit-btn {
    background-color: var(--borda); 
    color: var(--texto-branco);
    padding: 0.8rem 2rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 500;
    transition: background 0.2s;
}
.submit-btn:hover { background-color: var(--cor-primaria); }


.info-list {
    margin-bottom: 2rem;
    padding-left: 1rem;
    border-left: 2px solid var(--cor-primaria); 
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.info-item {
    display: flex;
    align-items: center;
    gap: 10px;
    color: var(--texto-muted);
    font-size: 0.95rem;
}
.info-item .icon { color: var(--texto-cinza); }

.action-buttons-stack {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-bottom: 2rem;
}

.action-btn {
    background-color: var(--cor-primaria); 
    border: none;
    border-radius: 6px;
    padding: 1rem;
    color: var(--texto-branco);
    cursor: pointer;
    text-align: center;
    transition: background 0.2s;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
}

.action-btn:hover { background-color: var(--cor-primaria-hover); }

.btn-title { font-weight: 600; font-size: 1rem; }
.btn-desc { font-size: 0.8rem; opacity: 0.9; font-weight: 300; }

.card-bottom-info {
    margin-top: auto;
    text-align: right;
    font-size: 0.75rem;
    color: var(--texto-cinza);
    line-height: 1.4;
}
</style>
