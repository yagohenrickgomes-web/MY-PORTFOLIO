/* ============================================
   YAGO HENRICK — PORTFOLIO
   Interactions
   ============================================ */

document.getElementById('year').textContent = new Date().getFullYear();

/* ---------- Loader ---------- */
window.addEventListener('load', () => {
  setTimeout(() => document.getElementById('loader').classList.add('hide'), 400);
});

/* ---------- Internal navigation (javascript:void(0) pattern) ---------- */
function nav(id){
  const headerOffset = 76;
  if(id === 'top'){
    window.scrollTo({ top: 0, behavior: 'smooth' });
  } else {
    const target = document.getElementById(id);
    if(target){
      const top = target.getBoundingClientRect().top + window.scrollY - headerOffset;
      window.scrollTo({ top, behavior: 'smooth' });
    }
  }
  closeMobileMenu();
}

/* ---------- Header scroll state ---------- */
const header = document.getElementById('siteHeader');
const backToTop = document.getElementById('backToTop');
window.addEventListener('scroll', () => {
  const scrolled = window.scrollY > 40;
  header.classList.toggle('scrolled', scrolled);
  backToTop.classList.toggle('show', window.scrollY > 600);
});
backToTop.addEventListener('click', () => nav('top'));

/* ---------- Mobile menu ---------- */
const menuToggle = document.getElementById('menuToggle');
const mobileNav = document.getElementById('mobileNav');
menuToggle.addEventListener('click', () => {
  menuToggle.classList.toggle('active');
  mobileNav.classList.toggle('open');
});
function closeMobileMenu(){
  menuToggle.classList.remove('active');
  mobileNav.classList.remove('open');
}

/* ---------- Custom cursor ---------- */
const cursorDot = document.getElementById('cursorDot');
const cursorRing = document.getElementById('cursorRing');
window.addEventListener('mousemove', (e) => {
  cursorDot.style.left = e.clientX + 'px';
  cursorDot.style.top = e.clientY + 'px';
  cursorRing.style.left = e.clientX + 'px';
  cursorRing.style.top = e.clientY + 'px';
});
document.querySelectorAll('a, button, .service-card, .project-card, input, select, textarea').forEach(el => {
  el.addEventListener('mouseenter', () => cursorRing.classList.add('hover'));
  el.addEventListener('mouseleave', () => cursorRing.classList.remove('hover'));
});

/* ---------- Scroll reveal ---------- */
const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if(entry.isIntersecting){
      entry.target.classList.add('in-view');
      revealObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.15 });
document.querySelectorAll('[data-reveal]').forEach(el => revealObserver.observe(el));

/* ---------- Animated counters ---------- */
const countObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if(entry.isIntersecting){
      const el = entry.target;
      const target = parseInt(el.getAttribute('data-count'), 10);
      let current = 0;
      const step = Math.max(1, Math.round(target / 40));
      const timer = setInterval(() => {
        current += step;
        if(current >= target){ current = target; clearInterval(timer); }
        el.textContent = current;
      }, 30);
      countObserver.unobserve(el);
    }
  });
}, { threshold: 0.5 });
document.querySelectorAll('[data-count]').forEach(el => countObserver.observe(el));

/* ---------- Public vs Private projects ---------- */
const projectModal = document.getElementById('projectModal');
const projectModalShot = document.getElementById('projectModalShot');
const projectModalTitle = document.getElementById('projectModalTitle');

document.querySelectorAll('.project-card').forEach(card => {
  const isPublic = card.getAttribute('data-public') === 'true';
  const photo = card.getAttribute('data-photo');

  card.addEventListener('click', (e) => {
    if(isPublic){
      const url = card.getAttribute('data-url');
      if(url) window.open(url, '_blank', 'noopener');
    } else if(photo){
      openLightbox(photo);
    } else {
      openProjectModal(card);
    }
  });
});

function openProjectModal(card){
  const title = card.querySelector('h3').textContent;
  const mediaClass = [...card.querySelector('.project-media').classList].find(c => c.startsWith('pm-'));
  projectModalShot.className = 'project-modal-shot ' + (mediaClass || '');
  projectModalTitle.textContent = title;
  projectModal.classList.add('open');
  document.body.style.overflow = 'hidden';
}
function closeProjectModal(){
  projectModal.classList.remove('open');
  document.body.style.overflow = '';
}

/* ---------- Lightbox (imagem em tela cheia) ---------- */
const lightbox = document.getElementById('lightbox');
const lightboxImg = document.getElementById('lightboxImg');

function openLightbox(src){
  lightboxImg.src = src;
  lightbox.classList.add('open');
  document.body.style.overflow = 'hidden';
}
function closeLightbox(){
  lightbox.classList.remove('open');
  document.body.style.overflow = '';
  lightboxImg.src = '';
}
document.addEventListener('keydown', (e) => {
  if(e.key === 'Escape'){ closeLightbox(); closeProjectModal(); }
});

/* ---------- Contact form -> email ---------- */
function enviarFormulario(){
  const name = document.getElementById('cName').value.trim();
  const email = document.getElementById('cEmail').value.trim();
  const subject = document.getElementById('cSubject').value;
  const message = document.getElementById('cMessage').value.trim();

  if(!name || !email || !message){
    alert(currentLang === 'pt' ? 'Por favor, preencha todos os campos obrigatórios.' : 'Please fill in all required fields.');
    return;
  }

  const body = `Nome: ${name}\nE-mail: ${email}\nAssunto: ${subject}\n\nMensagem:\n${message}`;
  const target = window.CONTACT_EMAIL || 'yago.contato@email.com';
  const mailto = `mailto:${target}?subject=${encodeURIComponent('Contato via Portfólio — ' + subject)}&body=${encodeURIComponent(body)}`;
  window.location.href = mailto;
}

/* ---------- Ícones de tecnologia (nos pills e nas tags dos projetos) ---------- */
const TECH_ICONS = {
  python: '<circle cx="7" cy="7" r="3.2"/><circle cx="13" cy="13" r="3.2"/><path d="M7 3.8h6a3.2 3.2 0 013.2 3.2v0M13 16.2H7A3.2 3.2 0 013.8 13v0" stroke-linecap="round"/>',
  javascript: '<rect x="2.5" y="2.5" width="15" height="15" rx="3"/><path d="M7 13.2c0 1 .6 1.6 1.6 1.6S10 14.2 10 13V7.5M12.3 11.8c.4.7 1 1 1.7 1 1 0 1.7-.5 1.7-1.3 0-1.8-3-1-3-2.8 0-.8.7-1.3 1.6-1.3.8 0 1.4.4 1.7 1" stroke-linecap="round"/>',
  html: '<path d="M4 3l1.3 14L10 18.5 14.7 17 16 3H4z"/><path d="M7 7h6.3l-.2 2.3H8.9M13 9.3l-.4 4.8L10 15l-2.5-.8-.15-1.8" stroke-linecap="round"/>',
  css: '<path d="M4 3l1.3 14L10 18.5 14.7 17 16 3H4z"/><path d="M13.2 7H6.8M12.9 9.8H7.2l.15 1.6h5.4l-.35 3.9L10 16.1l-2.35-.7-.15-1.7" stroke-linecap="round"/>',
  sql: '<ellipse cx="10" cy="5" rx="6.3" ry="2.3"/><path d="M3.7 5v10c0 1.27 2.82 2.3 6.3 2.3s6.3-1.03 6.3-2.3V5M3.7 10c0 1.27 2.82 2.3 6.3 2.3s6.3-1.03 6.3-2.3" stroke-linecap="round"/>',
  postgresql: '<ellipse cx="10" cy="5" rx="6.3" ry="2.3"/><path d="M3.7 5v10c0 1.27 2.82 2.3 6.3 2.3s6.3-1.03 6.3-2.3V5M3.7 10c0 1.27 2.82 2.3 6.3 2.3s6.3-1.03 6.3-2.3" stroke-linecap="round"/>',
  sqlite: '<ellipse cx="10" cy="5" rx="6.3" ry="2.3"/><path d="M3.7 5v10c0 1.27 2.82 2.3 6.3 2.3s6.3-1.03 6.3-2.3V5M3.7 10c0 1.27 2.82 2.3 6.3 2.3s6.3-1.03 6.3-2.3" stroke-linecap="round"/>',
  git: '<circle cx="6" cy="5" r="1.8"/><circle cx="6" cy="15" r="1.8"/><circle cx="14" cy="10" r="1.8"/><path d="M6 6.8V13.2M7.5 5H12a2 2 0 012 2v1.3" stroke-linecap="round"/>',
  github: '<rect x="2.8" y="4" width="14.4" height="10.5" rx="1.8"/><path d="M6.3 14.5v1.7M13.7 14.5v1.7M2.8 9.3h14.4" stroke-linecap="round"/>',
  docker: '<rect x="3" y="9" width="3" height="3"/><rect x="6.6" y="9" width="3" height="3"/><rect x="10.2" y="9" width="3" height="3"/><rect x="6.6" y="5.4" width="3" height="3"/><path d="M2 12.2c0 3 2.7 4.6 8 4.6 5.6 0 8.5-2.4 9-6.4-.8-.6-1.9-.8-3-.4-.3-1-1-1.7-2-2" stroke-linecap="round"/>',
  vscode: '<path d="M13.6 2.6L6 9l-3-2.3-1.4 1L5 10l-3.4 2.3 1.4 1L6 11l7.6 6.4 3.4-1.6V4.2l-3.4-1.6z"/>',
  "vs code": '<path d="M13.6 2.6L6 9l-3-2.3-1.4 1L5 10l-3.4 2.3 1.4 1L6 11l7.6 6.4 3.4-1.6V4.2l-3.4-1.6z"/>',
  "google apps script": '<path d="M6 3.5h6.5L15 6v10.5H6z" stroke-linejoin="round"/><path d="M9 9l1.5 1.5L9 12M12 9l-1.5 1.5L12 12" stroke-linecap="round" stroke-linejoin="round"/>',
  fastapi: '<path d="M11.5 2L4 11h5l-1.5 7L16 9h-5l1.5-7z" stroke-linejoin="round"/>',
  pyside6: '<rect x="2.8" y="3.5" width="14.4" height="13" rx="1.6"/><path d="M2.8 6.8h14.4" stroke-linecap="round"/><circle cx="4.6" cy="5.15" r="0.5" fill="currentColor" stroke="none"/>',
  backend: '<rect x="3" y="3" width="14" height="4.5" rx="1.2"/><rect x="3" y="9" width="14" height="4.5" rx="1.2"/><circle cx="5.5" cy="5.25" r="0.6" fill="currentColor" stroke="none"/><circle cx="5.5" cy="11.25" r="0.6" fill="currentColor" stroke="none"/>',
  excel: '<rect x="2.8" y="2.8" width="14.4" height="14.4" rx="2"/><path d="M2.8 8.2h14.4M8.4 2.8v14.4M6 5.5l2.4 2.7M8.4 5.5L6 8.2" stroke-linecap="round"/>',
  vba: '<circle cx="10" cy="10" r="2.6"/><path d="M10 3.5v2M10 14.5v2M16.5 10h-2M5.5 10h-2M14.6 5.4l-1.4 1.4M6.8 13.2l-1.4 1.4M14.6 14.6l-1.4-1.4M6.8 6.8L5.4 5.4" stroke-linecap="round"/>',
  macros: '<circle cx="10" cy="10" r="2.6"/><path d="M10 3.5v2M10 14.5v2M16.5 10h-2M5.5 10h-2M14.6 5.4l-1.4 1.4M6.8 13.2l-1.4 1.4M14.6 14.6l-1.4-1.4M6.8 6.8L5.4 5.4" stroke-linecap="round"/>',
  "power query": '<path d="M3 4h14l-5.5 6.5v5L8.5 17v-6.5z" stroke-linejoin="round"/>',
  openai: '<path d="M10 2.5l2.2 4.5 4.9.7-3.5 3.5.8 4.9-4.4-2.3-4.4 2.3.8-4.9-3.5-3.5 4.9-.7z" stroke-linejoin="round"/>',
  claude: '<path d="M10 2.5l2.2 4.5 4.9.7-3.5 3.5.8 4.9-4.4-2.3-4.4 2.3.8-4.9-3.5-3.5 4.9-.7z" stroke-linejoin="round"/>',
  gemini: '<path d="M10 2.5l2.2 4.5 4.9.7-3.5 3.5.8 4.9-4.4-2.3-4.4 2.3.8-4.9-3.5-3.5 4.9-.7z" stroke-linejoin="round"/>',
};

function injectTechIcons(){
  document.querySelectorAll('.tech-pill, .project-tags span').forEach(el => {
    if(el.dataset.iconized) return;
    const key = el.textContent.trim().toLowerCase();
    if(TECH_ICONS[key]){
      const label = el.textContent.trim();
      el.innerHTML = `<svg class="tech-icon" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.4">${TECH_ICONS[key]}</svg><span>${label}</span>`;
      el.dataset.iconized = 'true';
    }
  });
}
injectTechIcons();


let currentLang = 'pt';
const langToggle = document.getElementById('langToggle');

const i18n = {
  pt: {
    nav_about:'Sobre', nav_services:'O Que Faço', nav_tech:'Tecnologias', nav_projects:'Projetos',
    nav_experience:'Experiência', nav_education:'Formação', nav_blog:'Blog', nav_contact:'Contato', nav_cta:'Contato', nav_cv:'CV ↓',
    hero_eyebrow:'Disponível para projetos remotos e presenciais',
    hero_name:'Yago Henrick', hero_surname:'Alves Gomes',
    hero_role:'Business Process & AI Automation Specialist',
    hero_sub:'Transformando processos empresariais em soluções inteligentes utilizando Inteligência Artificial, Python e Análise de Dados.',
    hero_btn_projects:'Ver Projetos', hero_btn_contact:'Falar Comigo', hero_btn_cv:'Download CV ↓',
    pipeline_label:'Fluxo de Automação', pipe_tag1:'Dados', pipe_tag2:'IA', pipe_tag3:'Automação', pipe_tag4:'Resultado',
    scroll_cue:'Explore',
    about_eyebrow:'Sobre Mim', about_title:'Onde negócios e tecnologia se encontram.',
    about_p1:'Minha trajetória começou na administração e contabilidade, mas foi na tecnologia que encontrei a ferramenta certa para resolver problemas reais de negócio. Hoje uno essas duas visões — a de quem entende processos e a de quem constrói sistemas — para criar soluções que realmente entregam resultado.',
    about_p2:'Trabalho com Inteligência Artificial, Python e Business Intelligence para automatizar rotinas, eliminar retrabalho e transformar dados dispersos em decisões claras. Não penso apenas em código: penso em processo, em custo, em tempo economizado.',
    about_p3:'Minha visão é simples: tecnologia só tem valor quando resolve um problema de negócio de verdade.',
    stat1_label:'Projetos entregues', stat2_label:'Áreas de formação', stat3_label:'Foco em resultado',
    services_eyebrow:'O Que Faço', services_title:'Soluções que unem processo, dado e automação.',
    service1_title:'Automação de Processos', service1_desc:'Elimino tarefas repetitivas e conecto sistemas para que sua equipe foque no que realmente importa.',
    service2_title:'Inteligência Artificial', service2_desc:'Aplico IA de forma prática: extração de dados, OCR, assistentes e classificação inteligente.',
    service3_title:'Automação de Planilhas', service3_desc:'Planilhas que fazem o trabalho pesado sozinhas: cálculos, atualizações e conferências automáticas com Excel e Python.',
    service4_title:'Dashboards em Excel', service4_desc:'Planilhas inteligentes e dashboards que transformam números em decisão rápida.',
    service5_title:'Business Analytics', service5_desc:'Análise de dados aplicada à realidade do negócio, sem complexidade desnecessária.',
    service6_title:'Rotinas Fiscais e Administrativas', service6_desc:'Organização de apuração de impostos, emissão de notas e controles administrativos do dia a dia.',
    tech_eyebrow:'Tecnologias', tech_title:'Ferramentas do dia a dia.',
    projects_eyebrow:'Projetos', projects_title:'Um retrato de como eu penso soluções.',
    proj1_title:'Sistema de Gestão Empresarial', proj1_desc:'Plataforma desktop para controle de operações, contratos e indicadores em tempo real.',
    proj2_title:'Dashboard Financeiro', proj2_desc:'Painel interativo com KPIs, gráficos e projeções para tomada de decisão financeira.',
    proj3_title:'Sistema de NFC-e com OCR', proj3_desc:'Extração automática de dados fiscais em notas de consumidor via reconhecimento de imagem.',
    proj4_title:'CRM Comercial', proj4_desc:'Gestão de funil de vendas, clientes e follow-ups automatizados em um só lugar.',
    proj5_title:'Sistema para Licitações', proj5_desc:'Acompanhamento de editais, prazos e documentação com alertas automáticos.',
    proj6_title:'Dashboard de Estoque', proj6_desc:'Controle de inventário com previsão de ruptura e curva ABC automatizada.',
    proj_cta:'Ver Projeto →', proj_cta_private:'Ver Preview →',
    badge_public:'🌐 Público', badge_private:'🔒 Privado',
    modal_private_note:'Este é um sistema privado (uso interno de empresa/cliente). Por segurança, apenas a interface é exibida — sem acesso ao sistema real.',
    exp_eyebrow:'Experiência', exp_title:'Trajetória construída com resultado.',
    exp1_date:'Anterior', exp1_title:'Instituto Mais Visão', exp1_desc:'Atuação administrativa e automação de planilhas: controle de estoque, fluxo de caixa e rotinas do setor.',
    exp2_date:'Anterior', exp2_title:'CTR Contabilidade', exp2_desc:'Rotina fiscal: apuração de impostos dos regimes Simples Nacional e Lucro Presumido, emissão de notas fiscais e controle de obrigações.',
    exp3_date:'Atual', exp3_title:'Centro América', exp3_desc:'Transformo planilhas soltas em processos vivos: estruturo, automatizo e mantenho os controles que o setor usa todos os dias para decidir mais rápido e com menos erro.',
    edu_eyebrow:'Formação', edu_title:'Base sólida entre negócios e números.',
    edu1:'Bacharel em Administração', edu2:'MBA em Administração e Contabilidade Tributária',
    edu3:'Ciências Contábeis — 6º semestre', edu4:'Pós-graduação em Licitações e Contratos — em andamento', edu5:'Pós-graduação em Administração Pública — em andamento',
    cert_eyebrow:'Certificações', cert_title:'Aprendizado contínuo.', cert2:'Excel Avançado', cert3:'Automação de Processos', cert4:'Inteligência Artificial Aplicada',
    gallery_eyebrow:'Galeria', gallery_title:'Dashboards e Business Intelligence.',
    gallery1_title:'Faturamento em tempo real', gallery1_sub:'22 lojas, um painel só — do total geral ao ranking de vendedores.',
    gallery2_title:'Frota sob controle', gallery2_sub:'Agendamento, status de veículos e ordens de serviço sem planilha perdida.',
    gallery3_title:'Consumo sob a lupa', gallery3_sub:'Combustível, peças e serviços — o que cada unidade realmente consome.',
    diff_eyebrow:'Diferenciais', diff_title:'O que trago para cada projeto.',
    diff1:'Resolução de Problemas', diff2:'Aprendizado Rápido', diff3:'Visão de Negócio',
    diff4:'Mentalidade AI First', diff5:'Pensamento Analítico', diff6:'Mentalidade de Automação',
    process_eyebrow:'Processo de Trabalho', process_title:'Do diagnóstico à entrega.',
    proc1:'Descoberta', proc2:'Planejamento', proc3:'Desenvolvimento', proc4:'Testes', proc5:'Implantação', proc6:'Suporte',
    testi_eyebrow:'Depoimentos', testi_title:'O que dizem sobre o trabalho.',
    testi1:'"Automatizou um processo que consumia horas da nossa equipe todo mês. Resultado imediato."', testi1_author:'— Diretora Financeira, Consultoria',
    testi2:'"Entendeu o negócio antes de escrever a primeira linha de código. Isso fez toda diferença."', testi2_author:'— Sócio, Escritório Contábil',
    testi3:'"Dashboard entregue superou o que tínhamos em mente. Comunicação clara do início ao fim."', testi3_author:'— Gerente de Operações',
    blog_eyebrow:'Blog', blog_title:'Ideias sobre Python, IA e negócios.',
    blog1:'Automatizando relatórios mensais com Python', blog2:'Como aplicar IA sem complicar seu processo', blog3:'Dashboards que sua equipe realmente usa',
    blog_note:'Novos artigos em breve.', blog_see_all:'Ver todos os artigos →',
    contact_eyebrow:'Contato', contact_title:'Vamos conversar sobre o seu processo.',
    contact_sub:'Envie os detalhes do seu projeto e retorno por e-mail o quanto antes.',
    form_name:'Nome', form_email:'E-mail', form_subject:'Assunto',
    form_opt1:'Automação de Processos', form_opt2:'Desenvolvimento de Sistema', form_opt3:'Dashboard / BI', form_opt4:'Outro',
    form_message:'Mensagem', form_submit:'Enviar por E-mail', contact_email_label:'E-mail direto',
    footer_text:'Yago Henrick Alves Gomes — Business Process & AI Automation Specialist'
  },
  en: {
    nav_about:'About', nav_services:'What I Do', nav_tech:'Technologies', nav_projects:'Projects',
    nav_experience:'Experience', nav_education:'Education', nav_blog:'Blog', nav_contact:'Contact', nav_cta:'Contact', nav_cv:'CV ↓',
    hero_eyebrow:'Available for remote and on-site projects',
    hero_name:'Yago Henrick', hero_surname:'Alves Gomes',
    hero_role:'Business Process & AI Automation Specialist',
    hero_sub:'Turning business processes into intelligent solutions using Artificial Intelligence, Python and Data Analysis.',
    hero_btn_projects:'View Projects', hero_btn_contact:'Get in Touch', hero_btn_cv:'Download CV ↓',
    pipeline_label:'Automation Flow', pipe_tag1:'Data', pipe_tag2:'AI', pipe_tag3:'Automation', pipe_tag4:'Result',
    scroll_cue:'Explore',
    about_eyebrow:'About Me', about_title:'Where business and technology meet.',
    about_p1:'My path started in administration and accounting, but it was in technology that I found the right tool to solve real business problems. Today I combine both perspectives — understanding processes and building systems — to create solutions that truly deliver results.',
    about_p2:'I work with Artificial Intelligence, Python and Business Intelligence to automate routines, eliminate rework and turn scattered data into clear decisions. I don\'t think only in code: I think in process, cost, and time saved.',
    about_p3:'My view is simple: technology only has value when it solves a real business problem.',
    stat1_label:'Projects delivered', stat2_label:'Fields of study', stat3_label:'Focus on results',
    services_eyebrow:'What I Do', services_title:'Solutions that unite process, data and automation.',
    service1_title:'Process Automation', service1_desc:'I eliminate repetitive tasks and connect systems so your team can focus on what really matters.',
    service2_title:'Artificial Intelligence', service2_desc:'I apply AI in practical ways: data extraction, OCR, assistants and smart classification.',
    service3_title:'Spreadsheet Automation', service3_desc:'Spreadsheets that do the heavy lifting on their own: automatic calculations, updates and reconciliations with Excel and Python.',
    service4_title:'Excel Dashboards', service4_desc:'Smart spreadsheets and dashboards that turn numbers into fast decisions.',
    service5_title:'Business Analytics', service5_desc:'Data analysis applied to real business needs, without unnecessary complexity.',
    service6_title:'Tax and Administrative Routines', service6_desc:'Organizing tax filing, invoice issuance and day-to-day administrative controls.',
    tech_eyebrow:'Technologies', tech_title:'Everyday tools.',
    projects_eyebrow:'Projects', projects_title:'A snapshot of how I approach solutions.',
    proj1_title:'Enterprise Management System', proj1_desc:'Desktop platform for real-time operations, contracts and indicators control.',
    proj2_title:'Financial Dashboard', proj2_desc:'Interactive panel with KPIs, charts and projections for financial decision-making.',
    proj3_title:'OCR-based Invoice System', proj3_desc:'Automatic extraction of fiscal data from receipts through image recognition.',
    proj4_title:'Sales CRM', proj4_desc:'Sales pipeline, client management and automated follow-ups in one place.',
    proj5_title:'Public Tender Tracking System', proj5_desc:'Tracking of bids, deadlines and documentation with automatic alerts.',
    proj6_title:'Inventory Dashboard', proj6_desc:'Inventory control with stockout forecasting and automated ABC analysis.',
    proj_cta:'View Project →', proj_cta_private:'View Preview →',
    badge_public:'🌐 Public', badge_private:'🔒 Private',
    modal_private_note:'This is a private system (internal use for a company/client). For security reasons, only the interface is shown — no access to the real system.',
    exp_eyebrow:'Experience', exp_title:'A track record built on results.',
    exp1_date:'Previous', exp1_title:'Instituto Mais Visão', exp1_desc:'Administrative work and spreadsheet automation: inventory control, cash flow and department routines.',
    exp2_date:'Previous', exp2_title:'CTR Contabilidade', exp2_desc:'Tax routine: tax filing under the Simples Nacional and Lucro Presumido regimes, invoice issuance and compliance control.',
    exp3_date:'Current', exp3_title:'Centro América', exp3_desc:'I turn loose spreadsheets into living processes: structuring, automating and maintaining the controls the department relies on every day to decide faster and with fewer errors.',
    edu_eyebrow:'Education', edu_title:'A solid foundation between business and numbers.',
    edu1:'Bachelor\'s Degree in Business Administration', edu2:'MBA in Administration and Tax Accounting',
    edu3:'Accounting Sciences — 6th semester', edu4:'Postgraduate in Public Tenders and Contracts — in progress', edu5:'Postgraduate in Public Administration — in progress',
    cert_eyebrow:'Certifications', cert_title:'Continuous learning.', cert2:'Advanced Excel', cert3:'Process Automation', cert4:'Applied Artificial Intelligence',
    gallery_eyebrow:'Gallery', gallery_title:'Dashboards and Business Intelligence.',
    gallery1_title:'Real-time revenue', gallery1_sub:'22 stores, one dashboard — from total revenue to the sales ranking.',
    gallery2_title:'Fleet under control', gallery2_sub:'Scheduling, vehicle status and service orders without a lost spreadsheet.',
    gallery3_title:'Consumption under the lens', gallery3_sub:'Fuel, parts and services — what each unit actually consumes.',
    diff_eyebrow:'Differentials', diff_title:'What I bring to every project.',
    diff1:'Problem Solving', diff2:'Fast Learning', diff3:'Business Vision',
    diff4:'AI First Mindset', diff5:'Analytical Thinking', diff6:'Automation Mindset',
    process_eyebrow:'Work Process', process_title:'From diagnosis to delivery.',
    proc1:'Discover', proc2:'Planning', proc3:'Development', proc4:'Testing', proc5:'Deployment', proc6:'Support',
    testi_eyebrow:'Testimonials', testi_title:'What people say about the work.',
    testi1:'"Automated a process that took hours of our team\'s time every month. Immediate results."', testi1_author:'— Finance Director, Consultancy',
    testi2:'"Understood the business before writing the first line of code. That made all the difference."', testi2_author:'— Partner, Accounting Firm',
    testi3:'"The delivered dashboard exceeded what we had in mind. Clear communication from start to finish."', testi3_author:'— Operations Manager',
    blog_eyebrow:'Blog', blog_title:'Thoughts on Python, AI and business.',
    blog1:'Automating monthly reports with Python', blog2:'How to apply AI without complicating your process', blog3:'Dashboards your team will actually use',
    blog_note:'New articles coming soon.', blog_see_all:'See all articles →',
    contact_eyebrow:'Contact', contact_title:'Let\'s talk about your process.',
    contact_sub:'Send over your project details and I\'ll reply by email as soon as possible.',
    form_name:'Name', form_email:'Email', form_subject:'Subject',
    form_opt1:'Process Automation', form_opt2:'System Development', form_opt3:'Dashboard / BI', form_opt4:'Other',
    form_message:'Message', form_submit:'Send by Email', contact_email_label:'Direct email',
    footer_text:'Yago Henrick Alves Gomes — Business Process & AI Automation Specialist'
  }
};

// Mescla os textos vindos do banco de dados (editados via /admin) com o dicionário estático
if(window.DYNAMIC_I18N){
  Object.assign(i18n.pt, window.DYNAMIC_I18N.pt || {});
  Object.assign(i18n.en, window.DYNAMIC_I18N.en || {});
}

function applyLang(lang){
  currentLang = lang;
  document.documentElement.lang = lang === 'pt' ? 'pt-BR' : 'en';
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if(i18n[lang][key]) el.textContent = i18n[lang][key];
  });
  document.querySelectorAll('.lang-opt').forEach(el => {
    el.classList.toggle('active', el.getAttribute('data-lang') === lang);
  });
}

langToggle.addEventListener('click', () => {
  applyLang(currentLang === 'pt' ? 'en' : 'pt');
});
