# -*- coding: utf-8 -*-
"""
Estudo de Caso aplicado a Estatistica - Trabalho Final
Analise tecnica da base SoftTech Analytics (220 projetos).

Gera:
  - saidas/  -> tabelas em CSV (utf-8) + resumo de testes/ICs em TXT
  - figuras/ -> graficos PNG

Nivel de confianca: 95% | alpha = 0.05
"""

import os
import warnings
import numpy as np
import pandas as pd
import scipy.stats as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")

ARQ = "Dados_Brutos_estatistica_estudo_caso (1).xlsx"
ALPHA = 0.05
CONF = 1 - ALPHA
Z = st.norm.ppf(1 - ALPHA / 2)  # 1.959963...

os.makedirs("saidas", exist_ok=True)
os.makedirs("figuras", exist_ok=True)

plt.rcParams.update({"figure.dpi": 110, "figure.autolayout": True, "font.size": 10})

# Ordenacao para variaveis ordinais
ORD_PORTE = ["Pequeno", "Médio", "Grande"]
ORD_COMPLEX = ["Baixa", "Média", "Alta", "Muito alta"]

LOG = []
def log(*a):
    linha = " ".join(str(x) for x in a)
    print(linha)
    LOG.append(linha)

# ----------------------------------------------------------------------
# Carga e limpeza de acentuacao (a planilha veio em cp1252)
# ----------------------------------------------------------------------
df = pd.read_excel(ARQ, sheet_name="Dados_Brutos")

def conserta(s):
    """Reconverte strings mal decodificadas para acentuacao correta quando possivel."""
    if isinstance(s, str):
        try:
            return s.encode("cp1252").decode("utf-8")
        except Exception:
            return s
    return s

for c in df.columns:
    if df[c].dtype == object:
        df[c] = df[c].map(conserta)

# Variavel derivada: estouro de custo (real - estimado)
df["estouro_custo_mil"] = df["custo_real_mil"] - df["custo_estimado_mil"]
df["estouro_pct"] = 100 * df["estouro_custo_mil"] / df["custo_estimado_mil"]

log("=" * 70)
log("BASE:", df.shape[0], "observacoes |", df.shape[1], "variaveis")
log("Faltantes totais:", int(df.isna().sum().sum()))
log("=" * 70)

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

desc = df[NUM].describe().T
desc["mediana"] = df[NUM].median()
desc["assimetria"] = df[NUM].skew()
desc["curtose"] = df[NUM].kurtosis()
desc["CV_%"] = 100 * df[NUM].std() / df[NUM].mean()
desc = desc[["count", "mean", "mediana", "std", "CV_%", "min", "25%", "50%",
             "75%", "max", "assimetria", "curtose"]].round(2)
desc.to_csv("saidas/3_descritiva_quantitativas.csv", encoding="utf-8-sig")
log("\n-- Quantitativas (resumo):")
log(desc.to_string())

# Outliers por IQR
log("\n-- Outliers (regra 1.5*IQR):")
out_rows = []
for c in NUM:
    q1, q3 = df[c].quantile(0.25), df[c].quantile(0.75)
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    n_out = int(((df[c] < lo) | (df[c] > hi)).sum())
    out_rows.append([c, n_out, round(lo, 1), round(hi, 1)])
out_df = pd.DataFrame(out_rows, columns=["variavel", "n_outliers", "lim_inf", "lim_sup"])
out_df.to_csv("saidas/3_outliers_iqr.csv", index=False, encoding="utf-8-sig")
log(out_df.to_string(index=False))

# Frequencias das qualitativas
log("\n-- Frequencias (qualitativas):")
freqs = {}
for c in CAT:
    t = df[c].value_counts(dropna=False)
    p = (100 * t / t.sum()).round(1)
    tab = pd.DataFrame({"freq": t, "pct": p})
    freqs[c] = tab
    tab.to_csv(f"saidas/2_freq_{c}.csv", encoding="utf-8-sig")
    log(f"\n[{c}]")
    log(tab.to_string())

# ---- Graficos descritivos
def barra(col, ordem=None, fname=None):
    vc = df[col].value_counts()
    if ordem:
        vc = vc.reindex([o for o in ordem if o in vc.index])
    fig, ax = plt.subplots(figsize=(6, 3.6))
    ax.bar(vc.index.astype(str), vc.values, color="#3b6db5")
    ax.set_title(f"Distribuicao - {col}")
    ax.set_ylabel("Frequencia")
    for i, v in enumerate(vc.values):
        ax.text(i, v, str(int(v)), ha="center", va="bottom", fontsize=8)
    plt.xticks(rotation=20)
    fig.savefig(fname or f"figuras/barra_{col}.png")
    plt.close(fig)

barra("metodologia")
barra("setor_cliente")
barra("equipe")
barra("porte_projeto", ORD_PORTE)
barra("complexidade", ORD_COMPLEX)
barra("entregue_no_prazo")

for col in ["experiencia_media_anos", "num_desenvolvedores"]:
    fig, ax = plt.subplots(figsize=(6, 3.6))
    ax.hist(df[col], bins=15, color="#3b6db5", edgecolor="white")
    ax.axvline(df[col].mean(), color="red", ls="--", label=f"media={df[col].mean():.2f}")
    ax.set_title(f"Histograma - {col}"); ax.legend()
    fig.savefig(f"figuras/hist_{col}.png"); plt.close(fig)

# Boxplots dos indicadores de desempenho (padronizados p/ visual comparavel)
indic = ["atraso_dias", "horas_extras", "retrabalho_horas", "bugs_total",
         "custo_real_mil", "satisfacao_cliente"]
fig, axes = plt.subplots(2, 3, figsize=(11, 6))
for ax, c in zip(axes.flat, indic):
    ax.boxplot(df[c].dropna(), vert=True)
    ax.set_title(c, fontsize=9)
fig.suptitle("Boxplots - indicadores de desempenho")
fig.savefig("figuras/boxplots_desempenho.png"); plt.close(fig)

# ======================================================================
# 3.4 - RELACOES ENTRE VARIAVEIS
# ======================================================================
log("\n##### 3.4 - RELACOES ENTRE VARIAVEIS #####")

quant_rel = ["experiencia_media_anos", "num_desenvolvedores", "complexidade_num",
             "atraso_dias", "horas_extras", "retrabalho_horas", "bugs_total",
             "bugs_criticos", "custo_real_mil", "satisfacao_cliente",
             "mudancas_requisitos"]
df["complexidade_num"] = df["complexidade"].map(
    {"Baixa": 1, "Média": 2, "Alta": 3, "Muito alta": 4})

corr = df[quant_rel].corr(method="pearson").round(2)
corr.to_csv("saidas/4_matriz_correlacao_pearson.csv", encoding="utf-8-sig")
log("\n-- Matriz de correlacao (Pearson):")
log(corr.to_string())

# Heatmap
fig, ax = plt.subplots(figsize=(8, 6.5))
im = ax.imshow(corr.values, cmap="RdBu_r", vmin=-1, vmax=1)
ax.set_xticks(range(len(corr))); ax.set_xticklabels(corr.columns, rotation=90, fontsize=7)
ax.set_yticks(range(len(corr))); ax.set_yticklabels(corr.columns, fontsize=7)
for i in range(len(corr)):
    for j in range(len(corr)):
        ax.text(j, i, f"{corr.values[i,j]:.2f}", ha="center", va="center",
                fontsize=6, color="black")
fig.colorbar(im, fraction=0.046)
ax.set_title("Matriz de correlacao (Pearson)")
fig.savefig("figuras/heatmap_correlacao.png"); plt.close(fig)

# Pares de interesse: Pearson + Spearman + scatter
pares = [("experiencia_media_anos", "bugs_total"),
         ("complexidade_num", "atraso_dias"),
         ("retrabalho_horas", "satisfacao_cliente"),
         ("horas_extras", "atraso_dias"),
         ("custo_real_mil", "num_desenvolvedores")]
log("\n-- Correlacoes de interesse (Pearson r, p | Spearman rho, p):")
rel_rows = []
for x, y in pares:
    r, pr = st.pearsonr(df[x], df[y])
    rho, ps = st.spearmanr(df[x], df[y])
    rel_rows.append([f"{x} x {y}", round(r, 3), round(pr, 4), round(rho, 3), round(ps, 4)])
    log(f"  {x:24s} x {y:20s}  r={r:+.3f} (p={pr:.4f})  rho={rho:+.3f} (p={ps:.4f})")
    fig, ax = plt.subplots(figsize=(5, 3.6))
    ax.scatter(df[x], df[y], s=14, alpha=0.6, color="#3b6db5")
    b, a = np.polyfit(df[x], df[y], 1)
    xs = np.linspace(df[x].min(), df[x].max(), 50)
    ax.plot(xs, a + b * xs, "r--", lw=1)
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
n = len(x); media = x.mean(); s = x.std(ddof=1)
tc = st.t.ppf(1 - ALPHA / 2, df=n - 1)
me = tc * s / np.sqrt(n)
log(f"\n[IC1] Media de satisfacao_cliente (t-Student, gl={n-1})")
log(f"  media={media:.3f}  s={s:.3f}  n={n}  t_critico={tc:.3f}")
log(f"  IC95% = [{media-me:.3f} ; {media+me:.3f}]  (margem +/- {me:.3f})")

# IC 2 - proporcao de entregues no prazo
sucesso = (df["entregue_no_prazo"] == "Sim").sum()
n2 = len(df); p = sucesso / n2
me2 = Z * np.sqrt(p * (1 - p) / n2)
log(f"\n[IC2] Proporcao entregue_no_prazo = 'Sim'")
log(f"  p_chapeu={p:.4f}  ({sucesso}/{n2})  Z={Z:.3f}")
log(f"  IC95% = [{p-me2:.4f} ; {p+me2:.4f}]  -> [{100*(p-me2):.1f}% ; {100*(p+me2):.1f}%]")

# IC extra - media do estouro de custo (bonus de apoio a 3.7)
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

# Teste 1 - t pareado: custo_real > custo_estimado
d = df["custo_real_mil"] - df["custo_estimado_mil"]
t_stat, p_two = st.ttest_rel(df["custo_real_mil"], df["custo_estimado_mil"])
p_uni = p_two / 2 if t_stat > 0 else 1 - p_two / 2
log("\n[Teste 1] t pareado: custo real vs custo estimado")
log("  H0: mu_dif = 0   |   H1: mu_dif > 0 (custo real maior)")
log(f"  dif media = {d.mean():.2f} mil  | t = {t_stat:.3f}  | p(unilateral) = {p_uni:.2e}")
log(f"  Decisao: {'REJEITA H0' if p_uni < ALPHA else 'NAO rejeita H0'} -> "
    f"{'ha estouro sistematico de custo' if p_uni < ALPHA else 'sem evidencia de estouro'}")

# Teste 2 - qui-quadrado: metodologia x entregue_no_prazo
tab = pd.crosstab(df["metodologia"], df["entregue_no_prazo"])
chi2, p_chi, gl, esp = st.chi2_contingency(tab)
log("\n[Teste 2] Qui-quadrado: metodologia x entregue_no_prazo")
log("  H0: independentes  |  H1: associadas")
log("  Tabela observada:")
log(tab.to_string())
log(f"  chi2 = {chi2:.3f}  | gl = {gl}  | p = {p_chi:.4f}")
log(f"  Decisao: {'REJEITA H0 (ha associacao)' if p_chi < ALPHA else 'NAO rejeita H0 (sem associacao)'}")
tab.to_csv("saidas/6_tab_metodologia_prazo.csv", encoding="utf-8-sig")

# Teste extra - ANOVA: satisfacao entre metodologias
grupos = [g["satisfacao_cliente"].values for _, g in df.groupby("metodologia")]
F, p_anova = st.f_oneway(*grupos)
log("\n[Teste extra] ANOVA: satisfacao entre metodologias")
log("  H0: medias iguais  |  H1: ao menos uma difere")
log("  Medias por metodologia:")
log(df.groupby("metodologia")["satisfacao_cliente"].mean().round(3).to_string())
log(f"  F = {F:.3f}  | p = {p_anova:.4f}  -> "
    f"{'REJEITA H0' if p_anova < ALPHA else 'NAO rejeita H0'}")

# ======================================================================
with open("saidas/RESUMO_analise.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(LOG))

print("\n>>> Concluido. Veja a pasta 'saidas/' (tabelas+resumo) e 'figuras/' (graficos).")
