// gerar_relatorio.js - Gera Relatório de Implementação em DOCX

const { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, Table, TableRow, TableCell, WidthType, BorderStyle } = require('docx');
const fs = require('fs');

// Criar documento
const doc = new Document({
    sections: [{
        properties: {},
        children: [
            // Título
            new Paragraph({
                text: "RELATÓRIO DE IMPLEMENTAÇÃO",
                heading: HeadingLevel.TITLE,
                alignment: AlignmentType.CENTER,
                spacing: { after: 400 }
            }),
            
            new Paragraph({
                text: "SISTEMA DE EXPLORAÇÃO COLABORATIVA COM AGENTES INTELIGENTES",
                heading: HeadingLevel.HEADING_1,
                alignment: AlignmentType.CENTER,
                spacing: { after: 600 }
            }),
            
            new Paragraph({
                children: [
                    new TextRun({
                        text: "Projeto de Inteligência Artificial\n",
                        bold: true
                    }),
                    new TextRun("Ano Letivo: 2024/2025 - 4º Ano\n"),
                    new TextRun("ISPTEC - Instituto Superior Politécnico de Tecnologias e Ciências")
                ],
                alignment: AlignmentType.CENTER,
                spacing: { after: 800 }
            }),
            
            // 1. INTRODUÇÃO
            new Paragraph({
                text: "1. INTRODUÇÃO",
                heading: HeadingLevel.HEADING_1,
                spacing: { before: 400, after: 200 }
            }),
            
            new Paragraph({
                text: "1.1 Contexto",
                heading: HeadingLevel.HEADING_2,
                spacing: { before: 200, after: 100 }
            }),
            
            new Paragraph({
                text: "Este projeto implementa um sistema multiagente para exploração colaborativa de ambientes desconhecidos. O sistema compara três grupos de agentes com diferentes estratégias de exploração, avaliando o impacto de algoritmos de aprendizagem de máquina no desempenho da exploração.",
                spacing: { after: 200 }
            }),
            
            new Paragraph({
                text: "O ambiente é representado por um tabuleiro 10×10 contendo células livres (L), bombas (B), tesouros (T) e, opcionalmente, uma bandeira (F). Os agentes devem explorar este ambiente colaborativamente, compartilhando conhecimento dentro do seu grupo para maximizar descobertas e minimizar perdas.",
                spacing: { after: 200 }
            }),
            
            new Paragraph({
                text: "1.2 Objetivos",
                heading: HeadingLevel.HEADING_2,
                spacing: { before: 200, after: 100 }
            }),
            
            new Paragraph({
                text: "Objetivos principais do projeto:",
                spacing: { after: 100 }
            }),
            
            new Paragraph({
                text: "• Implementar um sistema multiagente com comunicação e colaboração intra-grupo",
                spacing: { after: 50 },
                bullet: { level: 0 }
            }),
            
            new Paragraph({
                text: "• Integrar algoritmo de busca (BFS) com algoritmos de aprendizagem de máquina",
                spacing: { after: 50 },
                bullet: { level: 0 }
            }),
            
            new Paragraph({
                text: "• Comparar desempenho entre exploração pura (baseline) e exploração com aprendizagem",
                spacing: { after: 50 },
                bullet: { level: 0 }
            }),
            
            new Paragraph({
                text: "• Avaliar impacto da diversidade algorítmica em sistemas colaborativos",
                spacing: { after: 200 },
                bullet: { level: 0 }
            }),
            
            // 2. ARQUITETURA DO SISTEMA
            new Paragraph({
                text: "2. ARQUITETURA DO SISTEMA",
                heading: HeadingLevel.HEADING_1,
                spacing: { before: 400, after: 200 }
            }),
            
            new Paragraph({
                text: "2.1 Visão Geral",
                heading: HeadingLevel.HEADING_2,
                spacing: { before: 200, after: 100 }
            }),
            
            new Paragraph({
                text: "O sistema foi desenvolvido com arquitetura cliente-servidor:",
                spacing: { after: 100 }
            }),
            
            new Paragraph({
                text: "• Back-end: Servidor Python (Flask) com lógica de simulação e IA",
                spacing: { after: 50 },
                bullet: { level: 0 }
            }),
            
            new Paragraph({
                text: "• Front-end: Interface web (HTML + CSS + JavaScript) para configuração e visualização",
                spacing: { after: 200 },
                bullet: { level: 0 }
            }),
            
            new Paragraph({
                text: "2.2 Componentes do Back-End",
                heading: HeadingLevel.HEADING_2,
                spacing: { before: 200, after: 100 }
            }),
            
            new Paragraph({
                text: "servidor.py - API REST Flask",
                bold: true,
                spacing: { after: 50 }
            }),
            
            new Paragraph({
                text: "Servidor web que expõe endpoints para simular explorações. Gerencia carregamento de modelos treinados e coordena execução de simulações.",
                spacing: { after: 150 }
            }),
            
            new Paragraph({
                text: "tabuleiro.py - Ambiente de Exploração",
                bold: true,
                spacing: { after: 50 }
            }),
            
            new Paragraph({
                text: "Classe que representa o ambiente 10×10. Responsável por gerar tabuleiros aleatórios, verificar resolubilidade, rastrear células exploradas e gerenciar estado do ambiente.",
                spacing: { after: 150 }
            }),
            
            new Paragraph({
                text: "agente.py - Agente Explorador",
                bold: true,
                spacing: { after: 50 }
            }),
            
            new Paragraph({
                text: "Classe que representa cada agente individual. Gerencia posição, imunidades, células visitadas e decisão de próxima ação (com ou sem algoritmos de ML).",
                spacing: { after: 150 }
            }),
            
            new Paragraph({
                text: "grupo.py - Gerenciador de Grupos",
                bold: true,
                spacing: { after: 50 }
            }),
            
            new Paragraph({
                text: "Gerencia grupo de agentes e conhecimento compartilhado. Coordena comunicação entre agentes do mesmo grupo.",
                spacing: { after: 150 }
            }),
            
            new Paragraph({
                text: "simulador.py - Motor de Simulação",
                bold: true,
                spacing: { after: 50 }
            }),
            
            new Paragraph({
                text: "Coordena simulação completa. Cria ambiente e grupos, executa passos de exploração e verifica condições de término.",
                spacing: { after: 200 }
            }),
            
            // 3. ALGORITMOS IMPLEMENTADOS
            new Paragraph({
                text: "3. ALGORITMOS IMPLEMENTADOS",
                heading: HeadingLevel.HEADING_1,
                spacing: { before: 400, after: 200 }
            }),
            
            new Paragraph({
                text: "3.1 Busca em Largura (BFS)",
                heading: HeadingLevel.HEADING_2,
                spacing: { before: 200, after: 100 }
            }),
            
            new Paragraph({
                text: "Algoritmo de busca em grafos usado por todos os grupos. Identifica células candidatas para exploração de forma sistemática, garantindo exploração completa do espaço acessível.",
                spacing: { after: 150 }
            }),
            
            new Paragraph({
                text: "Características: Sistemático, completo, encontra caminho mais curto, comportamento previsível.",
                spacing: { after: 200 }
            }),
            
            new Paragraph({
                text: "3.2 SVM (Support Vector Machine)",
                heading: HeadingLevel.HEADING_2,
                spacing: { before: 200, after: 100 }
            }),
            
            new Paragraph({
                text: "Algoritmo de aprendizagem supervisionada que encontra hiperplano ótimo para separar classes.",
                spacing: { after: 100 }
            }),
            
            new Paragraph({
                text: "Configuração: Kernel RBF, C=1.0, normalização com StandardScaler.",
                spacing: { after: 150 }
            }),
            
            new Paragraph({
                text: "Vantagens: Eficaz em espaços de alta dimensão, robusto a overfitting.",
                spacing: { after: 200 }
            }),
            
            new Paragraph({
                text: "3.3 Árvore de Decisão",
                heading: HeadingLevel.HEADING_2,
                spacing: { before: 200, after: 100 }
            }),
            
            new Paragraph({
                text: "Algoritmo que cria regras de decisão hierárquicas através de particionamento recursivo do espaço de features.",
                spacing: { after: 100 }
            }),
            
            new Paragraph({
                text: "Configuração: Profundidade máxima 10, mínimo 5 amostras por folha.",
                spacing: { after: 150 }
            }),
            
            new Paragraph({
                text: "Vantagens: Alta interpretabilidade, não requer normalização, rápido.",
                spacing: { after: 200 }
            }),
            
            new Paragraph({
                text: "3.4 Perceptron (3 neurónios)",
                heading: HeadingLevel.HEADING_2,
                spacing: { before: 200, after: 100 }
            }),
            
            new Paragraph({
                text: "Rede neural de uma camada. Modelo mais simples de rede neural artificial.",
                spacing: { after: 100 }
            }),
            
            new Paragraph({
                text: "Arquitetura: 7 features de entrada → 3 neurónios de saída (classes).",
                spacing: { after: 150 }
            }),
            
            new Paragraph({
                text: "Vantagens: Simples, rápido, baixo custo computacional.",
                spacing: { after: 200 }
            }),
            
            new Paragraph({
                text: "3.5 MLP (Multilayer Perceptron - 3 neurónios)",
                heading: HeadingLevel.HEADING_2,
                spacing: { before: 200, after: 100 }
            }),
            
            new Paragraph({
                text: "Rede neural com camada oculta, capaz de aprender relações não lineares.",
                spacing: { after: 100 }
            }),
            
            new Paragraph({
                text: "Arquitetura: 7 entrada → 3 neurónios ocultos (ReLU) → 3 saída (Softmax).",
                spacing: { after: 150 }
            }),
            
            new Paragraph({
                text: "Vantagens: Maior capacidade de representação que Perceptron, aprende padrões complexos.",
                spacing: { after: 200 }
            }),
            
            // 4. FUNCIONALIDADES
            new Paragraph({
                text: "4. FUNCIONALIDADES PRINCIPAIS",
                heading: HeadingLevel.HEADING_1,
                spacing: { before: 400, after: 200 }
            }),
            
            new Paragraph({
                text: "4.1 Três Abordagens de Sucesso",
                heading: HeadingLevel.HEADING_2,
                spacing: { before: 200, after: 100 }
            }),
            
            new Paragraph({
                text: "Abordagem A: Sucesso se mais de 50% dos tesouros forem descobertos.",
                spacing: { after: 100 }
            }),
            
            new Paragraph({
                text: "Abordagem B: Sucesso se ambiente completamente explorado E pelo menos 1 agente sobreviver.",
                spacing: { after: 100 }
            }),
            
            new Paragraph({
                text: "Abordagem C: Sucesso se pelo menos 1 agente encontrar a bandeira.",
                spacing: { after: 200 }
            }),
            
            new Paragraph({
                text: "4.2 Sistema de Imunidades",
                heading: HeadingLevel.HEADING_2,
                spacing: { before: 200, after: 100 }
            }),
            
            new Paragraph({
                text: "Cada tesouro encontrado concede 1 imunidade ao agente. Quando agente com imunidade aciona bomba, a bomba é desativada (para todo o grupo) e agente sobrevive. Sem imunidade, agente morre ao acionar bomba.",
                spacing: { after: 200 }
            }),
            
            new Paragraph({
                text: "4.3 Conhecimento Compartilhado",
                heading: HeadingLevel.HEADING_2,
                spacing: { before: 200, after: 100 }
            }),
            
            new Paragraph({
                text: "Agentes do mesmo grupo compartilham instantaneamente todas as descobertas: posições de bombas, tesouros, células livres e bandeira. Esta comunicação permite coordenação eficiente e evita exploração redundante.",
                spacing: { after: 200 }
            }),
            
            new Paragraph({
                text: "4.4 Validação de Configuração",
                heading: HeadingLevel.HEADING_2,
                spacing: { before: 200, after: 100 }
            }),
            
            new Paragraph({
                text: "REGRA CRÍTICA: Grupo 2 e Grupo 3 devem ter combinações DIFERENTES de algoritmos de aprendizagem. Esta restrição é validada no front-end e back-end antes de iniciar simulação.",
                spacing: { after: 200 }
            }),
            
            // 5. INTERFACE WEB
            new Paragraph({
                text: "5. INTERFACE WEB",
                heading: HeadingLevel.HEADING_1,
                spacing: { before: 400, after: 200 }
            }),
            
            new Paragraph({
                text: "Interface intuitiva desenvolvida em HTML5, CSS3 e JavaScript puro (sem frameworks).",
                spacing: { after: 150 }
            }),
            
            new Paragraph({
                text: "Painéis principais:",
                spacing: { after: 100 }
            }),
            
            new Paragraph({
                text: "• Configuração: Seleção de abordagem, número de agentes, percentagem de bombas e algoritmos",
                spacing: { after: 50 },
                bullet: { level: 0 }
            }),
            
            new Paragraph({
                text: "• Visualização: Tabuleiro 10×10 renderizado dinamicamente, status da simulação",
                spacing: { after: 50 },
                bullet: { level: 0 }
            }),
            
            new Paragraph({
                text: "• Métricas: Agentes vivos, tesouros encontrados e células exploradas por grupo",
                spacing: { after: 50 },
                bullet: { level: 0 }
            }),
            
            new Paragraph({
                text: "• Resultados: Painel com estatísticas finais (tempo, passos, razão de término)",
                spacing: { after: 200 },
                bullet: { level: 0 }
            }),
            
            // 6. INSTRUÇÕES DE USO
            new Paragraph({
                text: "6. INSTRUÇÕES DE USO",
                heading: HeadingLevel.HEADING_1,
                spacing: { before: 400, after: 200 }
            }),
            
            new Paragraph({
                text: "6.1 Instalação",
                heading: HeadingLevel.HEADING_2,
                spacing: { before: 200, after: 100 }
            }),
            
            new Paragraph({
                text: "1. Instalar dependências Python:",
                spacing: { after: 50 }
            }),
            
            new Paragraph({
                text: "cd backend",
                spacing: { after: 50 },
                style: "code"
            }),
            
            new Paragraph({
                text: "pip install -r requisitos.txt",
                spacing: { after: 150 },
                style: "code"
            }),
            
            new Paragraph({
                text: "2. Treinar modelos de ML (OBRIGATÓRIO):",
                spacing: { after: 50 }
            }),
            
            new Paragraph({
                text: "python treinar_modelos.py",
                spacing: { after: 200 },
                style: "code"
            }),
            
            new Paragraph({
                text: "6.2 Execução",
                heading: HeadingLevel.HEADING_2,
                spacing: { before: 200, after: 100 }
            }),
            
            new Paragraph({
                text: "1. Iniciar servidor:",
                spacing: { after: 50 }
            }),
            
            new Paragraph({
                text: "python servidor.py",
                spacing: { after: 150 },
                style: "code"
            }),
            
            new Paragraph({
                text: "2. Abrir interface.html no navegador",
                spacing: { after: 150 }
            }),
            
            new Paragraph({
                text: "3. Configurar simulação e clicar em 'Iniciar Simulação'",
                spacing: { after: 200 }
            }),
            
            // 7. MÉTRICAS CAPTURADAS
            new Paragraph({
                text: "7. MÉTRICAS CAPTURADAS",
                heading: HeadingLevel.HEADING_1,
                spacing: { before: 400, after: 200 }
            }),
            
            new Paragraph({
                text: "Para cada simulação:",
                spacing: { after: 100 }
            }),
            
            new Paragraph({
                text: "• Tempo de execução (segundos)",
                spacing: { after: 50 },
                bullet: { level: 0 }
            }),
            
            new Paragraph({
                text: "• Número de passos executados",
                spacing: { after: 50 },
                bullet: { level: 0 }
            }),
            
            new Paragraph({
                text: "• Sucesso/Falha da missão",
                spacing: { after: 50 },
                bullet: { level: 0 }
            }),
            
            new Paragraph({
                text: "• Agentes vivos por grupo",
                spacing: { after: 50 },
                bullet: { level: 0 }
            }),
            
            new Paragraph({
                text: "• Tesouros encontrados por grupo",
                spacing: { after: 50 },
                bullet: { level: 0 }
            }),
            
            new Paragraph({
                text: "• Células exploradas por grupo",
                spacing: { after: 200 },
                bullet: { level: 0 }
            }),
            
            // 8. ESPAÇOS RESERVADOS
            new Paragraph({
                text: "8. RESULTADOS E ANÁLISE",
                heading: HeadingLevel.HEADING_1,
                spacing: { before: 400, after: 200 }
            }),
            
            new Paragraph({
                text: "[ESPAÇO RESERVADO PARA ANÁLISE]",
                bold: true,
                spacing: { after: 150 }
            }),
            
            new Paragraph({
                text: "Complete esta secção com:",
                spacing: { after: 100 }
            }),
            
            new Paragraph({
                text: "• Dados de pelo menos 30 execuções por abordagem",
                spacing: { after: 50 },
                bullet: { level: 0 }
            }),
            
            new Paragraph({
                text: "• Tabelas comparativas de desempenho",
                spacing: { after: 50 },
                bullet: { level: 0 }
            }),
            
            new Paragraph({
                text: "• Gráficos (histogramas de tempo, taxas de sucesso)",
                spacing: { after: 50 },
                bullet: { level: 0 }
            }),
            
            new Paragraph({
                text: "• Análise estatística (média, desvio padrão, testes de significância)",
                spacing: { after: 50 },
                bullet: { level: 0 }
            }),
            
            new Paragraph({
                text: "• Discussão crítica dos resultados",
                spacing: { after: 50 },
                bullet: { level: 0 }
            }),
            
            new Paragraph({
                text: "• Conclusões fundamentadas",
                spacing: { after: 200 },
                bullet: { level: 0 }
            }),
            
            // 9. CONCLUSÃO
            new Paragraph({
                text: "9. CONCLUSÃO",
                heading: HeadingLevel.HEADING_1,
                spacing: { before: 400, after: 200 }
            }),
            
            new Paragraph({
                text: "Este projeto implementou com sucesso um sistema multiagente para exploração colaborativa de ambientes. O sistema permite comparação rigorosa entre exploração pura (BFS) e exploração com aprendizagem de máquina (SVM, Árvore, Perceptron, MLP).",
                spacing: { after: 150 }
            }),
            
            new Paragraph({
                text: "A arquitetura modular facilita extensões futuras e adição de novos algoritmos. A interface web intuitiva permite configuração fácil e visualização clara dos resultados.",
                spacing: { after: 150 }
            }),
            
            new Paragraph({
                text: "Os resultados experimentais (a serem preenchidos na secção 8) permitirão avaliar quantitativamente o impacto da aprendizagem de máquina no desempenho de agentes exploradores.",
                spacing: { after: 400 }
            }),
            
            // AUTORES
            new Paragraph({
                text: "AUTORES",
                heading: HeadingLevel.HEADING_1,
                spacing: { before: 400, after: 200 }
            }),
            
            new Paragraph({
                text: "Grupo: [INSERIR NÚMERO DO GRUPO]",
                spacing: { after: 100 }
            }),
            
            new Paragraph({
                text: "Integrantes:",
                spacing: { after: 50 }
            }),
            
            new Paragraph({
                text: "• [Nome Completo 1]",
                spacing: { after: 50 },
                bullet: { level: 0 }
            }),
            
            new Paragraph({
                text: "• [Nome Completo 2]",
                spacing: { after: 50 },
                bullet: { level: 0 }
            }),
            
            new Paragraph({
                text: "• [Nome Completo 3]",
                spacing: { after: 200 },
                bullet: { level: 0 }
            }),
            
            new Paragraph({
                text: "Professor: Bongo Cahisso",
                spacing: { after: 50 }
            }),
            
            new Paragraph({
                text: "Disciplina: Inteligência Artificial",
                spacing: { after: 50 }
            }),
            
            new Paragraph({
                text: "Ano Letivo: 2024/2025",
                spacing: { after: 50 }
            }),
            
            new Paragraph({
                text: "ISPTEC - Instituto Superior Politécnico de Tecnologias e Ciências",
                spacing: { after: 200 }
            })
        ]
    }]
});

// Salvar documento
Packer.toBuffer(doc).then(buffer => {
    fs.writeFileSync("/home/claude/projeto_agentes_ia/RELATORIO_IMPLEMENTACAO.docx", buffer);
    console.log("✓ Relatório gerado: RELATORIO_IMPLEMENTACAO.docx");
});
