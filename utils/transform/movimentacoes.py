
import pandas as pd

from scrappers.utils.text import search_series_pattern


#### ------------------ EXTRACT FUNCTIONS ------------------
def extract_mov_data_trabalhista(movimentacoes: list[dict[str, str]]):

    # Creates mov filters, each filters add a column: tem, data
    mov_filters = {
        # Separação de fases
        "ex_inicio": (r"Iniciada a execu[cç][aâáàã]o", 'new', []),
        "tst_recurso_extra": (r"Recurso Extraordinario", 'new', []),
        "2da_recurso_revista": (r"Recurso de Revista", 'new', []),
        "1ra_recurso_ordinario": (r"Recurso Ordin[aâáàã]rio", 'new', []),

        # Conclusão
        "fim_desarquivado": (r"desarquivados os autos", 'new', []),
        "fim_arquivado": (r"Arquivados os autos definitivamente", 'new', []),
        "fim_extinto": (r"Extinta a execu[cç][âáàã]o|Extinto o cumprimento", 'new', []),
        "fim_suspenso_o_processo": (r"suspenso o processo", 'new', []),
        "fim_satisfacao_obrigacao": (r"satisfa[cç][aâáàã]o da obriga[cç][aâáàã]o", 'new', []),

        # Acordo
        "ac_decisao_homologatoria": (r"decis[aâáàã]o homologat[oóò]ria", 'new', []),
        "ac_transacao_homologada": (r"Transa[çc][aâáàã]o Homologada|Homologada a Transa[çc][aâáàã]o|homologa[çc][aâáàã]o de transa[çc][aâáàã]o", 'new', []),
        "ac_transacao": (r"Transa[çc][aâáàã]o", 'new', []),
        "ac_acordo_homologado": (r"Homologado o ac[oóò]rdo|homologa[çc][aâáàã]o de acordo", 'new', []),
        "ac_pet_acordo": (r"Juntada a peti[cç][aàãâá]o de Acordo", 'new', []),
        "ac_men_acordo": (r"Acordo$", 'new', []),

        # Execução
        "ex_perito": (r"perito", 'new', []),

        "ex_impugnacao": (r"impugna[cç][aâáàã]o", 'new', []),
        "ex_impugnacao_calculo": (r"impugna[cç][aâáàã]o ao c[aàãâá]lculo", 'new', []),

        "ex_embargo_execucao": (r"embargos [aâáàã] execu[cç][aâáàã]o", 'new', []),
        "ex_embargo_execucao_alterado": (r"alterado o tipo de Peti[cç][aâáàã]o de Embargos [aâáàã] execu[cç][aâáàã]o", 'old', [["after", ["ex_embargo_execucao"], 0, "fail"]]),
        "ex_sentenca_last": (r"^senten[cç]a$", 'new', [["after", ["ex_embargo_execucao"], 0, "fail"]]),
        "ex_sentenca_first": (r"^senten[cç]a$", 'old', [["after", ["ex_embargo_execucao"], 0, "fail"]]),

        "ex_calculo_homologado_last": (r"C[aàãâá]lculo Homologado|Homologada a Liquida[cç][aâáàã]o", 'new', []),
        "ex_calculo_decisão_last": (r"Decisão", 'new', [["near", ["ex_calculo_homologado_last"], 2, "fail"]]),

        "ex_calculo_homologado_first": (r"C[aàãâá]lculo Homologado|Homologada a Liquida[cç][aâáàã]o", 'old', []),
        "ex_calculo_decisão_first": (r"Decisão", 'old', [["near", ["ex_calculo_homologado_first"], 2, "fail"]]),

        "ex_liquidacao_inicio": (r"Iniciada a Liquida[cç][aâáàã]o", 'new', []),
        "ex_em_liquidacao": (r"Liquida[cç][aâáàã]o", 'new', []),
        "ex_pet_calculo": (r"Juntada a peti[cç][aàãâá]o de Apresenta[cç][aàãâá]o de C[aàãâá]lculos", 'new', []),
        "ex_calculo": (r"C[aàãâá]lculo", 'new', []),

        "ex_agravo_peticao": (r"Agravo de Peti[cç][aâáàã]o", 'new', []),

        "ex_em_execução": (r"execu[cç][aâáàã]o provis[oóò]ria|execu[cç][aâáàã]o ajuizada", 'new', []),

        # Pré Execução
        "pex_decisao_prevencao": (r"Decis[aàãâá]o de preven[cç][aàãâá]o", 'new', []),
        "pex_cumprimento_provisorio": (r"Cumprimento Provis[oóôò]rio", 'new', []),
        "pex_transito_em_julgado_last": (r"Tr[âa]nsit", 'new', []),
        "pex_transito_em_julgado_first": (r"Tr[âa]nsit", 'old', []),

        # TST
        "tst_pet_recurso_extra": (r"Juntada a peti[cç][aâáàã]o de Recurso Extraordinario", 'new', []),

        "tst_acordao_last": (r"^ac[oóò]rd[aâáàã]o$", 'new', [["after", ["2da_recurso_revista"], 0, "fail"], ["before", ["tst_recurso_extra"], 0, "skip"]]),
        "tst_acordao_first": (r"^ac[oóò]rd[aâáàã]o$", 'old', [["after", ["2da_recurso_revista"], 0, "fail"], ["before", ["tst_recurso_extra"], 0, "skip"]]),

        "tst_embargo_acordao": (r"embargo", 'old', [["after", ["tst_acordao_first"], 0, "fail"], ["before", ["tst_acordao_last"], 0, "skip"]]),
        "tst_pet_embargo_acordao": (r"Juntada a peti[cç][aâáàã]o de Embargos de Declara[cç][aâáàã]o|Juntada a petição de Manifesta[cç][aâáàã]o (Embargos de Declara[cç][aâáàã]o)", 'old', [["after", ["tst_acordao_first"], 0, "fail"], ["before", ["tst_acordao_last"], 0, "skip"]]),

        # 2da Instancia
        "2da_pet_recurso_revista": (r"Juntada a peti[cç][aâáàã]o de Recurso de Revista", 'new', []),

        "2da_agravo_rec_revista": (r"Agravo de instrumento", 'new', [['after', ['2da_recurso_revista'], 30, "fail"]]),

        "2da_acordao_last": (r"^ac[oóò]rd[aâáàã]o$", 'new', [["before", ["2da_recurso_revista"], 0, "skip"]]),
        "2da_acordao_first": (r"^ac[oóò]rd[aâáàã]o$", 'old', [["before", ["2da_recurso_revista"], 0, "skip"]]),

        "2da_embargo_acordao": (r"embargo", 'old', [["after", ["2da_acordao_first"], 0, "fail"], ["before", ["2da_acordao_last"], 0, "fail"]]),
        "2da_pet_embargo_acordao": (r"Juntada a peti[cç][aâáàã]o de Embargos de Declara[cç][aâáàã]o|Juntada a petição de Manifesta[cç][aâáàã]o (Embargos de Declara[cç][aâáàã]o)", 'old', [["after", ["2da_acordao_first"], 0, "fail"], ["before", ["2da_acordao_last"], 0, "skip"]]),

        # 1ra Instancia
        "1ra_pet_recurso_ordinario": (r"Juntada a peti[cç][aâáàã]o de Recurso Ordin[aâáàã]rio", 'new', []),

        "1ra_sentenca_last": (r"^senten[cç]a$", 'new', [["before", ["1ra_recurso_ordinario"], 0, "skip"]]),
        "1ra_sentenca_first": (r"^senten[cç]a$", 'old', [["before", ["1ra_recurso_ordinario"], 0, "skip"]]),

        "1ra_embargo_sentença": (r"embargo", 'old', [["after", ["1ra_sentenca_first"], 0, "fail"], ["before", ["1ra_sentenca_last"], 0, "skip"]]),
        "1ra_pet_embargo_sentença": (r"Juntada a peti[cç][aâáàã]o de Embargos de Declara[cç][aâáàã]o|Juntada a petição de Manifesta[cç][aâáàã]o (Embargos de Declara[cç][aâáàã]o)", 'old', [["after", ["1ra_sentenca_first"], 0, "fail"], ["before", ["1ra_sentenca_last"], 0, "skip"]]),

        "1ra_improcedente": (r"Julgado\(?s?\)? improcedente\(?s?\)? o\(?s?\)? pedido\(?s?\)?", 'old', [["near", ["1ra_sentenca_first"], 2, "fail"]]),
        "1ra_procedente": (r"Julgado\(?s?\)? procedente\(?s?\)? o\(?s?\)? pedido\(?s?\)?", 'old', [["near", ["1ra_sentenca_first"], 2, "fail"]]),
        "1ra_procedente_pt": (r"Julgado\(?s?\)? procedente\(?s?\)? em parte o\(?s?\)? pedido\(?s?\)?", 'old', [["near", ["1ra_sentenca_first"], 2, "fail"]]),

        "1ra_dispensadas_custas": (r"Arbitradas e dispensadas as custas processuais", 'old', [["near", ["1ra_sentenca_first"], 2, "fail"]]),
        "1ra_justiça_gratuita": (r"Concedida a assist[eéèê]ncia judici[aâáàã]ria gratuita", 'old', [["near", ["1ra_sentenca_first"], 2, "fail"]]),

        '1ra_conclusos_autos_sentença': (r"Conclusos os autos para julgamento Proferir sentença", 'old', [["before", ["1ra_sentenca_first"], 0, "skip"]]),
        "1ra_pet_contestacao": (r"juntada a peti[cç][aâáàã]o de contesta[cç][aâáàã]o", 'new', [["before", ["1ra_sentenca_first"], 0, "skip"]]),
    }

    movs_dados = pd.Series({mov["data"]: mov["titulo"]} for mov in movimentacoes)
    movs_dados.index = pd.to_datetime(movs_dados.index, format="%Y-%m-%dT%H:%M:%S")

    mov_results = {}
    for keyword, (search_pattern, method, rules) in mov_filters.items():
        this_mov_dados = movs_dados.copy(deep=True)

        failed_rule = False
        for (rule, targets, tol, missing) in rules:
            if isinstance(targets, str):
                raise ValueError(f"Wrong target for {keyword}: {rule} {targets} {tol}")

            # Check target
            rule_dates = []
            for target in targets:
                if f"data_{target}" in mov_results.keys():
                    if mov_results[f"data_{target}"]:
                        rule_dates.append(mov_results[f"data_{target}"])
                    elif missing == "fail":
                        failed_rule = True
                    else:
                        continue
                else:
                    raise ValueError(f"Cant apply rule {keyword}: {rule} {target} {tol}, target not calculated yet")

            if len(rule_dates) == 0:
                continue

            # Check rule and tolerance
            min_date, max_date = None, None
            if rule == "near":
                max_date = min(rule_dates) + pd.DateOffset(days=tol)
                min_date = max(rule_dates) - pd.DateOffset(days=tol)
            elif rule == "before":
                max_date = min(rule_dates) + pd.DateOffset(days=tol)
            elif rule == "after":
                min_date = max(rule_dates) - pd.DateOffset(days=tol)
            else:
                raise ValueError(f"Unkwon rule {rule}")

            # Apply rule
            this_mov_dados = this_mov_dados.loc[max_date:min_date]

        if failed_rule:
            mov_results[f"data_{keyword}"] = None
            continue

        if method == "new":
            mov_data, _ = search_series_pattern(this_mov_dados, search_pattern)
        elif method == "old":
            mov_data, _ = search_series_pattern(this_mov_dados[::-1], search_pattern)
        else:
            raise ValueError(f"Unkown mov search method: {method}")

        mov_results[f"data_{keyword}"] = mov_data

    return mov_results
