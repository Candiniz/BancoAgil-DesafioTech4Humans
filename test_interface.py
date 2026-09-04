from streamlit.testing.v1 import AppTest


def test_bloqueio_interface_apos_tres_falhas():
    print("\n" + "=" * 70)
    print("TESTE: Bloqueio da interface após 3 falhas de autenticação")
    print("=" * 70)

    # Inicializa o app
    at = AppTest.from_file("app.py").run()

    print("\n[1/4] Verificando estado inicial...")
    assert at.chat_input[0].disabled is False
    print("      ✓ Chat habilitado inicialmente")

    # Simula três falhas
    print("\n[2/4] Simulando 3 tentativas de autenticação...")
    at.session_state["tentativas_autenticacao"] = 3
    at.run()
    print("      ✓ Contador definido para 3")

    # Verifica bloqueio
    print("\n[3/4] Verificando bloqueio do chat...")
    assert at.chat_input[0].disabled is True
    print("      ✓ Chat desabilitado corretamente")

    # Verifica mensagem
    print("\n[4/4] Verificando mensagem de bloqueio...")
    mensagem = at.error[0].value

    assert "temporariamente bloqueado" in mensagem

    print(f"      ✓ Mensagem exibida: '{mensagem}'")

    print("\n" + "-" * 70)
    print("RESULTADO: ✓ TESTE APROVADO")
    print("-" * 70)