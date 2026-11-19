"""Servidor LDAP de la organización (LDAP 389 / LDAPS 636)."""
import hmac

from ldap3 import Connection, Server
from ldap3.core.exceptions import LDAPException
from ldap3.utils.dn import escape_rdn

from ..config import settings


class LdapClient:
    def autenticar(self, username: str, password: str) -> bool:
        if not username or not password:  # un bind con clave vacía sería anónimo
            return False

        if settings.auth_mode == "mock":
            pares = (p.split(":", 1) for p in settings.mock_users.split(",") if ":" in p)
            esperada = {u.strip().upper(): c for u, c in pares}.get(username)
            return esperada is not None and hmac.compare_digest(esperada.encode(), password.encode())

        dn = settings.ldap_user_dn_template.format(username=escape_rdn(username))
        try:
            server = Server(settings.ldap_server, connect_timeout=5)  # ldaps:// activa TLS
            Connection(server, user=dn, password=password, auto_bind=True).unbind()
            return True
        except LDAPException:
            return False
