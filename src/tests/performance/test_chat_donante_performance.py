import time
import statistics
import sys
import os
import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# PERFORMANCE 1 – Carga (múltiples requests secuenciales)
# =====================================================
def test_performance_carga(client, monkeypatch):

    # ===================== ARRANGE =====================
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Ana", "donante": True}

    monkeypatch.setattr(app, "generate_response",
                        lambda *args, **kwargs: "ok")

    # ======================= ACT =======================
    start = time.time()

    for _ in range(50):  # 🔥 carga simulada
        resp = client.post(
            "/chatbot_donante",
            json={"mensaje_ingresado": "Hola"},
            content_type="application/json"
        )
        assert resp.status_code == 200

    end = time.time()

    # ====================== ASSERT =====================
    total_time = end - start
    assert total_time < 5  # ajustable según tu máquina


# =====================================================
# PERFORMANCE 2 – Estabilidad (muchas ejecuciones)
# =====================================================
def test_performance_estabilidad(client, monkeypatch):

    # ===================== ARRANGE =====================
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Ana", "donante": True}

    monkeypatch.setattr(app, "generate_response",
                        lambda *args, **kwargs: "ok")

    # ======================= ACT + ASSERT =======================
    for _ in range(30):
        resp = client.post(
            "/chatbot_donante",
            json={"mensaje_ingresado": "Hola"},
            content_type="application/json"
        )
        assert resp.status_code == 200


# =====================================================
# PERFORMANCE 3 – Tiempo promedio
# =====================================================
def test_performance_tiempo_promedio(client, monkeypatch):

    # ===================== ARRANGE =====================
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Ana", "donante": True}

    monkeypatch.setattr(app, "generate_response",
                        lambda *args, **kwargs: "ok")

    tiempos = []

    # ======================= ACT =======================
    for _ in range(20):
        start = time.time()

        resp = client.post(
            "/chatbot_donante",
            json={"mensaje_ingresado": "Hola"},
            content_type="application/json"
        )

        end = time.time()

        assert resp.status_code == 200
        tiempos.append(end - start)

    # ====================== ASSERT =====================
    promedio = statistics.mean(tiempos)
    assert promedio < 0.2  # tiempo promedio razonable


# =====================================================
# PERFORMANCE 4 – Pico de carga (ráfaga)
# =====================================================
def test_performance_pico_carga(client, monkeypatch):

    # ===================== ARRANGE =====================
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Ana", "donante": True}

    monkeypatch.setattr(app, "generate_response",
                        lambda *args, **kwargs: "ok")

    # ======================= ACT =======================
    respuestas = []

    for _ in range(40):  # ráfaga rápida
        resp = client.post(
            "/chatbot_donante",
            json={"mensaje_ingresado": "Hola"},
            content_type="application/json"
        )
        respuestas.append(resp.status_code)

    # ====================== ASSERT =====================
    assert all(r == 200 for r in respuestas)