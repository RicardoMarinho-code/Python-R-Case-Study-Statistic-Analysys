# Estudo de Caso aplicado à Estatística — SoftTech Analytics

Trabalho Final da disciplina de **Estatística** (Engenharia de Software — Universidade Católica
de Brasília, 2026). O projeto aplica técnicas de estatística descritiva e inferencial sobre uma
base de **220 projetos de desenvolvimento de software** da empresa fictícia *SoftTech
Analytics*, atuando como uma equipe de consultoria que avalia produtividade, qualidade, prazos,
custos e satisfação dos clientes.

## Objetivo

Analisar quais fatores estão associados ao desempenho dos projetos e gerar evidências
estatísticas que apoiem recomendações para a diretoria — com foco na **interpretação** dos
resultados, não apenas no cálculo.

## Estrutura do repositório

```
.
├── README.md                                  # este arquivo
├── analise.py                                 # script único que gera todas as saídas
├── Dados_Brutos_estatistica_estudo_caso (1).xlsx   # base de dados original (não editar)
├── Roteiro Trabalho Final - Estatistica.pdf   # enunciado do trabalho
├── sd                                         # formulário de referência (fórmulas da disciplina)
├── 3.1_conhecimento_da_base.md                # texto do relatório — seções 3.1 e 3.2
├── figuras/                                   # gráficos gerados (PNG)
└── saidas/                                    # tabelas (CSV) + RESUMO_analise.txt
```

## A base de dados

- **220 observações** (1 linha = 1 projeto concluído entre 2024 e 2025).
- **22 variáveis** + 2 derivadas (`estouro_custo_mil`, `estouro_pct`), criadas no script.
- **Sem valores faltantes.**
- A planilha contém ainda as abas `Dicionario` (descrição das variáveis) e `Categorias`.

A classificação completa das variáveis por natureza estatística está em
[3.1_conhecimento_da_base.md](3.1_conhecimento_da_base.md).

## Como executar

**Pré-requisitos:** Python 3.11+ com as bibliotecas:

```bash
pip install pandas numpy scipy matplotlib openpyxl
```

**Rodar a análise** (a partir da raiz do projeto):

```bash
python analise.py
```

O script lê o `.xlsx`, executa todas as análises e (re)gera as pastas `figuras/` e `saidas/`.
É reproduzível: rodar de novo sobrescreve as saídas com os mesmos resultados.

## O que o `analise.py` produz

| Etapa do roteiro | O que é gerado |
|------------------|----------------|
| **3.1 / 3.2** Descritiva | Tabelas de frequência (qualitativas), resumo estatístico (quantitativas), detecção de *outliers* por IQR, gráficos de barras, histogramas e boxplots |
| **3.4** Relações | Matriz de correlação (Pearson) + heatmap, correlações de interesse (Pearson e Spearman) e gráficos de dispersão |
| **3.5** Intervalos de confiança (95%) | IC para a média da satisfação (t-Student) e IC para a proporção de entregas no prazo |
| **3.6** Testes de hipóteses (α=0,05) | Teste t pareado (custo real × estimado), qui-quadrado (metodologia × prazo) e ANOVA (satisfação × metodologia) |

Todas as saídas de console também são salvas em `saidas/RESUMO_analise.txt`.

## Principais resultados

- **Apenas 19,5% dos projetos** são entregues no prazo (IC 95%: 14,3% – 24,8%).
- **Estouro de custo sistemático:** custo real supera o estimado em ~27% em média
  (teste t pareado, p ≈ 3×10⁻⁵⁸).
- **Metodologia influencia o cumprimento de prazo** (qui-quadrado, p = 0,0001): projetos Ágeis
  entregam no prazo com frequência muito maior que os Tradicionais.
- **Qualidade dirige a satisfação:** bugs (r = −0,87), retrabalho (r = −0,81) e horas extras
  (r = −0,81) são fortemente associados à queda da satisfação do cliente.
- A **experiência média da equipe** não apresentou associação relevante com a redução de
  defeitos (resultado contraintuitivo que merece discussão no relatório).

> **Importante:** muitas variáveis de desempenho (complexidade, bugs, retrabalho, custo, atraso)
> são fortemente correlacionadas entre si — provável fator latente de complexidade/porte. As
> correlações devem ser interpretadas com cautela, sem inferir causalidade direta.

## Parâmetros adotados

- Nível de confiança: **95%** · Nível de significância: **α = 0,05**.

## Status

| Seção | Análise técnica | Texto do relatório |
|-------|:---------------:|:------------------:|
| 3.1 Conhecimento da base | ✅ | ✅ |
| 3.2 Caracterização | ✅ | ✅ |
| 3.3 Indicadores de desempenho | ✅ | ✅ |
| 3.4 Relações entre variáveis | ✅ | ✅ |
| 3.5 Intervalos de confiança | ✅ | ✅ |
| 3.6 Testes de hipóteses | ✅ | ✅ |
| 3.7 Recomendações | ✅ | ✅ |

---

# Desenvolvimento das análises

> As seções 3.1 e 3.2 (conhecimento da base e caracterização) estão em
> [3.1_conhecimento_da_base.md](3.1_conhecimento_da_base.md). Abaixo seguem as seções 3.3 a 3.7,
> com discussão fundamentada em evidências estatísticas. Parâmetros: confiança 95%, α = 0,05.

## 3.3 — Análise dos indicadores de desempenho

> Figura: `figuras/boxplots_desempenho.png` · Tabelas: `saidas/3_descritiva_quantitativas.csv`,
> `saidas/3_outliers_iqr.csv`

Estatística descritiva das principais variáveis de desempenho (n = 220):

| Indicador | Média | Mediana | Desv. padrão | CV % | Mín | Máx | Assimetria | Outliers (IQR) |
|-----------|------:|--------:|-------------:|-----:|----:|----:|-----------:|---------------:|
| Duração planejada (dias) | 127,9 | 121,5 | 56,7 | 44,3 | 35 | 303 | +0,79 | 2 |
| Duração real (dias) | 145,5 | 136,0 | 70,7 | 48,6 | 28 | 381 | +0,81 | 4 |
| Atraso (dias) | 17,5 | 16,0 | 22,1 | **126,3** | −34 | 111 | +0,98 | 9 |
| Horas extras | 96,6 | 88,6 | 56,8 | 58,8 | 0 | 290,9 | +0,76 | 4 |
| Retrabalho (horas) | 162,0 | 160,0 | 83,9 | 51,8 | 0 | 421 | +0,36 | 1 |
| Bugs total | 30,8 | 29,0 | 17,4 | 56,5 | 0 | 86 | +0,39 | 1 |
| Bugs críticos | 4,8 | 4,0 | 4,0 | 84,2 | 0 | 17 | +0,89 | 5 |
| Custo estimado (mil R$) | 245,0 | 220,9 | 132,2 | 54,0 | 68,9 | 672,1 | +1,17 | 13 |
| Custo real (mil R$) | 309,8 | 280,2 | 162,2 | 52,4 | 68,3 | 784,9 | +0,99 | 12 |
| Satisfação cliente (0–10) | 6,3 | 6,4 | 1,8 | 28,6 | 1,1 | 9,4 | **−0,69** | 8 |

**Discussão.**

- **Prazos e atraso.** A duração real (média 145,5 dias) supera sistematicamente a planejada
  (127,9 dias). O **atraso médio é de 17,5 dias**, mas a variável tem **dispersão altíssima
  (CV = 126%)** e amplitude de −34 a +111 dias — ou seja, há projetos entregues antecipadamente
  e outros com atrasos severos. Os **9 outliers** acima de 64 dias são os casos que mais
  merecem atenção da diretoria.
- **Esforço e qualidade.** Horas extras (média 96,6 h) e retrabalho (162 h) são elevados e
  dispersos, sinalizando sobrecarga das equipes. Em média cada projeto acumula **~31 bugs**,
  dos quais **~5 críticos**.
- **Custos.** O custo real médio (309,8 mil) é **~26% maior que o estimado** (245,0 mil). Ambas
  as variáveis têm forte assimetria positiva (+1,17 e +0,99) e muitos outliers superiores
  (12–13), puxados pelos grandes projetos — comportamento típico de custo.
- **Satisfação.** É a única variável com **assimetria negativa (−0,69)**: a maioria dos clientes
  dá notas medianas-altas (mediana 6,4), mas existe uma cauda de **8 projetos com notas baixas**
  (até 1,1) que derruba a média. Esses casos insatisfatórios são prioritários para investigação.

**Padrão geral:** os indicadores "ruins" (atraso, horas extras, bugs, custo) têm forte dispersão
e caudas à direita, enquanto a satisfação tem cauda à esquerda. Isso sugere que **um subgrupo de
projetos problemáticos** concentra os piores resultados — hipótese reforçada pelas correlações
da seção 3.4.

## 3.4 — Investigação de relações entre variáveis

> Figuras: `figuras/heatmap_correlacao.png`, `figuras/scatter_*.png` ·
> Tabelas: `saidas/4_matriz_correlacao_pearson.csv`, `saidas/4_correlacoes_interesse.csv`

Para cada par usou-se o coeficiente de **Pearson** (relação linear) e, como verificação robusta,
**Spearman** (relação monótona). Abaixo, os pares sugeridos pelo roteiro:

| Relação investigada | Coeficiente | p-valor | Conclusão |
|---------------------|------------:|--------:|-----------|
| Experiência da equipe × bugs total | r = −0,12 | 0,065 | **Sem associação significativa** |
| Complexidade × atraso | r = +0,63 | < 0,0001 | Associação positiva forte |
| Retrabalho × satisfação | r = −0,81 | < 0,0001 | Associação negativa forte |
| Horas extras × atraso | r = +0,83 | < 0,0001 | Associação positiva forte |
| Bugs total × satisfação | r = −0,87 | < 0,0001 | Associação negativa muito forte |
| Custo real × nº desenvolvedores | r = +0,81 | < 0,0001 | Associação positiva forte |

Relações categórica × quantitativa (não-lineares, via comparação de grupos):

| Relação | Evidência | Resultado |
|---------|-----------|-----------|
| Horas extras × cumprimento de prazo | Média 49,8 h (no prazo) vs **107,9 h (atrasados)**; t = −9,39 | p < 0,0001 |
| Porte do projeto × custo final | Pequeno 172,8 → Médio 330,9 → **Grande 608,3** mil; ANOVA F = 504 | p < 0,0001 |
| Metodologia × desempenho | ver testes da seção 3.6 (prazo e satisfação) | significativo |

**Discussão.**

- **Experiência não reduz defeitos (contraintuitivo).** A correlação entre experiência da equipe
  e bugs é fraca e **não significativa** (r = −0,12; p = 0,065). Ao contrário do esperado, equipes
  mais experientes não entregam menos defeitos — o que sugere que a qualidade depende mais da
  **complexidade do projeto** do que da senioridade da equipe.
- **A complexidade é o motor dos problemas.** Complexidade se associa fortemente a atraso
  (r = 0,63), e os indicadores de esforço/qualidade caminham juntos: mais horas extras → mais
  atraso (r = 0,83); mais bugs e retrabalho → menos satisfação (r = −0,87 e −0,81).
- **Qualidade é o que o cliente sente.** A satisfação é governada principalmente por **bugs
  (r = −0,87)** e retrabalho — reduzir defeitos é o caminho mais direto para clientes satisfeitos.
- **Custo escala com porte e tamanho de equipe** (r = 0,81; ANOVA F = 504): projetos grandes
  custam, em média, **3,5× mais** que os pequenos.

> ⚠️ **Cautela com causalidade.** Quase todas as variáveis de desempenho são fortemente
> correlacionadas entre si, provavelmente por compartilharem um **fator latente de
> complexidade/porte**. As correlações indicam associação, não causa direta — a complexidade do
> projeto tende a ser a variável de fundo que move as demais.

## 3.5 — Intervalos de confiança (95%)

Foram construídos ICs para dois parâmetros de interesse direto da diretoria, mais um terceiro de
apoio às recomendações.

### IC 1 — Média da satisfação do cliente (t de Student, σ desconhecido)
Justificativa: a satisfação é o indicador-síntese da percepção do cliente. Como σ populacional é
desconhecido, usa-se a distribuição t com n−1 = 219 graus de liberdade.

- x̄ = 6,29 · s = 1,80 · n = 220 · t₍0,025;219₎ = 1,971 · margem = ± 0,24
- **IC 95% = [6,05 ; 6,53]**

*Interpretação:* com 95% de confiança, a satisfação média da carteira está entre **6,05 e 6,53**.
É um patamar apenas mediano (numa escala de 0 a 10) — há margem clara de melhoria.

### IC 2 — Proporção de projetos entregues no prazo
Justificativa: cumprimento de prazo é meta gerencial central. Estima-se a proporção populacional
de entregas pontuais.

- p̂ = 0,1955 (43/220) · Z₍0,025₎ = 1,96 · margem = ± 0,052
- **IC 95% = [14,3% ; 24,8%]**

*Interpretação:* com 95% de confiança, **no máximo cerca de 1 em 4 projetos** é entregue no
prazo. Mesmo no cenário mais otimista do intervalo, a taxa de pontualidade é baixa — um problema
estrutural, não pontual.

### IC 3 (apoio) — Média do estouro de custo
- x̄ = 64,81 mil R$ · **IC 95% = [59,1 ; 70,6] mil R$**

*Interpretação:* em média, cada projeto custa entre **59 e 71 mil reais a mais** que o estimado —
base quantitativa para a recomendação sobre revisão do processo de orçamentação.

## 3.6 — Testes de hipóteses (α = 0,05)

### Teste 1 — O custo real supera o estimado? (t pareado)
- **Objetivo:** verificar se há estouro sistemático de orçamento.
- **H₀:** μ_dif = 0 (custo real = estimado) · **H₁:** μ_dif > 0 (custo real maior).
- **Nível de significância:** α = 0,05 (teste unilateral à direita).
- **Resultado:** diferença média = 64,81 mil R$; t = 22,17; **p ≈ 3×10⁻⁵⁸**.
- **Decisão e interpretação:** rejeita-se H₀. Há **forte evidência de estouro sistemático de
  custo** — não é variação aleatória, mas um padrão. Em média os projetos custam ~27% acima do
  orçado, indicando falha na fase de estimativa.

### Teste 2 — A metodologia influencia a entrega no prazo? (qui-quadrado de independência)
- **Objetivo:** testar associação entre metodologia e cumprimento de prazo.
- **H₀:** metodologia e entrega no prazo são independentes · **H₁:** são associadas.
- **Nível de significância:** α = 0,05.
- **Tabela observada:**

  | Metodologia | Não | Sim | % no prazo |
  |-------------|----:|----:|-----------:|
  | Ágil | 67 | 30 | **30,9%** |
  | Híbrida | 39 | 9 | 18,8% |
  | Tradicional | 71 | 4 | **5,3%** |

- **Resultado:** χ² = 17,65; gl = 2; **p = 0,0001**.
- **Decisão e interpretação:** rejeita-se H₀. **A metodologia está associada ao cumprimento de
  prazo.** Projetos Ágeis entregam no prazo ~6× mais frequentemente que os Tradicionais
  (30,9% vs 5,3%) — evidência forte a favor da adoção de práticas ágeis.

### Teste 3 (extra) — A satisfação difere entre metodologias? (ANOVA)
- **Objetivo:** verificar se a satisfação média varia conforme a metodologia.
- **H₀:** médias iguais (μ_Ágil = μ_Híbrida = μ_Tradicional) · **H₁:** ao menos uma difere.
- **Nível de significância:** α = 0,05.
- **Resultado:** médias — Ágil 6,73 · Híbrida 6,28 · Tradicional 5,72; F = 6,98; **p = 0,0012**.
- **Decisão e interpretação:** rejeita-se H₀. A **satisfação difere entre metodologias**, sendo
  mais alta na Ágil e mais baixa na Tradicional — coerente com o resultado de prazo do Teste 2.

## 3.7 — Recomendações para a diretoria

Com base nas evidências estatísticas acima:

1. **Rever o processo de estimativa de custos.** O estouro é sistemático e significativo
   (Teste 1; IC de +59 a +71 mil R$/projeto). Recomenda-se incorporar margens de contingência
   calibradas por porte e complexidade e revisar premissas de orçamentação.
2. **Expandir o uso de metodologias ágeis.** Projetos Ágeis entregam no prazo ~6× mais que os
   Tradicionais (Teste 2) e têm maior satisfação (Teste 3). Migrar projetos Tradicionais para
   abordagens ágeis/híbridas tende a melhorar prazo e satisfação simultaneamente.
3. **Atacar a pontualidade como problema estrutural.** Apenas 14–25% dos projetos saem no prazo
   (IC da seção 3.5). Vale revisar o planejamento de prazos e a gestão de horas extras — que
   estão associadas a *mais* atraso (107,9 h nos atrasados vs 49,8 h nos pontuais), sinal de que
   horas extras são reação ao problema, não solução.
4. **Priorizar a redução de defeitos para elevar a satisfação.** Bugs e retrabalho são os
   maiores determinantes da insatisfação (r = −0,87 e −0,81). Investir em testes, revisão de
   código e qualidade tende a ter o maior retorno em satisfação do cliente.
5. **Gerenciar a complexidade com atenção redobrada.** A complexidade é o fator de fundo que
   eleva atraso, retrabalho e custo. Projetos de complexidade "Muito alta" (apenas 6,8% da base)
   devem receber alocação reforçada e acompanhamento próximo desde o início.

> **Ressalva metodológica:** as relações encontradas são associações estatísticas, não
> necessariamente causais. As recomendações apontam direções fundamentadas nos dados, que devem
> ser validadas com conhecimento de negócio antes de mudanças de larga escala.
