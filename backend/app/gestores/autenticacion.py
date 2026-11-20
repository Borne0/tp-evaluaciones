"""CU001 – Autenticar usuario.  (No figura aún en el diagrama de clases: conviene agregarlo.)"""
from sqlalchemy.orm import Session

from ..dao import ConsultorDAO, CuestionarioDAO
from ..entidades.models import Consultor, Cuestionario
from ..infraestructura.ldap_client import LdapClient
from .base import BaseGestor
from .excepciones import CredencialesInvalidas


class GestorAutenticacion(BaseGestor):
    def __init__(self, db: Session, ldap: LdapClient | None = None):
        super().__init__(db)
        self.consultor_dao = ConsultorDAO(db)
        self.cuestionario_dao = CuestionarioDAO(db)
        self.ldap = ldap or LdapClient()

    def autenticar_consultor(self, username: str, password: str) -> Consultor:
        username = username.strip().upper()
        if not self.ldap.autenticar(username, password):
            raise CredencialesInvalidas()
        consultor = self.consultor_dao.obtener_por_username(username)
        if consultor is None:  # válido en LDAP pero sin legajo en el sistema
            raise CredencialesInvalidas()
        return consultor

    def autenticar_candidato(self, tipo_documento: str, nro_documento: str, clave: str) -> Cuestionario:
        cuestionario = self.cuestionario_dao.obtener_por_clave(tipo_documento, nro_documento.strip().upper(), clave)
        if cuestionario is None:
            raise CredencialesInvalidas()
        return cuestionario
