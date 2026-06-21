"""
Estudo de Caso aplicado a Estatistica - Trabalho Final
Analise tecnica da base SoftTech Analytics (220 projetos).

Gera:
  - saidas/  -> tabelas em CSV (utf-8) + resumo de testes/ICs em TXT
  - figuras/ -> graficos PNG

Nivel de confianca: 95% | alpha = 0.05
"""

# ---------------------------------------------------------------------------
# IMPORTACOES
# ---------------------------------------------------------------------------
import os                     # criar pastas no sistema de arquivos
import warnings               # controlar/silenciar avisos
import numpy as np            # calculos numericos e arrays
import pandas as pd           # manipulacao de tabelas (DataFrames)
import scipy.stats as st      # testes estatisticos e distribuicoes
import matplotlib
matplotlib.use("Agg")         # backend "sem janela" (so salva arquivos); deve vir ANTES do pyplot
import matplotlib.pyplot as plt  # geracao de graficos

warnings.filterwarnings("ignore")  # ignora todos os avisos para manter a saida limpa

# ---------------------------------------------------------------------------
# CONSTANTES DE CONFIGURACAO
# ---------------------------------------------------------------------------
ARQ = "Dados_Brutos_estatistica_estudo_caso (1).xlsx"  # arquivo Excel de entrada
ALPHA = 0.05                       # nivel de significancia (5%)
CONF = 1 - ALPHA                   # nivel de confianca (95%)
Z = st.norm.ppf(1 - ALPHA / 2)     # valor critico Z da Normal padrao p/ IC 95% (~1.96)

os.makedirs("saidas", exist_ok=True)   # cria pasta de tabelas/resumo (nao falha se ja existir)
os.makedirs("figuras", exist_ok=True)  # cria pasta de graficos

# Ajustes globais dos graficos: resolucao, layout automatico e tamanho de fonte
plt.rcParams.update({"figure.dpi": 110, "figure.autolayout": True, "font.size": 10})

# Ordenacao logica para variaveis ordinais (evita ordem alfabetica nos graficos)
ORD_PORTE = ["Pequeno", "Médio", "Grande"]
ORD_COMPLEX = ["Baixa", "Média", "Alta", "Muito alta"]

# ---------------------------------------------------------------------------
# FUNCAO DE LOG: imprime na tela E acumula as linhas para salvar no resumo TXT
# ---------------------------------------------------------------------------
LOG = []
def log(*a):
    linha = " ".join(str(x) for x in a)  # junta os argumentos numa unica string
    print(linha)                          # mostra na tela
    LOG.append(linha)                     # guarda para o arquivo de resumo

# ----------------------------------------------------------------------
# Carga e limpeza de acentuacao (a planilha veio em cp1252)
# ----------------------------------------------------------------------
df = pd.read_excel(ARQ, sheet_name="Dados_Brutos")  # le a aba "Dados_Brutos" do Excel

def conserta(s):
    """Reconverte strings mal decodificadas para acentuacao correta quando possivel."""
    if isinstance(s, str):                          # so processa texto
        try:
            return s.encode("cp1252").decode("utf-8")  # recodifica e recupera os acentos
        except Exception:
            return s                                # se falhar, devolve o original
    return s                                        # nao-texto volta inalterado

for c in df.columns:                # percorre todas as colunas
    if df[c].dtype == object:       # aplica apenas nas colunas de texto
        df[c] = df[c].map(conserta)

# Variavel derivada: estouro de custo (real - estimado)
df["estouro_custo_mil"] = df["custo_real_mil"] - df["custo_estimado_mil"]      # valor absoluto
df["estouro_pct"] = 100 * df["estouro_custo_mil"] / df["custo_estimado_mil"]   # percentual sobre o estimado

log("=" * 70)
log("BASE:", df.shape[0], "observacoes |", df.shape[1], "variaveis")  # linhas x colunas
log("Faltantes totais:", int(df.isna().sum().sum()))                  # soma de todos os NaN
log("=" * 70)

# Listas de colunas por tipo: qualitativas (CAT) e quantitativas (NUM)
CAT = ["ano_conclusao", "setor_cliente", "metodologia", "equipe",
       "porte_projeto", "complexidade", "entregue_no_prazo"]
NUM = ["num_desenvolvedores", "experiencia_media_anos", "duracao_planejada_dias",
       "duracao_real_dias", "atraso_dias", "mudancas_requisitos", "horas_extras",
       "bugs_total", "bugs_criticos", "tempo_medio_correcao_horas",
       "retrabalho_horas", "custo_estimado_mil", "custo_real_mil",
       "satisfacao_cliente", "estouro_custo_mil", "estouro_pct"]

# ======================================================================
# 3.2 / 3.3 - DESCRITIVA
# ======================================================================
log("\n##### 3.2 / 3.3 - ESTATISTICA DESCRITIVA #####")

# Resumo das quantitativas: describe() da contagem/media/desvio/min/quartis/max (.T = transposto)
desc = df[NUM].describe().T
desc["mediana"] = df[NUM].median()                     # mediana (medida central robusta)
desc["assimetria"] = df[NUM].skew()                    # assimetria da distribuicao
desc["curtose"] = df[NUM].kurtosis()                   # achatamento/peso das caudas
desc["CV_%"] = 100 * df[NUM].std() / df[NUM].mean()    # coeficiente de variacao (dispersao relativa)
desc = desc[["count", "mean", "mediana", "std", "CV_%", "min", "25%", "50%",
             "75%", "max", "assimetria", "curtose"]].round(2)  # reordena colunas e arredonda
desc.to_csv("saidas/3_descritiva_quantitativas.csv", encoding="utf-8-sig")  # utf-8-sig p/ Excel ler acentos
log("\n-- Quantitativas (resumo):")
log(desc.to_string())

# Outliers por IQR (regra de Tukey: fora de [Q1-1.5*IQR ; Q3+1.5*IQR])
log("\n-- Outliers (regra 1.5*IQR):")
out_rows = []
for c in NUM:
    q1, q3 = df[c].quantile(0.25), df[c].quantile(0.75)   # 1o e 3o quartis
    iqr = q3 - q1                                          # intervalo interquartil
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr                # limites inferior e superior
    n_out = int(((df[c] < lo) | (df[c] > hi)).sum())       # conta valores fora dos limites
    out_rows.append([c, n_out, round(lo, 1), round(hi, 1)])
out_df = pd.DataFrame(out_rows, columns=["variavel", "n_outliers", "lim_inf", "lim_sup"])
out_df.to_csv("saidas/3_outliers_iqr.csv", index=False, encoding="utf-8-sig")
log(out_df.to_string(index=False))

# Frequencias das qualitativas (contagem e percentual de cada categoria)
log("\n-- Frequencias (qualitativas):")
freqs = {}
for c in CAT:
    t = df[c].value_counts(dropna=False)   # conta ocorrencias (inclui NaN)
    p = (100 * t / t.sum()).round(1)       # percentual de cada categoria
    tab = pd.DataFrame({"freq": t, "pct": p})
    freqs[c] = tab                         # guarda no dicionario
    tab.to_csv(f"saidas/2_freq_{c}.csv", encoding="utf-8-sig")  # um CSV por variavel
    log(f"\n[{c}]")
    log(tab.to_string())

# ---- Graficos descritivos
def barra(col, ordem=None, fname=None):
    """Gera grafico de barras de uma variavel categorica (com ordem opcional p/ ordinais)."""
    vc = df[col].value_counts()                              # contagem por categoria
    if ordem:
        vc = vc.reindex([o for o in ordem if o in vc.index])  # reordena conforme 'ordem'
    fig, ax = plt.subplots(figsize=(6, 3.6))
    ax.bar(vc.index.astype(str), vc.values, color="#3b6db5")  # desenha as barras
    ax.set_title(f"Distribuicao - {col}")
    ax.set_ylabel("Frequencia")
    for i, v in enumerate(vc.values):                         # rotulo com o valor em cima de cada barra
        ax.text(i, v, str(int(v)), ha="center", va="bottom", fontsize=8)
    plt.xticks(rotation=20)                                   # inclina os rotulos do eixo X
    fig.savefig(fname or f"figuras/barra_{col}.png")          # salva o PNG
    plt.close(fig)                                            # fecha a figura (libera memoria)

# Um grafico de barras para cada qualitativa (porte/complexidade usam a ordem definida)
barra("metodologia")
barra("setor_cliente")
barra("equipe")
barra("porte_projeto", ORD_PORTE)
barra("complexidade", ORD_COMPLEX)
barra("entregue_no_prazo")

# Histogramas de duas numericas, com linha vertical na media
for col in ["experiencia_media_anos", "num_desenvolvedores"]:
    fig, ax = plt.subplots(figsize=(6, 3.6))
    ax.hist(df[col], bins=15, color="#3b6db5", edgecolor="white")   # 15 classes
    ax.axvline(df[col].mean(), color="red", ls="--", label=f"media={df[col].mean():.2f}")
    ax.set_title(f"Histograma - {col}"); ax.legend()
    fig.savefig(f"figuras/hist_{col}.png"); plt.close(fig)

# Boxplots dos indicadores de desempenho (grade 2x3, um por indicador)
indic = ["atraso_dias", "horas_extras", "retrabalho_horas", "bugs_total",
         "custo_real_mil", "satisfacao_cliente"]
fig, axes = plt.subplots(2, 3, figsize=(11, 6))
for ax, c in zip(axes.flat, indic):
    ax.boxplot(df[c].dropna(), vert=True)   # mediana, quartis e outliers (sem NaN)
    ax.set_title(c, fontsize=9)
fig.suptitle("Boxplots - indicadores de desempenho")
fig.savefig("figuras/boxplots_desempenho.png"); plt.close(fig)

# ======================================================================
# 3.4 - RELACOES ENTRE VARIAVEIS
# ======================================================================
log("\n##### 3.4 - RELACOES ENTRE VARIAVEIS #####")

# Variaveis quantitativas usadas na analise de correlacao
quant_rel = ["experiencia_media_anos", "num_desenvolvedores", "complexidade_num",
             "atraso_dias", "horas_extras", "retrabalho_horas", "bugs_total",
             "bugs_criticos", "custo_real_mil", "satisfacao_cliente",
             "mudancas_requisitos"]
# Converte a complexidade (texto ordinal) em numero 1-4 para entrar nos calculos
df["complexidade_num"] = df["complexidade"].map(
    {"Baixa": 1, "Média": 2, "Alta": 3, "Muito alta": 4})

# Matriz de correlacao de Pearson (relacao LINEAR entre pares)
corr = df[quant_rel].corr(method="pearson").round(2)
corr.to_csv("saidas/4_matriz_correlacao_pearson.csv", encoding="utf-8-sig")
log("\n-- Matriz de correlacao (Pearson):")
log(corr.to_string())

# Heatmap (mapa de calor) da matriz de correlacao
fig, ax = plt.subplots(figsize=(8, 6.5))
im = ax.imshow(corr.values, cmap="RdBu_r", vmin=-1, vmax=1)   # cores de -1 (azul) a +1 (vermelho)
ax.set_xticks(range(len(corr))); ax.set_xticklabels(corr.columns, rotation=90, fontsize=7)
ax.set_yticks(range(len(corr))); ax.set_yticklabels(corr.columns, fontsize=7)
for i in range(len(corr)):                # escreve o valor numerico em cada celula
    for j in range(len(corr)):
        ax.text(j, i, f"{corr.values[i,j]:.2f}", ha="center", va="center",
                fontsize=6, color="black")
fig.colorbar(im, fraction=0.046)          # legenda de cores
ax.set_title("Matriz de correlacao (Pearson)")
fig.savefig("figuras/heatmap_correlacao.png"); plt.close(fig)

# Pares de interesse: Pearson (linear) + Spearman (por postos) + dispersao com reta
pares = [("experiencia_media_anos", "bugs_total"),
         ("complexidade_num", "atraso_dias"),
         ("retrabalho_horas", "satisfacao_cliente"),
         ("horas_extras", "atraso_dias"),
         ("custo_real_mil", "num_desenvolvedores")]
log("\n-- Correlacoes de interesse (Pearson r, p | Spearman rho, p):")
rel_rows = []
for x, y in pares:
    r, pr = st.pearsonr(df[x], df[y])     # correlacao linear + p-valor
    rho, ps = st.spearmanr(df[x], df[y])  # correlacao monotonica (postos) + p-valor
    rel_rows.append([f"{x} x {y}", round(r, 3), round(pr, 4), round(rho, 3), round(ps, 4)])
    log(f"  {x:24s} x {y:20s}  r={r:+.3f} (p={pr:.4f})  rho={rho:+.3f} (p={ps:.4f})")
    fig, ax = plt.subplots(figsize=(5, 3.6))
    ax.scatter(df[x], df[y], s=14, alpha=0.6, color="#3b6db5")  # grafico de dispersao
    b, a = np.polyfit(df[x], df[y], 1)                          # ajuste linear: b=inclinacao, a=intercepto
    xs = np.linspace(df[x].min(), df[x].max(), 50)              # pontos x da reta
    ax.plot(xs, a + b * xs, "r--", lw=1)                        # reta de regressao
    ax.set_xlabel(x); ax.set_ylabel(y)
    ax.set_title(f"r={r:+.2f}")
    fig.savefig(f"figuras/scatter_{x}__{y}.png"); plt.close(fig)
pd.DataFrame(rel_rows, columns=["par", "pearson_r", "p_pearson", "spearman_rho",
             "p_spearman"]).to_csv("saidas/4_correlacoes_interesse.csv",
             index=False, encoding="utf-8-sig")

# ======================================================================
# 3.5 - INTERVALOS DE CONFIANCA (95%)
# ======================================================================
log("\n##### 3.5 - INTERVALOS DE CONFIANCA (95%) #####")

# IC 1 - media da satisfacao (sigma desconhecido -> t de Student)
x = df["satisfacao_cliente"].dropna()
n = len(x); media = x.mean(); s = x.std(ddof=1)    # n, media e desvio amostral (ddof=1)
tc = st.t.ppf(1 - ALPHA / 2, df=n - 1)             # t critico com n-1 graus de liberdade
me = tc * s / np.sqrt(n)                           # margem de erro = t * erro-padrao
log(f"\n[IC1] Media de satisfacao_cliente (t-Student, gl={n-1})")
log(f"  media={media:.3f}  s={s:.3f}  n={n}  t_critico={tc:.3f}")
log(f"  IC95% = [{media-me:.3f} ; {media+me:.3f}]  (margem +/- {me:.3f})")

# IC 2 - proporcao de entregues no prazo (aproximacao Normal)
sucesso = (df["entregue_no_prazo"] == "Sim").sum()  # quantidade de "Sim"
n2 = len(df); p = sucesso / n2                       # proporcao amostral
me2 = Z * np.sqrt(p * (1 - p) / n2)                  # margem de erro pela Normal
log(f"\n[IC2] Proporcao entregue_no_prazo = 'Sim'")
log(f"  p_chapeu={p:.4f}  ({sucesso}/{n2})  Z={Z:.3f}")
log(f"  IC95% = [{p-me2:.4f} ; {p+me2:.4f}]  -> [{100*(p-me2):.1f}% ; {100*(p+me2):.1f}%]")

# IC extra - media do estouro de custo (bonus de apoio a 3.7); mesma logica do IC1
xe = df["estouro_custo_mil"].dropna()
ne = len(xe); me_e = xe.mean(); se = xe.std(ddof=1)
tce = st.t.ppf(1 - ALPHA / 2, df=ne - 1)
mee = tce * se / np.sqrt(ne)
log(f"\n[IC extra] Media do estouro de custo (mil R$)")
log(f"  media={me_e:.2f}  IC95% = [{me_e-mee:.2f} ; {me_e+mee:.2f}]")

# ======================================================================
# 3.6 - TESTES DE HIPOTESES (alpha = 0.05)
# ======================================================================
log("\n##### 3.6 - TESTES DE HIPOTESES (alpha=0.05) #####")

# Teste 1 - t pareado: custo_real > custo_estimado (mesmos projetos = amostras pareadas)
d = df["custo_real_mil"] - df["custo_estimado_mil"]                 # diferenca por projeto
t_stat, p_two = st.ttest_rel(df["custo_real_mil"], df["custo_estimado_mil"])  # p bilateral
p_uni = p_two / 2 if t_stat > 0 else 1 - p_two / 2                  # converte p para unilateral
log("\n[Teste 1] t pareado: custo real vs custo estimado")
log("  H0: mu_dif = 0   |   H1: mu_dif > 0 (custo real maior)")
log(f"  dif media = {d.mean():.2f} mil  | t = {t_stat:.3f}  | p(unilateral) = {p_uni:.2e}")
log(f"  Decisao: {'REJEITA H0' if p_uni < ALPHA else 'NAO rejeita H0'} -> "
    f"{'ha estouro sistematico de custo' if p_uni < ALPHA else 'sem evidencia de estouro'}")

# Teste 2 - qui-quadrado de independencia: metodologia x entregue_no_prazo
tab = pd.crosstab(df["metodologia"], df["entregue_no_prazo"])      # tabela de contingencia
chi2, p_chi, gl, esp = st.chi2_contingency(tab)                    # chi2, p, gl, frequencias esperadas
log("\n[Teste 2] Qui-quadrado: metodologia x entregue_no_prazo")
log("  H0: independentes  |  H1: associadas")
log("  Tabela observada:")
log(tab.to_string())
log(f"  chi2 = {chi2:.3f}  | gl = {gl}  | p = {p_chi:.4f}")
log(f"  Decisao: {'REJEITA H0 (ha associacao)' if p_chi < ALPHA else 'NAO rejeita H0 (sem associacao)'}")
tab.to_csv("saidas/6_tab_metodologia_prazo.csv", encoding="utf-8-sig")

# Teste extra - ANOVA de um fator: satisfacao entre metodologias
grupos = [g["satisfacao_cliente"].values for _, g in df.groupby("metodologia")]  # uma lista por grupo
F, p_anova = st.f_oneway(*grupos)                                 # teste F das medias
log("\n[Teste extra] ANOVA: satisfacao entre metodologias")
log("  H0: medias iguais  |  H1: ao menos uma difere")
log("  Medias por metodologia:")
log(df.groupby("metodologia")["satisfacao_cliente"].mean().round(3).to_string())
log(f"  F = {F:.3f}  | p = {p_anova:.4f}  -> "
    f"{'REJEITA H0' if p_anova < ALPHA else 'NAO rejeita H0'}")

# ======================================================================
# ENCERRAMENTO: grava todo o log acumulado no arquivo de resumo
# ======================================================================
with open("saidas/RESUMO_analise.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(LOG))

print("\n>>> Concluido. Veja a pasta 'saidas/' (tabelas+resumo) e 'figuras/' (graficos).")
