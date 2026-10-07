# chaskiwasi-plugin-remaju

Plugin REMAJU para `chaskiwasi>=0.3.0,<0.4.0`.

La extracción sigue una estrategia de bajo consumo de tokens:

1. Regex/reglas deterministas localizan candidatos por chunk.
2. Se intenta resolver el dato sin IA.
3. Si el dato es ambiguo o incompleto, se construye una ventana contextual de chunks vecinos.
4. Gemini recibe únicamente esa ventana; nunca recibe el PDF completo como comportamiento normal.
5. La ventana se amplía progresivamente solo si el extractor lo requiere.

`gemini_rules.py` solo contiene configuración. La llamada real a Gemini está aislada en `semantic_extractor.py` y puede inyectarse en pruebas sin red.

## Instalación local

Desde el directorio del plugin, con Chaskiwasi 0.3.x instalado/editable:

```powershell
python -m pip install -e .
python -m pytest -q
```

Para habilitar Gemini:

```powershell
python -m pip install -e ".[gemini]"
$env:GEMINI_API_KEY="..."
```

El modelo puede sobrescribirse con `REMAJU_GEMINI_MODEL`. El valor por defecto procede de `gemini_rules.py`.
