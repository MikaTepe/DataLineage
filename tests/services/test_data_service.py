import pytest
import networkx as nx
from app.services.data_service import DataService
from app.models.node import Node

@pytest.fixture
def data_service():
    return DataService(mock_mode=True)

def test_build_mock_graph_for_ceo_dashboard(data_service):
    # Der Artefaktname im Dialog wird der vollqualifizierte sein
    selections = {'artifact': 'REPORTING.V_CEO_DASHBOARD'}
    graph = data_service.get_graph_for_artifact(selections)

    assert isinstance(graph, nx.DiGraph)
    assert graph.number_of_nodes() > 5
    assert graph.number_of_edges() > 4

    # Erwartete Knoten mit bereinigten, vollqualifizierten Namen
    expected_nodes = [
        'REPORTING_V_CEO_DASHBOARD',
        'REPORTING_V_QUARTERLY_SALES',
        'DWH_CORE_F_INVENTORY_LEVELS',
        'REPORTING_ELT_LOAD_REPORTS',
        'DWH_CORE_V_SALES_AGG_MONTHLY',
        'DWH_CORE_V_CUSTOMER_SEGMENTATION'
    ]
    for node_id in expected_nodes:
        assert node_id in graph.nodes, f"Erwarteter Knoten '{node_id}' nicht im Graphen gefunden."

    # Prüfe die korrekte Kette von Kanten
    assert graph.has_edge('REPORTING_V_QUARTERLY_SALES', 'REPORTING_V_CEO_DASHBOARD')
    assert graph.has_edge('REPORTING_ELT_LOAD_REPORTS', 'REPORTING_V_QUARTERLY_SALES')
    assert graph.has_edge('DWH_CORE_V_SALES_AGG_MONTHLY', 'REPORTING_ELT_LOAD_REPORTS')

def test_empty_graph_for_nonexistent_artifact(data_service):
    selections = {'artifact': 'GIBT_ES_NICHT'}
    graph = data_service.get_graph_for_artifact(selections)
    assert isinstance(graph, nx.DiGraph)
    assert graph.number_of_nodes() == 0

def test_node_data_is_populated_correctly(data_service):
    selections = {'artifact': 'DWH_CORE.V_SALES_AGG_MONTHLY'}
    graph = data_service.get_graph_for_artifact(selections)

    node_id = 'DWH_CORE_V_SALES_AGG_MONTHLY'
    node_data = graph.nodes[node_id]['data']

    assert 'DWH_CORE_F_SALES_TRANSACTIONS' in node_data.predecessors
    assert 'DWH_CORE_D_PRODUCT' in node_data.predecessors
    assert 'REPORTING_ELT_LOAD_REPORTS' in node_data.successors