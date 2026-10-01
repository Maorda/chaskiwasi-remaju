# D:\libs\chaskiwasi_plugin_remaju\src\chaskiwasi_plugin_remaju\factory.py
"""
Fábrica principal para el plugin REMAJU.
"""
def create_cascade_factory():
    # Lazy Loading: importaciones locales del plugin
    from chaskiwasi_plugin_remaju.taxonomy import get_taxonomy_registry, SourceEnum
    from chaskiwasi_plugin_remaju.domain_rules import get_domain_rules
    from chaskiwasi_plugin_remaju.gemini_rules import get_gemini_rules

    taxonomy = get_taxonomy_registry()
    domain_rules = get_domain_rules()
    gemini_rules = get_gemini_rules()

    return {
        "source": SourceEnum.REMAJU_RESOLUTION,
        "taxonomy": taxonomy,
        "domain_rules": domain_rules,
        "gemini_rules": gemini_rules,
    }