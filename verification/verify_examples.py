"""Independent example checks with RDFLib, NOT an Apache Jena integration test.
Run: python verification/verify_examples.py
Requires: rdflib (tested here with the version recorded in validation-report.md).
The small precondition checks below are NOT a SHACL validator.
"""
from pathlib import Path
from decimal import Decimal
import json
import unittest
import rdflib
from rdflib import Graph, Namespace, Literal, RDF, RDFS, XSD

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / 'examples'
EX = Namespace('https://example.org/vehicle/')
SH = Namespace('http://www.w3.org/ns/shacl#')


def load_graph() -> Graph:
    graph = Graph()
    graph.parse(EXAMPLES / 'ontology.ttl', format='turtle')
    graph.parse(EXAMPLES / 'data.ttl', format='turtle')
    return graph


def run_impact(graph: Graph):
    rows = graph.query((EXAMPLES / 'impact.rq').read_text())
    return [(str(r.vehicleModel), str(r.configuration), str(r.currency),
             r.affectedQuantity.toPython(), r.deltaPerVehicle.toPython()) for r in rows]


def change_constraint_violations(graph: Graph) -> list:
    """Execute only the SPARQL query embedded in ChangeShape, not SHACL Core."""
    shapes = Graph().parse(EXAMPLES / 'shapes.ttl', format='turtle')
    node = shapes.value(EX.ChangeShape, SH.sparql)
    query = str(shapes.value(node, SH.select))
    return list(graph.query(query, initBindings={'this': EX.ECN_2026_017}))


class ExampleChecks(unittest.TestCase):
    def setUp(self):
        self.graph = load_graph()

    def test_01_turtle_files_parse(self):
        self.assertGreater(len(self.graph), 50)
        self.assertGreater(len(Graph().parse(EXAMPLES / 'shapes.ttl', format='turtle')), 20)

    def test_02_expected_costs(self):
        self.assertEqual(run_impact(self.graph), [
            ('V-A', 'STD', 'CNY', Decimal('1.0'), Decimal('20.00')),
            ('V-B', 'PRO', 'CNY', Decimal('2.0'), Decimal('40.00'))])

    def test_03_evidence_has_three_occurrences(self):
        rows = list(self.graph.query((EXAMPLES / 'evidence.rq').read_text()))
        self.assertEqual(len(rows), 3)
        self.assertEqual({str(r.line).rsplit('/', 1)[-1] for r in rows},
                         {'Line_A1', 'Line_B1', 'Line_B2'})

    def test_04_draft_excluded(self):
        self.assertNotIn('V-DRAFT', [r[0] for r in run_impact(self.graph)])

    def test_05_expired_excluded(self):
        self.assertNotIn('V-OLD', [r[0] for r in run_impact(self.graph)])

    def test_06_new_revision_excluded(self):
        self.assertNotIn('V-NEW', [r[0] for r in run_impact(self.graph)])

    def test_07_plain_graph_does_not_infer_part(self):
        self.assertEqual(list(self.graph.query((EXAMPLES / 'parts.rq').read_text())), [])

    def test_08_explicit_hierarchy_path_finds_part(self):
        rows = list(self.graph.query((EXAMPLES / 'parts-path.rq').read_text()))
        self.assertEqual([r.part for r in rows], [EX.P100])

    def test_09_minimal_subclass_materialization_finds_part(self):
        # Implements this example's one subclass rule only, not general RDFS/OWL.
        additions = {(s, RDF.type, sup) for s, cls in self.graph.subject_objects(RDF.type)
                     for sup in self.graph.objects(cls, RDFS.subClassOf)}
        for triple in additions:
            self.graph.add(triple)
        rows = list(self.graph.query((EXAMPLES / 'parts.rq').read_text()))
        self.assertEqual([r.part for r in rows], [EX.P100])

    def test_10_identical_triple_is_not_an_extra_occurrence(self):
        before = len(self.graph)
        self.graph.add((EX.Line_B1, EX.quantity, Literal('1.0', datatype=XSD.decimal)))
        self.assertEqual(len(self.graph), before)
        self.assertEqual(run_impact(self.graph)[1][-1], Decimal('40.00'))

    def test_11_change_sparql_constraint_passes(self):
        self.assertEqual(change_constraint_violations(self.graph), [])

    def test_12_currency_mismatch_is_detected(self):
        self.graph.set((EX.P100_B, EX.currency, Literal('USD')))
        self.assertEqual(len(change_constraint_violations(self.graph)), 1)
        self.assertEqual(run_impact(self.graph), [])
        # Empty query output MUST NOT be interpreted as 'no affected BOM'.

    def test_13_time_end_is_exclusive(self):
        self.graph.set((EX.BOM_A, EX.validTo,
                        Literal('2026-10-15T09:00:00+08:00', datatype=XSD.dateTime)))
        self.assertEqual([r[0] for r in run_impact(self.graph)], ['V-B'])

    def test_14_missing_price_detected_as_missing_not_zero(self):
        self.graph.remove((EX.P100_B, EX.unitPrice, None))
        self.assertEqual(len(list(self.graph.objects(EX.P100_B, EX.unitPrice))), 0)
        self.assertEqual(run_impact(self.graph), [])
        # SHACL sh:minCount 1 is the intended production gate; this test only
        # verifies why querying alone does not safely distinguish missing data.

    def test_15_two_prices_multiply_join_rows(self):
        self.graph.add((EX.P100_B, EX.unitPrice, Literal('125.00', datatype=XSD.decimal)))
        self.assertEqual(len(list(self.graph.objects(EX.P100_B, EX.unitPrice))), 2)
        self.assertEqual(run_impact(self.graph)[0][-1], Decimal('45.00'))
        # Intentional negative case: maxCount=1 must reject before costing.


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ExampleChecks)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = {
        'engine': f'RDFLib {rdflib.__version__}',
        'testsRun': result.testsRun,
        'failures': len(result.failures), 'errors': len(result.errors),
        'success': result.wasSuccessful(),
        'notVerified': ['Apache Jena 6.2.0 runtime', 'Jena SHACL Core execution',
                        'Java snippet compilation', 'Fuseki HTTP deployment',
                        'TDB2 persistence or transaction behavior'],
        'results': [list(map(str, row)) for row in run_impact(load_graph())]
    }
    (ROOT / 'verification' / 'test-results.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
