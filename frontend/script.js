// script_tempo_real.js - Visualização em Tempo Real

const API_URL = 'http://localhost:5000';

let simulacaoAtiva = false;
let intervaloAnimacao = null;

// Elementos DOM
const numAgentesSlider = document.getElementById('num-agentes');
const numAgentesValor = document.getElementById('num-valor');
const bombasSlider = document.getElementById('percentagem-bombas');
const bombasValor = document.getElementById('bombas-valor');
const btnSimular = document.getElementById('btn-simular');
const btnMultiplas = document.getElementById('btn-multiplas');
const mensagem = document.getElementById('mensagem');
const status = document.getElementById('status');
const tabuleiro = document.getElementById('tabuleiro');

// Atualizar sliders
numAgentesSlider.addEventListener('input', (e) => {
    numAgentesValor.textContent = e.target.value;
});

bombasSlider.addEventListener('input', (e) => {
    bombasValor.textContent = e.target.value + '%';
});

// Validação
function validarAlgoritmos() {
    const g2 = Array.from(document.querySelectorAll('input[name="g2"]:checked')).map(cb => cb.value);
    const g3 = Array.from(document.querySelectorAll('input[name="g3"]:checked')).map(cb => cb.value);
    
    if (g2.length === 0 && g3.length === 0) return { valido: true };
    
    if (g2.length === g3.length && g2.every(alg => g3.includes(alg))) {
        return { valido: false, erro: 'Grupos 2 e 3 devem ter algoritmos DIFERENTES!' };
    }
    
    return { valido: true };
}

function obterConfiguracao() {
    const abordagem = document.querySelector('input[name="abordagem"]:checked').value;
    const numAgentes = parseInt(numAgentesSlider.value);
    const percentagemBombas = parseInt(bombasSlider.value);
    const g2 = Array.from(document.querySelectorAll('input[name="g2"]:checked')).map(cb => cb.value);
    const g3 = Array.from(document.querySelectorAll('input[name="g3"]:checked')).map(cb => cb.value);
    
    return { abordagem, num_agentes: numAgentes, percentagem_bombas: percentagemBombas, algoritmos_grupo2: g2, algoritmos_grupo3: g3 };
}

function mostrarMensagem(texto, tipo = 'erro') {
    mensagem.textContent = texto;
    mensagem.className = 'mensagem ' + tipo;
    mensagem.style.display = 'block';
    setTimeout(() => mensagem.style.display = 'none', 5000);
}

// RENDERIZAR TABULEIRO COM AGENTES
function renderizarTabuleiroComAgentes(matriz, posicoes_agentes) {
    console.log('Renderizando:', matriz.length, 'x', matriz[0].length, '| Agentes:', posicoes_agentes.length);
    
    tabuleiro.innerHTML = '';
    tabuleiro.style.display = 'grid';
    
    // Criar mapa de agentes por posição
    const mapaAgentes = {};
    posicoes_agentes.forEach(ag => {
        const chave = `${ag.posicao[0]},${ag.posicao[1]}`;
        if (!mapaAgentes[chave]) mapaAgentes[chave] = [];
        mapaAgentes[chave].push(ag);
    });
    
    // Renderizar células
    matriz.forEach((linha, i) => {
        linha.forEach((celula, j) => {
            const div = document.createElement('div');
            div.className = `celula ${celula}`;
            
            const chave = `${i},${j}`;
            const agentesAqui = mapaAgentes[chave] || [];
            
            if (agentesAqui.length > 0) {
                // Mostrar agentes
                div.innerHTML = agentesAqui.map(ag => 
                    `<span class="agente g${ag.grupo}" title="G${ag.grupo} A${ag.id}">●</span>`
                ).join('');
                div.style.position = 'relative';
            } else {
                div.textContent = celula;
            }
            
            tabuleiro.appendChild(div);
        });
    });
}

function atualizarMetricas(grupos) {
    grupos.forEach(g => {
        document.getElementById(`g${g.grupo}-vivos`).textContent = g.vivos;
        document.getElementById(`g${g.grupo}-tesouros`).textContent = g.tesouros;
    });
}

// SIMULAR EM TEMPO REAL
btnSimular.addEventListener('click', async () => {
    const validacao = validarAlgoritmos();
    if (!validacao.valido) {
        mostrarMensagem(validacao.erro, 'erro');
        return;
    }
    
    btnSimular.disabled = true;
    btnMultiplas.disabled = true;
    simulacaoAtiva = true;
    
    status.textContent = '🎬 Iniciando simulação tempo real...';
    status.style.background = '#fff3cd';
    
    const config = obterConfiguracao();
    
    try {
        // 1. CRIAR SIMULAÇÃO
        const respInicial = await fetch(`${API_URL}/simular_tempo_real`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });
        
        const estadoInicial = await respInicial.json();
        console.log('Estado inicial:', estadoInicial);
        
        renderizarTabuleiroComAgentes(estadoInicial.tabuleiro, estadoInicial.posicoes_agentes);
        atualizarMetricas(estadoInicial.grupos);
        
        status.textContent = '⏳ Simulando passo a passo...';
        
        // 2. EXECUTAR PASSOS
        let passo = 0;
        
        const executarPasso = async () => {
            const respPasso = await fetch(`${API_URL}/proximo_passo`, { method: 'POST' });
            const estado = await respPasso.json();
            
            passo++;
            console.log(`Passo ${passo}:`, estado.posicoes_agentes.length, 'agentes vivos');
            
            renderizarTabuleiroComAgentes(estado.tabuleiro, estado.posicoes_agentes);
            atualizarMetricas(estado.grupos);
            
            status.textContent = `⏳ Passo ${passo}...`;
            
            if (estado.completo) {
                clearInterval(intervaloAnimacao);
                simulacaoAtiva = false;
                
                status.textContent = estado.sucesso ? '✅ Sucesso!' : '❌ Falhou';
                status.style.background = estado.sucesso ? '#c6f6d5' : '#fed7d7';
                
                mostrarMensagem(`Simulação concluída: ${estado.razao}`, 'sucesso');
                btnSimular.disabled = false;
                btnMultiplas.disabled = false;
            }
        };
        
        // Executar a cada 200ms
        intervaloAnimacao = setInterval(executarPasso, 200);
        
    } catch (erro) {
        console.error('ERRO:', erro);
        mostrarMensagem('Erro: ' + erro.message, 'erro');
        btnSimular.disabled = false;
        btnMultiplas.disabled = false;
        if (intervaloAnimacao) clearInterval(intervaloAnimacao);
    }
});

// Estilo CSS para agentes (adicionar dinamicamente)
const style = document.createElement('style');
style.textContent = `
.celula {
    position: relative;
    font-size: 0.7em;
}
.agente {
    font-size: 32px;
    font-weight: bold;
    display: inline-block;
    animation: pulse 0.5s ease-in-out;
    line-height: 1;
}
.agente.g1 { color: #FF6B6B; }
.agente.g2 { color: #4ECDC4; }
.agente.g3 { color: #95E1D3; }
@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.2); }
}
`;
document.head.appendChild(style);

console.log('Script tempo real carregado!');