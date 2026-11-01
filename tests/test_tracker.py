import csv
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('tracker', ROOT / 'tracker.py')
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)

class TrackerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def write(self, name, headers, rows):
        path = self.root / name
        with path.open('w', newline='', encoding='utf-8') as f:
            w = csv.writer(f); w.writerow(headers); w.writerows(rows)
        return path

    def inputs(self, rows=None, citations=None):
        if rows is None:
            rows = [self.row('a'), self.row('b'), self.row('c', market='France')]
        a = self.write('answers.csv', t.ANSWER_FIELDS, rows)
        c = self.write('citations.csv', t.CITATION_FIELDS, citations or [])
        return a, c

    def row(self, ident, market='Morocco', prompt='p1', text='An answer'):
        return [ident, '2026-10-01', 'Example engine', 'v1', 'web', 'en', market, prompt, 'Who is cited?', text]

    def test_explicit_group_denominators_uncited_retained_and_repeats_count(self):
        a,c = self.inputs(citations=[['a','https://EXAMPLE.org:443/x#one'],['a','https://example.org/x#two'],['a','https://example.org/x?q=1'],['c','https://example.org/x']])
        report = t.analyze(a,c,'2026-11-01')
        self.assertEqual(len(report['answers']),3)
        group = next(g for g in report['groups'] if g['market']=='Morocco')
        self.assertEqual((group['answer_count'],group['cited_answer_count'],group['explicit_citation_count']),(2,1,2))
        self.assertEqual(group['cited_answer_rate'],0.5)
        self.assertEqual(group['citations_per_answer'],1)
        self.assertEqual(group['top_hostnames'],[{'hostname':'example.org','citation_count':2,'answer_count':1}])
        self.assertEqual(report['answers'][1]['citation_count'],0)
        self.assertEqual(report['answers'][0]['unique_hostname_count'],1)

    def test_url_normalization_retains_query_and_path(self):
        self.assertEqual(t.normalize_url('HTTPS://BÜCHER.example:443/a?b=2&a=1#x'),'https://xn--bcher-kva.example/a?b=2&a=1')
        self.assertEqual(t.normalize_url('http://[2001:db8::1]:80'),'http://[2001:db8::1]/')
        self.assertNotEqual(t.normalize_url('https://example.org/?x=1'),t.normalize_url('https://example.org/?x=2'))
        self.assertNotEqual(t.normalize_url('https://example.org/A'),t.normalize_url('https://example.org/a'))

    def test_unsafe_and_malformed_urls(self):
        for url in ['javascript:alert(1)','ftp://example.org','https://user:pw@example.org','https://bad host/x','https://example.org:99999','https:///x','https://-bad.example','https://example.org/%ZZ','https://example.org/\nfoo','https://example.org\\evil','https://example.org:', 'https://example.org/<bad>', 'https://example.org/a|b']:
            with self.subTest(url=url), self.assertRaises(ValueError): t.normalize_url(url)

    def test_strict_rows_dates_references_and_ids(self):
        cases = [([self.row('a'),self.row('a')],[]),([self.row('a')],[['missing','https://example.org']]),([],[])]
        for rows,cites in cases:
            a,c=self.inputs(rows,cites)
            with self.assertRaises(ValueError): t.analyze(a,c,'2026-11-01')
        for column,value in [(0,'bad id'),(1,'2026-12-01'),(1,'2026-1-01'),(2,''),(5,'english'),(8,'')]:
            row=self.row('a'); row[column]=value
            a,c=self.inputs([row])
            with self.subTest(column=column,value=value), self.assertRaises(ValueError): t.analyze(a,c,'2026-11-01')

    def test_strict_headers_and_quoting(self):
        a,c=self.inputs()
        a.write_text('answer_id,answer_id\na,a\n')
        with self.assertRaises(ValueError): t.analyze(a,c,'2026-11-01')
        a.write_text(','.join(t.ANSWER_FIELDS)+'\n"unterminated')
        with self.assertRaises(ValueError): t.analyze(a,c,'2026-11-01')

    def test_formula_guard_handles_bom_and_unicode_whitespace(self):
        self.assertTrue(t.safe_cell('\ufeff\u2003 \ufeff=SUM(1)').startswith("'"))

    def test_rejects_stray_quote_in_unquoted_csv_field(self):
        a,c=self.inputs([self.row('a')])
        a.write_text(a.read_text().replace('An answer','An "answer'))
        with self.assertRaises(ValueError): t.analyze(a,c,'2026-11-01')

    def test_rejects_output_files_aliased_to_each_other(self):
        a,c=self.inputs(); report=t.analyze(a,c,'2026-11-01')
        out=self.root/'out'; out.mkdir()
        (out/'report.json').write_text('old')
        import os
        os.link(out/'report.json',out/'report.html')
        with self.assertRaises(ValueError): t.export(report,out,[a,c])
        self.assertEqual((out/'report.json').read_text(),'old')

    def test_embedded_carriage_return_roundtrips_as_one_csv_cell(self):
        text = 'First line\r=1+1'
        path = self.root/'embedded-cr.csv'
        t.write_csv(path,['answer_text'],[{'answer_text':text}])
        with path.open(newline='',encoding='utf-8') as f:
            rows=list(csv.reader(f))
        self.assertEqual(rows,[['answer_text'],[text]])
        self.assertEqual(len(rows),2)  # No extra row beginning with a formula.
        a,c=self.inputs([self.row('a',text=text)])
        out=self.root/'report'
        t.export(t.analyze(a,c,'2026-11-01'),out,[a,c])
        with (out/'answers.csv').open(newline='',encoding='utf-8') as f:
            answers=list(csv.DictReader(f))
        self.assertEqual(len(answers),1)
        self.assertEqual(answers[0]['answer_text'],text)

    def test_safe_html_csv_and_deterministic_outputs(self):
        a,c=self.inputs([self.row('a',market='\ufeff \t=1+1',text='<script>alert(1)</script>')])
        report=t.analyze(a,c,'2026-11-01')
        out=self.root/'out'; t.export(report,out,[a,c])
        html=(out/'report.html').read_text()
        self.assertNotIn('<script>',html)
        self.assertIn('&lt;script&gt;',html)
        with (out/'answers.csv').open(newline='',encoding='utf-8') as f:
            rows=list(csv.DictReader(f))
        self.assertTrue(rows[0]['market'].startswith("'"))
        before={p.name:p.read_bytes() for p in out.iterdir()}
        t.export(t.analyze(a,c,'2026-11-01'),out,[a,c])
        self.assertEqual(before,{p.name:p.read_bytes() for p in out.iterdir()})
        self.assertEqual(json.loads((out/'report.json').read_text())['as_of'],'2026-11-01')

    def test_output_collisions_symlinks_and_hardlinks(self):
        a,c=self.inputs(); report=t.analyze(a,c,'2026-11-01')
        out=self.root/'out'; out.mkdir()
        (out/'answers.csv').symlink_to(a)
        with self.assertRaises(ValueError): t.export(report,out,[a,c])
        (out/'answers.csv').unlink()
        import os
        os.link(a,out/'report.json')
        with self.assertRaises(ValueError): t.export(report,out,[a,c])
        (out/'report.json').unlink()
        (self.root/'linked').symlink_to(out,target_is_directory=True)
        with self.assertRaises(ValueError): t.export(report,self.root/'linked',[a,c])
        with self.assertRaises(ValueError): t.export(report,a,[a,c])

if __name__ == '__main__': unittest.main()
