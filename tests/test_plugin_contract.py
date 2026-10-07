from chaskiwasi.plugins.contracts import PluginDefinition, PluginContext

from chaskiwasi_plugin_remaju.plugin import create_plugin, create_strategies
from chaskiwasi_plugin_remaju.taxonomy import SectionEnum, SourceEnum


def test_plugin_definition_matches_core_contract():
    plugin = create_plugin()
    assert isinstance(plugin, PluginDefinition)
    assert plugin.name == "remaju"
    assert plugin.taxonomy.name == "remaju"
    assert plugin.extractor is not None
    assert plugin.query_rules_factory is not None


def test_strategies_are_plugin_owned():
    plugin = create_plugin()
    context = PluginContext(plugin.name, plugin.taxonomy)
    strategies = create_strategies(context)
    assert len(strategies) == 2

    regex = strategies[0]
    assert any(rule.section is SectionEnum.HEADER for rule in regex.rules)
    assert any(rule.section is SectionEnum.BODY for rule in regex.rules)
    assert any(rule.section is SectionEnum.FOOTER for rule in regex.rules)
    assert SourceEnum.REMAJU_RESOLUTION in [rule.source for rule in regex.rules]
