// ✅ SCRIPT ATUALIZADO COM VISUALIZAÇÃO DE AGENTES EM TEMPO REAL

const API_URL = 'http://localhost:5000';

// Cores dos grupos
const CORES_GRUPOS = {
    1: '#800020',  // Grupo 1 - Vinho
    2: '#F4C430',  // Grupo 2 - Ouro
    3: '#043927'   // Grupo 3 - Verde escuro
};

let simulacaoAtiva = false;
let simulacaoEmPausa = false;
let intervaloAnimacao = null;

// Configuração inicial
document.getElementById('num-agentes').addEventListener('input', (e) => {
    document.getElementById('num-valor').textContent = e.target.value;
});

document.getElementById('percentagem-bombas').addEventListener('input', (e) => {
    document.getElementById('bombas-valor').textContent = `${e.target.value}%`;
});

// Seleção de abordagem
document.querySelectorAll('.mini-btn[data-value]').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.mini-btn[data-value]').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
    });
});

// Botão Iniciar Simulação
document.getElementById('btn-simular').addEventListener('click', iniciarSimulacao);

// ✅ NOVO: Botão Pausar
const btnPausar = document.getElementById('btn-pausar');
if (btnPausar) {
    btnPausar.addEventListener('click', () => {
        simulacaoEmPausa = !simulacaoEmPausa;
        btnPausar.textContent = simulacaoEmPausa ? '▶️ Continuar' : '⏸️ Pausar';
        btnPausar.classList.toggle('btn-pausado');
    });
}

// ✅ NOVO: Botão Parar
const btnParar = document.getElementById('btn-parar');
if (btnParar) {
    btnParar.addEventListener('click', () => {
        pararSimulacao();
    });
}

function pararSimulacao() {
    simulacaoAtiva = false;
    simulacaoEmPausa = false;
    if (intervaloAnimacao) {
        clearInterval(intervaloAnimacao);
        intervaloAnimacao = null;
    }
    
    document.getElementById('btn-simular').disabled = false;
    const btnPausar = document.getElementById('btn-pausar');
    const btnParar = document.getElementById('btn-parar');
    if (btnPausar) btnPausar.disabled = true;
    if (btnParar) btnParar.disabled = true;
    
    adicionarLog('🛑 Simulação interrompida pelo usuário');
}

async function iniciarSimulacao() {
    if (simulacaoAtiva) return;
    
    // Obter configurações
    const abordagem = document.querySelector('.mini-btn[data-value].active')?.dataset.value || 'A';
    const numAgentes = parseInt(document.getElementById('num-agentes').value);
    const percentagemBombas = parseInt(document.getElementById('percentagem-bombas').value);
    
    const alg_g2 = Array.from(document.querySelectorAll('input[name="g2"]:checked')).map(cb => cb.value);
    const alg_g3 = Array.from(document.querySelectorAll('input[name="g3"]:checked')).map(cb => cb.value);
    
    // Validar
    if (alg_g2.length > 0 && alg_g3.length > 0 && 
        JSON.stringify(alg_g2.sort()) === JSON.stringify(alg_g3.sort())) {
        mostrarMensagem('❌ Erro: Algoritmos dos grupos 2 e 3 devem ser diferentes!', 'erro');
        return;
    }
    
    limparLogs();
    adicionarLog('🚀 Iniciando simulação...');
    
    try {
        // Criar simulação
        const response = await fetch(`${API_URL}/simular_tempo_real`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                abordagem,
                num_agentes: numAgentes,
                percentagem_bombas: percentagemBombas,
                algoritmos_grupo2: alg_g2,
                algoritmos_grupo3: alg_g3
            })
        });
        
        const estadoInicial = await response.json();
        
        if (estadoInicial.erro) {
            mostrarMensagem(`❌ ${estadoInicial.erro}`, 'erro');
            return;
        }
        
        simulacaoAtiva = true;
        simulacaoEmPausa = false;
        
        // Habilitar controles
        document.getElementById('btn-simular').disabled = true;
        const btnPausar = document.getElementById('btn-pausar');
        const btnParar = document.getElementById('btn-parar');
        if (btnPausar) btnPausar.disabled = false;
        if (btnParar) btnParar.disabled = false;
        
        // Renderizar estado inicial
        renderizarEstado(estadoInicial);
        adicionarLog(`✅ Simulação criada | Abordagem ${abordagem} | ${numAgentes} agentes por grupo`);
        
        // Iniciar animação
        intervaloAnimacao = setInterval(async () => {
            if (!simulacaoEmPausa && simulacaoAtiva) {
                await executarProximoPasso();
            }
        }, 300); // 300ms entre passos
        
    } catch (error) {
        mostrarMensagem(`❌ Erro: ${error.message}`, 'erro');
        adicionarLog(`❌ Erro: ${error.message}`);
    }
}

async function executarProximoPasso() {
    try {
        const response = await fetch(`${API_URL}/proximo_passo`, {
            method: 'POST'
        });
        
        const estado = await response.json();
        
        if (estado.erro) {
            pararSimulacao();
            mostrarMensagem(`❌ ${estado.erro}`, 'erro');
            return;
        }
        
        renderizarEstado(estado);
        
        // Se completou
        if (estado.completo) {
            pararSimulacao();
            
            if (estado.sucesso) {
                const grupoVencedor = estado.grupo_vencedor;
                mostrarMensagem(`🏆 VITÓRIA DO GRUPO ${grupoVencedor}! ${estado.razao}`, 'sucesso');
                adicionarLog(`🏆 GRUPO ${grupoVencedor} VENCEU: ${estado.razao}`);
            } else {
                mostrarMensagem(`💀 ${estado.razao}`, 'erro');
                adicionarLog(`💀 ${estado.razao}`);
            }
            
            // Mostrar estatísticas finais
            mostrarEstatisticasFinais(estado);
        }
        
    } catch (error) {
        pararSimulacao();
        mostrarMensagem(`❌ Erro: ${error.message}`, 'erro');
    }
}

function renderizarEstado(estado) {
    const grid = document.getElementById('grid');
    grid.innerHTML = '';
    
    const tabuleiro = estado.tabuleiro;
    const agentes = estado.agentes || [];
    
    // Criar grid 10x10
    for (let i = 0; i < 10; i++) {
        for (let j = 0; j < 10; j++) {
            const celula = document.createElement('div');
            celula.className = 'celula';
            celula.dataset.pos = `${i},${j}`;
            
            const tipo = tabuleiro[i][j];
            celula.classList.add(`tipo-${tipo}`);
            
            // ✅ VISUALIZAR AGENTES
            const agentesNaCelula = agentes.filter(a => a.posicao[0] === i && a.posicao[1] === j);
            
            if (agentesNaCelula.length > 0) {
                const containerAgentes = document.createElement('div');
                containerAgentes.className = 'agentes-container';
                
                agentesNaCelula.forEach(agente => {
                    const agenteDiv = document.createElement('div');
                    agenteDiv.className = 'agente';
                    agenteDiv.style.backgroundColor = CORES_GRUPOS[agente.grupo];
                    agenteDiv.title = `Grupo ${agente.grupo} | Agente ${agente.id} | Tesouros: ${agente.tesouros}`;
                    
                    // Mostrar imunidade
                    if (agente.imunidades > 0) {
                        agenteDiv.classList.add('com-escudo');
                        const escudo = document.createElement('span');
                        escudo.className = 'escudo';
                        escudo.textContent = agente.imunidades;
                        agenteDiv.appendChild(escudo);
                    }
                    
                    containerAgentes.appendChild(agenteDiv);
                });
                
                celula.appendChild(containerAgentes);
            }
            
            // Ícone do tipo de célula (menor se houver agentes)
            const icone = document.createElement('span');
            icone.className = 'icone-tipo';
            if (agentesNaCelula.length > 0) {
                icone.style.fontSize = '10px';
                icone.style.opacity = '0.5';
            }
            
            switch(tipo) {
                case 'L': icone.textContent = ''; break;
                case 'B': icone.textContent = '💣'; break;
                case 'T': icone.textContent = '💎'; break;
                case 'F': icone.textContent = '🚩'; break;
            }
            celula.appendChild(icone);
            
            grid.appendChild(celula);
        }
    }
    
    // Atualizar métricas
    if (estado.grupos) {
        estado.grupos.forEach(g => {
            document.getElementById(`g${g.grupo}-vivos`).textContent = `${g.vivos}/${g.total}`;
            document.getElementById(`g${g.grupo}-tesouros`).textContent = g.tesouros;
            const celuasEl = document.getElementById(`g${g.grupo}-celulas`);
            if (celuasEl) celuasEl.textContent = g.celulas_exploradas;
        });
    }
    
    // ✅ NOVO: Processar e mostrar eventos nos logs
    if (estado.eventos && estado.eventos.length > 0) {
        estado.eventos.forEach(evento => {
            let logMsg = '';
            const grupoEmoji = evento.grupo === 1 ? '🌸' : evento.grupo === 2 ? '💎' : '🌿';
            
            switch(evento.tipo) {
                case 'movimento':
                    const emojiCelula = {
                        'livre': '✅',
                        'tesouro': '💎',
                        'bomba_desativada': '🛡️',
                        'bandeira': '🚩'
                    }[evento.evento_celula] || '➡️';
                    
                    logMsg = `${grupoEmoji} G${evento.grupo} A${evento.agente}: (${evento.de[0]},${evento.de[1]}) → (${evento.para[0]},${evento.para[1]}) ${emojiCelula}`;
                    
                    if (evento.evento_celula === 'tesouro') {
                        logMsg += ' [+1 Tesouro]';
                    } else if (evento.evento_celula === 'bomba_desativada') {
                        logMsg += ' [Bomba desativada]';
                    } else if (evento.evento_celula === 'bandeira') {
                        logMsg += ' [BANDEIRA ENCONTRADA!]';
                    }
                    break;
                    
                case 'morte':
                    logMsg = `${grupoEmoji} G${evento.grupo} A${evento.agente}: ☠️ MORREU em (${evento.para[0]},${evento.para[1]})`;
                    break;
                    
                case 'sem_movimento':
                    logMsg = `${grupoEmoji} G${evento.grupo} A${evento.agente}: ⏸️ Parado em (${evento.posicao[0]},${evento.posicao[1]}) - ${evento.razao}`;
                    break;
            }
            
            if (logMsg) {
                adicionarLog(logMsg);
            }
        });
    }
    
    // Atualizar status
    document.getElementById('status').textContent = 
        `Passo ${estado.passo} | ${simulacaoEmPausa ? '⏸️ PAUSADO' : '▶️ Em execução'}`;
}

function mostrarEstatisticasFinais(estado) {
    const panel = document.getElementById('resultados');
    const conteudo = document.getElementById('resultado-conteudo');
    
    let html = '<div class="stats-finais">';
    
    html += `<div class="stat-destaque">`;
    html += `<h4>⏱️ Tempo Total</h4>`;
    html += `<p>${estado.tempo_segundos?.toFixed(2) || '0.00'}s</p>`;
    html += `</div>`;
    
    html += `<div class="stat-destaque">`;
    html += `<h4>📊 Passos Executados</h4>`;
    html += `<p>${estado.passos}</p>`;
    html += `</div>`;
    
    // Detalhes por grupo
    estado.grupos.forEach(g => {
        const emoji = g.grupo === 1 ? '🌸' : g.grupo === 2 ? '💎' : '🌿';
        const vencedor = g.grupo === estado.grupo_vencedor;
        
        html += `<div class="grupo-stats ${vencedor ? 'vencedor' : ''}">`;
        html += `<h4>${emoji} Grupo ${g.grupo} ${vencedor ? '👑' : ''}</h4>`;
        html += `<p>Vivos: ${g.vivos}/${g.total}</p>`;
        html += `<p>Tesouros: ${g.tesouros}</p>`;
        html += `<p>Células: ${g.celulas_exploradas}</p>`;
        
        // ✅ Detalhes dos agentes
        if (g.agentes) {
            html += `<div class="agentes-detalhes">`;
            g.agentes.forEach(a => {
                const status = a.vivo ? '✅' : '💀';
                html += `<small>${status} Agente ${a.id}: ${a.tesouros}💎`;
                if (!a.vivo && a.posicao_morte) {
                    html += ` (morreu em ${a.posicao_morte[0]},${a.posicao_morte[1]})`;
                }
                html += `</small><br>`;
            });
            html += `</div>`;
        }
        
        html += `</div>`;
    });
    
    html += '</div>';
    
    conteudo.innerHTML = html;
    panel.style.display = 'block';
}

function mostrarMensagem(texto, tipo = 'info') {
    const div = document.getElementById('mensagem');
    div.textContent = texto;
    div.className = `mensagem ${tipo}`;
    div.style.display = 'block';
    
    setTimeout(() => {
        div.style.display = 'none';
    }, 5000);
}

function adicionarLog(texto) {
    const logs = document.getElementById('logs');
    const timestamp = new Date().toLocaleTimeString();
    const linha = document.createElement('div');
    linha.textContent = `[${timestamp}] ${texto}`;
    logs.appendChild(linha);
    logs.scrollTop = logs.scrollHeight;
}

function limparLogs() {
    document.getElementById('logs').innerHTML = '';
}

function setBombas(valor) {
    document.getElementById('percentagem-bombas').value = valor;
    document.getElementById('bombas-valor').textContent = `${valor}%`;
}

// Nova simulação
const btnNova = document.getElementById('btn-nova');
if (btnNova) {
    btnNova.addEventListener('click', () => {
        location.reload();
    });
}