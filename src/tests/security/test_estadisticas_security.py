import pytest
import sys
import os
import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# SECURITY 1 – Estadísticas requiere rol ADMIN
# =====================================================
def test_security_estadisticas_solo_admin(client):
    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": False, "donante": True}
    
    resp = client.get("/estadisticas", follow_redirects=False)
    assert resp.status_code in (301, 302)

# =====================================================
# SECURITY 2 – Estadísticas sin sesión redirige
# =====================================================
def test_security_estadisticas_sin_sesion(client):
    resp = client.get("/estadisticas", follow_redirects=False)
    assert resp.status_code in (301, 302)
