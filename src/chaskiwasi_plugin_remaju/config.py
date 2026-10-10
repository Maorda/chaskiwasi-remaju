import re
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# [CORRECCIÓN CRÍTICA]: Importar desde el paquete núcleo (chaskiwasi)
from chaskiwasi.contract import BaseExtractionConfig


class Remates_Judiciales_Schema(BaseModel):
    numero_expediente: Optional[str] = Field(
        default=None,
        description="Número de expediente judicial completo (ej: 00157-2014-0-2406-JM-CI-01)."
    )
    demandantes: List[str] = Field(
        default_factory=list,
        description="Lista con los nombres de las personas o empresas demandantes."
    )
    demandados: List[str] = Field(
        default_factory=list,
        description="Lista con los nombres de las personas o empresas demandadas."
    )
    direccion: Optional[str] = Field(
        default=None,
        description="Dirección completa del inmueble descrita."
    )
    requiere_cartel: bool = Field(
        default=False,
        description="True si ordena el pegado de carteles físicos. False si no."
    )


class Remates_Judiciales(BaseExtractionConfig):
    
    @property
    def model_class(self):
        return Remates_Judiciales_Schema
        
    @property
    def model_name(self) -> str:
        # Actualizado al modelo real de Gemini para tareas rápidas de extracción
        return "gemini-3.5-flash-lite"

    @property
    def palabras_clave(self) -> List[str]:
        return [
            "expediente", "demandante", "demandado", "juez", "resolución", "vistos", "materia","remate","convocatoria","postores",
        ]

    @property
    def prompt_extraccion(self) -> str:
        return (
            "Actúa como un extractor de datos legales de alta precisión especializado en "
            "resoluciones judiciales peruanas sobre remates de inmuebles. Analiza el texto "
            "o PDF y devuelve únicamente los datos del esquema JSON.\n\n"
            "REGLAS:\n"
            "1. No inventes ni completes datos mediante suposiciones.\n"
            "2. numero_expediente: usa el identificador completo si aparece; si no, null.\n"
            "3. demandantes y demandados: devuelve listas de nombres limpios, sin roles, "
            "etiquetas ni saltos de línea. Si no se identifican, devuelve []. No confundas "
            "abogados, jueces, peritos ni martilleros con las partes.\n"
            "4. direccion: devuelve solo la dirección del inmueble que conste explícitamente; "
            "si no aparece o es ambigua, null.\n"
            "5. requiere_cartel: true únicamente cuando una resolución ordene expresamente "
            "el pegado de carteles físicos; false únicamente si consta expresamente que no "
            "se requiere; null cuando el documento no lo aclara.\n"
            "6. Distingue instrucciones de publicación electrónica de la orden de colocar "
            "carteles físicos.\n"
            "7. Conserva nombres propios, números y denominaciones tal como aparecen, "
            "corrigiendo únicamente cortes de línea evidentes."
        )

    PATRON_ESTANDAR = r"\b\d{5}-\d{4}-\d+-\d{4}-[A-Z]+-[A-Z]+-\d+\b"
    PATRON_SECUNDARIO = r"EXPEDIENTE\s*:\s*([^\n\r]+)"

    @property
    def campos_requeridos(self) -> List[str]:
        # Los campos presentes en el esquema se revisan, aunque algunos admitan null/lista vacía.
        return [
            "numero_expediente",
            "demandantes",
            "demandados",
            "direccion",
            "requiere_cartel",
        ]

    def extraer_identificador(self, texto: str) -> str:
        if not texto:
            return "No detectado"

        match = re.search(self.PATRON_ESTANDAR, texto, re.IGNORECASE)
        if match:
            return match.group(0).upper()

        match_secundario = re.search(
            self.PATRON_SECUNDARIO,
            texto,
            re.IGNORECASE,
        )
        if match_secundario:
            valor = match_secundario.group(1).strip(" \t:;,.")
            return valor or "No detectado"

        return "No detectado"

    # Dentro del plugin chaskiwasi_plugin_remaju (config.py)

    def fusionar_datos(self, scraper_metadata: Dict[str, Any], ai_extraction_result: Dict[str, Any]) -> Dict[str, Any]:
        """Reglas de negocio exclusivas para el dominio de Remates Judiciales (Remaju)."""
        registro_unificado = dict(scraper_metadata)
        datos_ia = ai_extraction_result.get("datos_extraidos", {})
        
        expediente_ia = datos_ia.get("numero_expediente")
        if expediente_ia and expediente_ia != "No detectado":
            if "remate" in registro_unificado:
                registro_unificado["remate"]["expediente"] = expediente_ia
            else:
                registro_unificado["numero_expediente"] = expediente_ia

        if datos_ia.get("demandantes"):
            registro_unificado["demandantes_validados_ia"] = datos_ia["demandantes"]
        if datos_ia.get("demandados"):
            registro_unificado["demandados_validados_ia"] = datos_ia["demandados"]

        registro_unificado["resolucion_judicial_analisis"] = {
            "direccion_inmueble": datos_ia.get("direccion"),
            "requiere_cartel": datos_ia.get("requiere_cartel", False),
            "campos_faltantes_ia": ai_extraction_result.get("campos_faltantes", []),
            "completado_exitosamente": ai_extraction_result.get("completado_exitosamente", False)
        }
        
        return registro_unificado