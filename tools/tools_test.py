from csv_tools import (
    autenticar_cliente,
    consultar_limite_conta,
    processar_solicitacao_credito,
)


def test_autenticacao_sucesso():
    print("\n" + "=" * 70)
    print("TESTE: Autenticação com dados válidos")
    print("=" * 70)

    cpf = "000.000.000-00"
    data_nascimento = "01/01/2001"

    print(f"\n[ENTRADA]")
    print(f"  CPF: {cpf}")
    print(f"  Data de nascimento: {data_nascimento}")

    resultado = autenticar_cliente.func(
        cpf=cpf,
        data_nascimento=data_nascimento,
    )

    print("\n[SAÍDA]")
    print(f"  {resultado}")

    assert "Autenticado com sucesso" in resultado
    assert "Anderson" in resultado

    print("\nRESULTADO: ✓ AUTENTICAÇÃO APROVADA")


def test_autenticacao_falha():
    print("\n" + "=" * 70)
    print("TESTE: Autenticação com dados inválidos")
    print("=" * 70)

    cpf = "000.000.000-00"
    data_nascimento = "01/01/2000"

    print(f"\n[ENTRADA]")
    print(f"  CPF: {cpf}")
    print(f"  Data de nascimento: {data_nascimento}")

    resultado = autenticar_cliente.func(
        cpf=cpf,
        data_nascimento=data_nascimento,
    )

    print("\n[SAÍDA]")
    print(f"  {resultado}")

    assert "Dados não conferem" in resultado

    print("\nRESULTADO: ✓ FALHA DE AUTENTICAÇÃO TRATADA CORRETAMENTE")


def test_consultar_limite_sucesso():
    print("\n" + "=" * 70)
    print("TESTE: Consulta de limite com CPF válido")
    print("=" * 70)

    cpf = "000.000.000-00"

    print(f"\n[ENTRADA]")
    print(f"  CPF: {cpf}")

    resultado = consultar_limite_conta.func(cpf=cpf)

    print("\n[SAÍDA]")
    print(f"  {resultado}")

    assert "O limite atual do cliente é R$" in resultado

    print("\nRESULTADO: ✓ CONSULTA DE LIMITE APROVADA")


def test_consultar_limite_falha_cpf():
    print("\n" + "=" * 70)
    print("TESTE: Consulta de limite com CPF inexistente")
    print("=" * 70)

    cpf = "000.000.000-51"

    print(f"\n[ENTRADA]")
    print(f"  CPF: {cpf}")

    resultado = consultar_limite_conta.func(cpf=cpf)

    print("\n[SAÍDA]")
    print(f"  {resultado}")

    assert "Erro: CPF não localizado" in resultado

    print("\nRESULTADO: ✓ CPF INEXISTENTE TRATADO CORRETAMENTE")


def test_processar_credito_valor_negativo():
    print("\n" + "=" * 70)
    print("TESTE: Solicitação de crédito com valor inválido")
    print("=" * 70)

    cpf = "377.986.848-24"
    limite_solicitado = -500.0

    print(f"\n[ENTRADA]")
    print(f"  CPF: {cpf}")
    print(f"  Limite solicitado: R$ {limite_solicitado:.2f}")

    resultado = processar_solicitacao_credito.func(
        cpf=cpf,
        limite_solicitado=limite_solicitado,
    )

    print("\n[SAÍDA]")
    print(f"  {resultado}")

    assert "Abortado: número negativo ou zerado" in resultado

    print("\nRESULTADO: ✓ VALOR INVÁLIDO BLOQUEADO")


def test_processar_credito_cpf_inexistente():
    print("\n" + "=" * 70)
    print("TESTE: Solicitação de crédito com CPF inexistente")
    print("=" * 70)

    cpf = "123.456.678.90"
    limite_solicitado = 5000.0

    print(f"\n[ENTRADA]")
    print(f"  CPF: {cpf}")
    print(f"  Limite solicitado: R$ {limite_solicitado:.2f}")

    resultado = processar_solicitacao_credito.func(
        cpf=cpf,
        limite_solicitado=limite_solicitado,
    )

    print("\n[SAÍDA]")
    print(f"  {resultado}")

    assert "Erro: CPF não localizado na base de clientes" in resultado

    print("\nRESULTADO: ✓ CPF INEXISTENTE TRATADO CORRETAMENTE")