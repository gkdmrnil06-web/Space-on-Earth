"""Run without network/Streamlit: python test_decision_panels.py"""
import ast
import math
from pathlib import Path

source = Path(__file__).with_name('decision_panels.py').read_text(encoding='utf-8')
module = ast.parse(source)
languages = next(ast.literal_eval(node.value) for node in module.body
                 if isinstance(node, ast.Assign) and any(isinstance(x, ast.Name) and x.id == 'L' for x in node.targets))
assert set(languages) == {'en','tr','ja','fr','de','es','pt','zh','ar'}
assert all(len(items) == 54 for items in languages.values())
assert all(all(isinstance(x, str) and x.strip() for x in items) for items in languages.values())
assert all(languages[code][10] != languages['en'][10] for code in languages if code != 'en')

names = {'_distance_km', '_bbox'}
functions = [n for n in module.body if isinstance(n, ast.FunctionDef) and n.name in names]
env = {'math':math}
exec(compile(ast.Module(body=functions, type_ignores=[]), '<test>', 'exec'), env)
assert env['_distance_km'](0,0,0,0) == 0
assert 110 < env['_distance_km'](0,0,1,0) < 112
w,s,e,n = env['_bbox'](-17,-65)
assert w < -65 < e and s < -17 < n
assert -180 <= w <= e <= 180 and -90 <= s <= n <= 90
assert 'get' in source and 'NASA_FIRMS_MAP_KEY' in source
assert 'st.button' in source and 'fetch_firms' in source
assert 'certificat' in source.lower()
print('PASS: nine languages, geometry, source safety and optional FIRMS wiring')
