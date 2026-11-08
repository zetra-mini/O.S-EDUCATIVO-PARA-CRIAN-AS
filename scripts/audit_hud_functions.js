const fs = require('fs');
const content = fs.readFileSync('templates/hud_jarvis.html', 'utf8');

// Extrai blocos <script>
const scriptRegex = /<script(?:\s+[^>]*)?>([\s\S]*?)<\/script>/gi;
let match;
let fullScript = '';
while ((match = scriptRegex.exec(content)) !== null) {
  fullScript += '\n' + match[1];
}

// 1. Coleta todas as funções definidas
const definedFuncs = new Set([
  // Built-ins do navegador
  'fetch', 'setTimeout', 'clearTimeout', 'setInterval', 'clearInterval',
  'parseInt', 'parseFloat', 'isNaN', 'isFinite', 'encodeURIComponent', 'decodeURIComponent',
  'alert', 'confirm', 'prompt', 'requestAnimationFrame', 'cancelAnimationFrame',
  'addEventListener', 'removeEventListener', 'dispatchEvent',
  'btoa', 'atob', 'structuredClone'
]);

const defRegexes = [
  /function\s+([a-zA-Z0-9_$]+)\s*\(/g,
  /(?:window\.|const\s+|let\s+|var\s+)([a-zA-Z0-9_$]+)\s*=\s*(?:function|\([^)]*\)\s*=>|async\s+function|async\s*\([^)]*\)\s*=>)/g,
  /([a-zA-Z0-9_$]+)\s*\([^)]*\)\s*\{/g // method definitions
];

for (const reg of defRegexes) {
  while ((match = reg.exec(fullScript)) !== null) {
    definedFuncs.add(match[1]);
  }
}

// 2. Extrai todas as chamadas de funções: nome(
const callRegex = /(?<![a-zA-Z0-9_$.])([a-zA-Z0-9_$]+)\s*\(/g;
const calledFuncs = new Map();

// Palavras-chave do JS para ignorar
const jsKeywords = new Set([
  'if', 'for', 'while', 'switch', 'catch', 'function', 'return', 'typeof',
  'instanceof', 'delete', 'void', 'new', 'yield', 'await', 'import', 'export',
  'class', 'super', 'default', 'case', 'throw', 'with', 'do', 'async'
]);

while ((match = callRegex.exec(fullScript)) !== null) {
  const name = match[1];
  if (jsKeywords.has(name)) continue;
  if (definedFuncs.has(name)) continue;
  calledFuncs.set(name, (calledFuncs.get(name) || 0) + 1);
}

console.log('--- CHAMADAS A IDENTIFICADORES NÃO ENCONTRADOS COMO FUNÇÃO LOCAL ---');
for (const [name, count] of calledFuncs.entries()) {
  console.log(`${name}: ${count}x`);
}
