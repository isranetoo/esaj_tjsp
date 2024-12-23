def coletar_informacoes(arquivo_entrada, campos, arquivo_saida):
    """
    Coleta as informações do processos_unificados.json e as filtra em outro arquivo JSON informacoes_processos_completo.json
    com o formato BD e valores nulos para campos ausentes.
    """
    try:
        with open(arquivo_entrada, 'r', encoding='utf-8') as f:
            dados = json.load(f).get("documents", [])

        informacoes = {}
        for doc in dados:
            numero_processo = doc.get("processo", "desconhecido")
            informacoes[numero_processo] = {
                "sistema": doc.get("sistema", "PJE"),
                "numero": doc.get("processo", None),
                "classe": doc.get("classeJudicialSigla", None),
                "current_instance": doc.get("instancia", None),
                "orgaoJulgador": doc.get("orgaoJulgador", None),
                "juizoDigital": doc.get("meioTramitacao", None),
                "segredoJustica": doc.get("sigiloso", None),
                "justicaGratuita": doc.get("justicaGratuita", None),
                "distribuidoEm": doc.get("dataDistribuicao", None),
                "autuadoEm": doc.get("dataPublicacao", None),
                "valorDaCausa": doc.get("valorCausa", None),
                "envolvidos": doc.get("envolvidos", [
                        {
                            "id_sistema": doc.get("id", None),
                            "nome": doc.get("poloAtivo", None),
                            "tipo": doc.get("reclamante", "RECLAMANTE"),
                            "polo": doc.get("polo", "ATIVO"),
                            "tipoDocumento": "",
                            "documento": "",
                            "endereco": {},
                            "representantes": [
                            {
                                "id_sistema": doc.get("id", None),
                                "nome": doc.get("nome_adv", None),
                                "tipo": doc.get("adv", None),
                                "polo": doc.get("polo", "ATIVO"),
                                "tipoDocumento": doc.get("cpf", None),
                                "documento": doc.get("num_cpf", None),
                                "endereco": {
                                    "logradouro": doc.get("longradouro", None),
                                    "numero": doc.get("numero", None),
                                    "complemento": doc.get("complemento", None),
                                    "bairro": doc.get("bairro", None),
                                    "municipio": doc.get("municipio", None),
                                    "estado": doc.get("estado", None),
                                    "cep": doc.get("cep", None),
                                }
                            }
                            ]
                        },
                        {
                            "id_sistema": doc.get("id", None),
                            "nome": doc.get("poloPassivo", None),
                            "tipo": doc.get("reclamado", "RECLAMADO"),
                            "polo": doc.get("polo", "PASSIVO"),
                            "tipoDocumento": "",
                            "documento": "",
                            "endereco": {},
                            "representantes": [
                            {
                                "id_sistema": doc.get("id", None),
                                "nome": doc.get("nome_adv", None),
                                "tipo": doc.get("adv", None),
                                "polo": doc.get("polo", "PASSIVO"),
                                "tipoDocumento": doc.get("cpf", None),
                                "documento": doc.get("num_cpf", None),
                                    "endereco": {
                                    "logradouro": doc.get("longradouro", None),
                                    "numero": doc.get("numero", None),
                                    "complemento": doc.get("complemento", None),
                                    "bairro": doc.get("bairro", None),
                                    "municipio": doc.get("municipio", None),
                                    "estado": doc.get("estado", None),
                                    "cep": doc.get("cep", None),
                                }
                            }
                            ]
                        },
                        {
                            "id_sistema": doc.get("id", None),
                            "nome": doc.get("nome_perito", None),
                            "tipo": doc.get("tipo_perito", None),
                            "polo": doc.get("polo", "OUTROS"),
                            "tipoDocumento": "",
                            "documento": "",
                            "endereco": {},
                            "representantes": []
                        }
                        ],),
                "assuntos": doc.get("assunto", []),
                "movimentacoes": doc.get("movimentacoes", [{
                    "titulo": doc.get("movimentoDecisao", None),
                    "tipoConteudo": doc.get("html", None),
                    "data": doc.get("dataPublicacao", None),
                    "ativo": doc.get("ativo", None),
                    "documento": doc.get("f_ou_t", None),
                    "mostrarHeaderData": doc.get("header_data", None),
                    "usuarioCriador": doc.get("usuarioCriador", None),
                },
                {
                    "titulo": doc.get("titulo", None),
                    "tipoConteudo": doc.get("html", None),
                    "data": doc.get("dataPublicacao", None),
                    "ativo": doc.get("ativo", None),
                    "documento": doc.get("f_ou_t", None),
                    "mostrarHeaderData": doc.get("header_data", None),
                    "usuarioCriador": doc.get("usuarioCriador", None),
                },
                {
                    "id": doc.get("id", None),
                    "idUnicoDocumento": doc.get("idUnicoDocumento", None),
                    "titulo": doc.get("titulo", None),
                    "tipo": doc.get("tipoDocumento", None),
                    "tipoConteudo": doc.get("tipoConteudo","RTF"),
                    "data": doc.get("dataPublicacao", None),
                    "ativo": doc.get("ativo", None),
                    "documentoSigiloso": doc.get("sigiloso", None),
                    "usuarioPerito": doc.get("usuarioPerito", None),
                    "documento": doc.get("tipo_doc", None),
                    "publico": doc.get("tipo_publico", None),
                    "usuarioJuntada": doc.get("usuarioJuntada", None),
                    "usuarioCriador": doc.get("usuarioCriador", None),
                    "instancia": doc.get("instancia", None)
                }
            ])
        }
        with open(arquivo_saida, 'w', encoding='utf-8') as f:
            json.dump(informacoes, f, ensure_ascii=False, indent=4)
        print(f"Informações salvas em: \033[32m{arquivo_saida}\033[0m")
    except Exception as e:
        print(f"Erro ao processar informações: {e}")