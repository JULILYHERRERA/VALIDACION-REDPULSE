import os
import sys
import pytest
from flask import url_for

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

# ahora sí podemos importar app desde src/app.py
from app import app

# ---------------- fixtures ----------------
@pytest.fixture
def client():
    # configuración de testing
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'

    with app.test_client() as client:
        with app.app_context():
            yield client


# ---------------- tests ----------------

def test_get_redirect_if_user_logged_in(client):
    # Simula que ya hay datos de usuario en sesión -> redirección a 'home'
    with client.session_transaction() as sess:
        sess['user_data'] = {'id': 1, 'email': 'u@example.com'}

    resp = client.get('/restablecer_contrasena', follow_redirects=False)
    assert resp.status_code in (301, 302)

    with app.test_request_context():
        expected = url_for('home', _external=False)

    assert resp.headers.get('Location', '').endswith(expected)


def test_post_invalid_code_or_passwords_sets_flag_false(client):
    # Caso: el código ingresado no coincide -> debe setear cambio_contrasena_exitoso = False
    with client.session_transaction() as sess:
        sess['correo_recuperacion'] = '123456'  # código real esperado
        sess['correo_recuperacion_asociado'] = 'user@example.com'

    data = {
        'codigo_recuperacion': 'wrong-code',
        'nueva_contrasena': 'newpass123',
        'confirmacion_nueva_contrasena': 'newpass123'
    }
    resp = client.post('/restablecer_contrasena', data=data, follow_redirects=True)
    assert resp.status_code == 200  # renderiza template de nuevo

    with client.session_transaction() as sess:
        assert sess.get('cambio_contrasena_exitoso') is False


def test_post_success_calls_update_and_clears_session(monkeypatch, client):
    # Parcheamos la función actualizarContrasena que está en src/app.py
    called = {}
    def fake_actualizarContrasena(correo, nueva):
        called['correo'] = correo
        called['nueva'] = nueva

    # parche sobre el objeto app importado
    monkeypatch.setattr(app, 'actualizarContrasena', fake_actualizarContrasena)

    with client.session_transaction() as sess:
        sess['correo_recuperacion'] = 'ABC123'
        sess['correo_recuperacion_asociado'] = 'victim@example.com'

    data = {
        'codigo_recuperacion': 'ABC123',
        'nueva_contrasena': 's3gura!',
        'confirmacion_nueva_contrasena': 's3gura!'
    }
    resp = client.post('/restablecer_contrasena', data=data, follow_redirects=True)
    assert resp.status_code == 200

    # verificar que actualizarContrasena fue llamada con lo esperado
    assert called.get('correo') == 'victim@example.com'
    assert called.get('nueva') == 's3gura!'

    # verificar limpieza de sesión
    with client.session_transaction() as sess:
        assert sess.get('cambio_contrasena_exitoso') is True
        assert sess.get('correo_recuperacion') is None
        assert sess.get('correo_recuperacion_asociado') is None
        assert sess.get('correo_valido_resultado') is None


def test_post_success_should_fail_example(client):
    """
    Test diseñado para FALLAR intencionalmente:
    simula éxito pero asume que el flag debe ser False.
    """
    with client.session_transaction() as sess:
        sess['correo_recuperacion'] = 'ABC123'
        sess['correo_recuperacion_asociado'] = 'user@example.com'

    data = {
        'codigo_recuperacion': 'ABC123',
        'nueva_contrasena': 'pass',
        'confirmacion_nueva_contrasena': 'pass'
    }

    client.post('/restablecer_contrasena', data=data, follow_redirects=True)

    with client.session_transaction() as sess:
        # debería ser True (éxito), pero comprobamos False para que falle
        assert sess.get('cambio_contrasena_exitoso') is False