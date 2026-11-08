const puppeteer = require('puppeteer-core');
const path = require('path');
const fs = require('fs');

const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const SCREENSHOTS_DIR = path.join(__dirname, '..', 'docs', 'screenshots');

if (!fs.existsSync(SCREENSHOTS_DIR)) {
  fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true });
}

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function capture() {
  console.log('🚀 Iniciando Chrome Headless para captura dos prints...');
  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: 'new',
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-gpu',
      '--window-size=1024,640',
      '--autoplay-policy=no-user-gesture-required'
    ],
    defaultViewport: {
      width: 1024,
      height: 600,
      deviceScaleFactor: 1.5 // Imagem nítida em alta definição
    }
  });

  const page = await browser.newPage();

  // 1. HUD Principal (Sala de Brincar do Pou / Jarvis)
  console.log('📸 1. Capturando HUD Principal...');
  await page.goto('http://localhost:8000/', { waitUntil: 'networkidle2' });
  await sleep(1500);
  await page.screenshot({ path: path.join(SCREENSHOTS_DIR, '01_hud_jarvis_sala_brincar.png') });

  // 2. Quartel-General das Missões do Herói (v3.6.4)
  console.log('📸 2. Capturando Quartel-General das Missões...');
  await page.evaluate(() => {
    if (typeof abrirModalMissoesHeroi === 'function') abrirModalMissoesHeroi();
  });
  await sleep(1500);
  await page.screenshot({ path: path.join(SCREENSHOTS_DIR, '02_missoes_do_heroi.png') });

  // 3. Biblioteca Mágica de Histórias (Estante)
  console.log('📸 3. Capturando Estante da Biblioteca de Histórias...');
  await page.evaluate(() => {
    if (typeof openBooksLibrary === 'function') openBooksLibrary();
  });
  await sleep(1500);
  await page.screenshot({ path: path.join(SCREENSHOTS_DIR, '03_biblioteca_historias.png') });

  // 4. Tela de Conquista e Celebração do Livro
  console.log('📸 4. Capturando Tela de Conquista do Livro (Celebração)...');
  await page.evaluate(() => {
    const b = document.getElementById('modal-body');
    if (typeof concluirLivroComCelebracao === 'function' && b) {
      concluirLivroComCelebracao(b, 0);
    }
  });
  await sleep(1200);
  await page.screenshot({ path: path.join(SCREENSHOTS_DIR, '04_leitor_livro_celebracao.png') });

  // 5. Parque dos Dinossauros & Escavação de Fósseis
  console.log('📸 5. Capturando Parque dos Dinossauros...');
  await page.evaluate(() => {
    if (typeof openDinosaurFossilsGame === 'function') openDinosaurFossilsGame();
  });
  await sleep(1200);
  await page.screenshot({ path: path.join(SCREENSHOTS_DIR, '05_parque_dinossauros.png') });

  // 6. Jogo dos 7 Erros (Detetive Stark)
  console.log('📸 6. Capturando Detetive Stark (7 Erros)...');
  await page.evaluate(() => {
    if (typeof openDetectiveErrorsGame === 'function') openDetectiveErrorsGame();
  });
  await sleep(1200);
  await page.screenshot({ path: path.join(SCREENSHOTS_DIR, '06_detetive_7_erros.png') });

  // 7. Lousa Mágica Holográfica Neon
  console.log('📸 7. Capturando Lousa Neon...');
  await page.evaluate(() => {
    if (typeof openStarkPaint === 'function') openStarkPaint();
  });
  await sleep(1200);
  await page.screenshot({ path: path.join(SCREENSHOTS_DIR, '07_lousa_magica_neon.png') });

  // 8. Painel Administrativo dos Pais (/admin)
  console.log('📸 8. Capturando Painel Administrativo dos Pais...');
  await page.goto('http://localhost:8000/admin', { waitUntil: 'networkidle2' });
  await sleep(1500);
  await page.screenshot({ path: path.join(SCREENSHOTS_DIR, '08_painel_pais_admin.png') });

  // 9. Quarto de Engenharia (Blockly)
  console.log('📸 9. Capturando Quarto de Engenharia...');
  await page.goto('http://localhost:8000/engenharia', { waitUntil: 'networkidle2' });
  await sleep(2000);
  await page.screenshot({ path: path.join(SCREENSHOTS_DIR, '09_quarto_engenharia.png') });

  await browser.close();
  console.log('✅ Todas as 9 capturas foram concluídas e salvas com sucesso em docs/screenshots/!');
}

capture().catch(err => {
  console.error('❌ Erro na captura de tela:', err);
  process.exit(1);
});
