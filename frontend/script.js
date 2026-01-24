const API_URL = 'http://localhost:5000';

let simulacaoAtiva = false;
let intervaloAnimacao = null;
let logs = [];
let passoAtual = 0;

// Elementos DOM
const numAgentesSlider = document.getElementById('num-agentes');
const numAgentesValor = document.getElementById('num-valor');
const bombasSlider = document.getElementById('percentagem-bombas');
const bombasValor = document.getElementById('bombas-valor');
const btnSimular = document.getElementById('btn-simular');
const btnMultiplas = document.getElementById('btn-multiplas');
const mensagem = document.getElementById('mensagem');
const status = document.getElementById('status');
const grid = document.getElementById('grid');
const logsDiv = document.getElementById('logs');
const btnNova = document.getElementById('btn-nova');
const resultadosDiv = document.getElementById('resultados');

// Atualizar sliders
numAgentesSlider.addEventListener('input', (e) => {
    numAgentesValor.textContent = e.target.value;
});

bombasSlider.addEventListener('input', (e) => {
    bombasValor.textContent = e.target.value + '%';
});

// Botões de abordagem
document.querySelectorAll('.mini-btn[data-value]').forEach(btn => {
    btn.addEventListener('click', (e) => {
        document.querySelectorAll('.mini-btn[data-value]').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
    });
});

function setBombas(valor) {
    bombasSlider.value = valor;
    bombasValor.textContent = valor + '%';
    logs.push(`[CONFIG] Bombas definidas para ${valor}%`);
    atualizarLogs();
}

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
    const abordagem = document.querySelector('.mini-btn.active[data-value]').dataset.value;
    const numAgentes = parseInt(numAgentesSlider.value);
    const percentagemBombas = parseInt(bombasSlider.value);
    const g2 = Array.from(document.querySelectorAll('input[name="g2"]:checked')).map(cb => cb.value);
    const g3 = Array.from(document.querySelectorAll('input[name="g3"]:checked')).map(cb => cb.value);
    
    logs.push(`[CONFIG] Abordagem: ${abordagem}, Agentes: ${numAgentes}, Bombas: ${percentagemBombas}%`);
    logs.push(`[CONFIG] Grupo 2: ${g2.join(', ') || 'Nenhum'}`);
    logs.push(`[CONFIG] Grupo 3: ${g3.join(', ') || 'Nenhum'}`);
    
    return { abordagem, num_agentes: numAgentes, percentagem_bombas: percentagemBombas, algoritmos_grupo2: g2, algoritmos_grupo3: g3 };
}

function mostrarMensagem(texto, tipo = 'erro') {
    mensagem.textContent = texto;
    mensagem.className = 'mensagem ' + tipo;
    logs.push(`[${tipo.toUpperCase()}] ${texto}`);
    atualizarLogs();
}

function atualizarLogs() {
    logsDiv.textContent = logs.slice(-15).join('\n');
    logsDiv.scrollTop = logsDiv.scrollHeight;
}

// RENDERIZAR TABULEIRO COM AGENTES - VERSÃO MELHORADA
function renderizarTabuleiroComAgentes(matriz, posicoes_agentes) {
    grid.innerHTML = '';
    
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
            const cell = document.createElement('div');
            cell.className = `cell ${celula} revealed`;
            cell.dataset.row = i;
            cell.dataset.col = j;
            
            // Adicionar emoji baseado no tipo de célula
            let emoji = '';
            switch(celula) {
                case 'L': emoji = ' '; break;
                case 'B': emoji = '💣'; break;
                case 'T': emoji = '💰'; break;
                case 'F': emoji = '🚩'; break;
            }
            
            const chave = `${i},${j}`;
            const agentesAqui = mapaAgentes[chave] || [];
            
            if (agentesAqui.length > 0) {
                // Criar container para agentes
                const agentContainer = document.createElement('div');
                agentContainer.className = 'agent-container';
                
                // Adicionar ícones dos agentes
                agentesAqui.forEach((ag, idx) => {
                    const agentIcon = document.createElement('div');
                    agentIcon.className = `agent-icon g${ag.grupo} ${agentesAqui.length > 1 ? 'multiple' : ''}`;
                    agentIcon.textContent = getAgentEmoji(ag.grupo);
                    agentIcon.title = `Grupo ${ag.grupo} - Agente ${ag.id}`;
                    agentIcon.style.transform = `translate(${(idx - (agentesAqui.length-1)/2) * 8}px, ${(idx - (agentesAqui.length-1)/2) * 8}px)`;
                    agentContainer.appendChild(agentIcon);
                });
                
                cell.appendChild(agentContainer);
                
                // Se tiver muitos agentes, mostrar contador
                if (agentesAqui.length > 1) {
                    const agentCount = document.createElement('div');
                    agentCount.className = 'agent-count';
                    agentCount.textContent = agentesAqui.length;
                    cell.appendChild(agentCount);
                }
                
                cell.textContent = '';
            } else {
                cell.textContent = emoji;
                cell.title = getCellTitle(celula);
            }
            
            grid.appendChild(cell);
        });
    });
}

function getAgentEmoji(grupo) {
    switch(grupo) {
        case 1: return '🌸';
        case 2: return '💎';
        case 3: return '🌿';
        default: return '🤖';
    }
}

function getCellTitle(tipo) {
    switch(tipo) {
        case 'L': return 'Posição Livre';
        case 'B': return 'Bomba!';
        case 'T': return 'Tesouro!';
        case 'F': return 'Bandeira Final';
        default: return 'Desconhecido';
    }
}

function atualizarMetricas(grupos) {
    grupos.forEach(g => {
        const vivosElem = document.getElementById(`g${g.grupo}-vivos`);
        const tesourosElem = document.getElementById(`g${g.grupo}-tesouros`);
        
        vivosElem.textContent = g.vivos;
        tesourosElem.textContent = g.tesouros;
        
        // Animar mudanças
        vivosElem.style.transform = 'scale(1.2)';
        tesourosElem.style.transform = 'scale(1.2)';
        setTimeout(() => {
            vivosElem.style.transform = 'scale(1)';
            tesourosElem.style.transform = 'scale(1)';
        }, 300);
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
    passoAtual = 0;
    logs = [`[${new Date().toLocaleTimeString()}] 🚀 Iniciando simulação...`];
    atualizarLogs();
    
    status.textContent = '🎬 Iniciando simulação...';
    status.style.background = '#fff1b8';
    status.style.color = '#f57f17';
    
    const config = obterConfiguracao();
    
    try {
        // 1. CRIAR SIMULAÇÃO
        const respInicial = await fetch(`${API_URL}/simular_tempo_real`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });
        
        if (!respInicial.ok) {
            throw new Error(`Erro ${respInicial.status}: ${respInicial.statusText}`);
        }
        
        const estadoInicial = await respInicial.json();
        console.log('Estado inicial:', estadoInicial);
        
        renderizarTabuleiroComAgentes(estadoInicial.tabuleiro, estadoInicial.posicoes_agentes);
        atualizarMetricas(estadoInicial.grupos);
        
        status.textContent = '⏳ Simulando passo a passo...';
        status.style.color = '#6b5ca5';
        
        logs.push(`[INFO] Tabuleiro: ${estadoInicial.tabuleiro.length}x${estadoInicial.tabuleiro[0].length}`);
        logs.push(`[INFO] ${estadoInicial.posicoes_agentes.length} agentes iniciados`);
        atualizarLogs();
        
        // 2. EXECUTAR PASSOS
        const executarPasso = async () => {
            try {
                const respPasso = await fetch(`${API_URL}/proximo_passo`, { 
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                
                if (!respPasso.ok) {
                    throw new Error(`Erro ${respPasso.status} no passo`);
                }
                
                const estado = await respPasso.json();
                
                passoAtual++;
                console.log(`Passo ${passoAtual}:`, estado.posicoes_agentes.length, 'agentes vivos');
                
                renderizarTabuleiroComAgentes(estado.tabuleiro, estado.posicoes_agentes);
                atualizarMetricas(estado.grupos);
                
                status.textContent = `⏳ Passo ${passoAtual}... ${estado.posicoes_agentes.length} agentes vivos`;
                status.style.background = '#e0f7e9';
                
                logs.push(`[PASSO ${passoAtual}] ${estado.posicoes_agentes.length} agentes, ${estado.grupos.reduce((a, g) => a + g.tesouros, 0)} tesouros`);
                atualizarLogs();
                
                if (estado.completo) {
                    clearInterval(intervaloAnimacao);
                    simulacaoAtiva = false;
                    
                    status.textContent = estado.sucesso ? '✅ Sucesso!' : '❌ Falhou';
                    status.style.background = estado.sucesso ? '#e0f7e9' : '#ffd6d6';
                    status.style.color = estado.sucesso ? '#1b5e20' : '#c62828';
                    
                    mostrarMensagem(`Simulação concluída: ${estado.razao}`, 'sucesso');
                    btnSimular.disabled = false;
                    btnMultiplas.disabled = false;
                    
                    // Mostrar resultados
                    resultadosDiv.style.display = 'block';
                    const resultadoHTML = `
                        <div class="card">
                            <h4>${estado.sucesso ? '🎉 Sucesso!' : '😞 Falha'}</h4>
                            <p><strong>Resultado:</strong> ${estado.razao}</p>
                            <p><strong>Passos totais:</strong> ${passoAtual}</p>
                            <p><strong>Agentes sobreviventes:</strong> ${estado.posicoes_agentes.length}</p>
                            <p><strong>Tesouros coletados:</strong> ${estado.grupos.reduce((a, g) => a + g.tesouros, 0)}</p>
                        </div>
                    `;
                    document.getElementById('resultado-conteudo').innerHTML = resultadoHTML;
                    
                    // Log final
                    logs.push(`[FIM] ${estado.sucesso ? 'Sucesso' : 'Falha'}: ${estado.razao}`);
                    logs.push(`[FIM] Passos: ${passoAtual}, Sobreviventes: ${estado.posicoes_agentes.length}`);
                    atualizarLogs();
                }
            } catch (erro) {
                console.error('Erro no passo:', erro);
                logs.push(`[ERRO] ${erro.message}`);
                atualizarLogs();
            }
        };
        
        // Executar a cada 400ms (um pouco mais lento para melhor visualização)
        intervaloAnimacao = setInterval(executarPasso, 400);
        
    } catch (erro) {
        console.error('ERRO:', erro);
        mostrarMensagem('Erro na conexão: ' + erro.message, 'erro');
        btnSimular.disabled = false;
        btnMultiplas.disabled = false;
        if (intervaloAnimacao) clearInterval(intervaloAnimacao);
    }
});

// Nova simulação
btnNova.addEventListener('click', () => {
    if (intervaloAnimacao) clearInterval(intervaloAnimacao);
    
    resultadosDiv.style.display = 'none';
    status.textContent = 'Aguardando configuração...';
    status.style.background = 'white';
    status.style.color = '#555';
    grid.innerHTML = '';
    logs = ['[SISTEMA] Pronto para nova simulação'];
    atualizarLogs();
    
    // Resetar métricas
    [1, 2, 3].forEach(g => {
        document.getElementById(`g${g}-vivos`).textContent = '-';
        document.getElementById(`g${g}-tesouros`).textContent = '-';
    });
    
    simulacaoAtiva = false;
    passoAtual = 0;
});

// Executar múltiplas simulações
btnMultiplas.addEventListener('click', async () => {
    mostrarMensagem('Funcionalidade de múltiplas simulações será implementada na próxima versão', 'sucesso');
});

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    logs.push('[SISTEMA] Interface de Exploração Colaborativa carregada');
    logs.push('[SISTEMA] Conectando ao servidor...');
    atualizarLogs();
    
    // Testar conexão com API
    fetch(`${API_URL}/health`)
        .then(res => logs.push('[SISTEMA] Conexão com API estabelecida'))
        .catch(() => logs.push('[ALERTA] API não disponível em localhost:5000'))
        .finally(atualizarLogs);
});

console.log('Interface de Exploração Colaborativa carregada com design premium!');