# chaskiwasi-plugin-remaju 0.3.2

Plugin de dominio REMAJU para `chaskiwasi>=0.4.1,<0.5.0`.

## Responsabilidad del plugin

El plugin declara únicamente conocimiento específico de REMAJU:

- taxonomía;
- estrategias de clasificación;
- reglas de intención;
- campos de extracción;
- patrones candidatos;
- validaciones de dominio.

No implementa ChromaDB, multitenencia, retrieval, ventanas contextuales, cliente Gemini ni almacenamiento.
Esas responsabilidades pertenecen al core de Chaskiwasi 0.4.x.

## Campos declarados

- `demandantes`
- `demandados`
- `direccion`
- `requiere_cartel`

El core decide si cada campo se resuelve determinísticamente o necesita Gemini Structured Output.
El plugin solamente proporciona el resolver determinista, el esquema y el validador de dominio.
