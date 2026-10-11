"""
Paleta única do perfil, tirada da logo da Educação Tecnológica Paula Peclat.
Todos os geradores importam daqui, então trocar uma cor aqui troca no perfil inteiro.

Cada cor tem um papel fixo, pra quem olha aprender o código visual uma vez só:
  ROXO     marca, títulos de destaque e escalas (do claro ao escuro)
  AZUL     dado principal: linhas, áreas, mapas, a trilha
  ROSA     "você está aqui": o que está em andamento, a base, o progresso atual
  AMARELO  conquista e XP
  VERDE    concluído, tudo certo
O fundo é o preto da logo e o texto é o branco quente das letras de "Paula".
"""

ROXO = "#8D48E5"
ROXO_ESCURO = "#6C36D0"
AZUL = "#12A9DB"
AZUL_FORTE = "#188FEB"
ROSA = "#E14489"
ROSA_CLARO = "#F08DB8"
AMARELO = "#F6B50D"
LARANJA = "#E98504"
VERDE = "#80C733"
VERDE_AGUA = "#27C49C"

BRANCO = "#F2EFEA"
PRETO = "#000104"

# rampa sequencial em roxo, do claro (concreto) ao escuro (abstrato)
RAMPA_ROXO = ["#E4D3FA", "#CDB0F5", "#B48BF0", "#9E68EA", "#8D48E5", "#7A3AD4", "#6C36D0"]


def rgba(cor: str, alfa: float) -> str:
    cor = cor.lstrip("#")
    r, g, b = (int(cor[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alfa})"
