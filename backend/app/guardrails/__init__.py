import re

# Padrões comuns de prompt injection
_PADROES_INJECAO = re.compile(
    r"ignore\s.{0,20}(previous|all|above|your)\s+instructions"
    r"|system\s+prompt"
    r"|you\s+are\s+now\s+(a|an|the)\s"
    r"|jailbreak"
    r"|pretend\s+(you\s+are|to\s+be)"
    r"|DAN\s+mode"
    r"|ignore\s+as\s+instru[çc]"
    r"|nova\s+persona",
    flags=re.IGNORECASE,
)

# cliente_id: apenas alfanumérico, hífen e underscore, 1-64 chars
_CLIENTE_ID_RE = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")


def detectar_injecao_prompt(texto: str) -> bool:
    """Retorna True se o texto contém padrões suspeitos de prompt injection."""
    return bool(_PADROES_INJECAO.search(texto))


def validar_cliente_id(cliente_id: str) -> bool:
    """Garante que cliente_id só contém caracteres seguros para Redis e SQL."""
    return bool(_CLIENTE_ID_RE.match(cliente_id))
