from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Servidor de base de datos
    database_url: str = "postgresql+psycopg://tp_user:tp_pass@localhost:5432/tp_evaluaciones"

    # Sesión
    jwt_secret: str = "cambiar-esto-en-produccion"
    jwt_expire_minutes: int = 60

    # Servidor LDAP de la organización
    auth_mode: str = "mock"  # "mock" | "ldap"
    mock_users: str = "CONSULTOR:consultor123"  # USUARIO:clave,USUARIO2:clave2
    ldap_server: str = "ldap://localhost:389"  # ldaps://host:636 en producción
    ldap_user_dn_template: str = "uid={username},ou=people,dc=capitalhumano,dc=com"

    # Sistemas externos
    ia_base_url: str = ""
    ia_api_key: str = ""
    sistema_candidatos_url: str = ""
    sistema_candidatos_api_key: str = ""
    impresora_uri: str = ""


settings = Settings()
