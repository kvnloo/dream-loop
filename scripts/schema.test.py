"""Validate declarative evidence contracts with their real schema consumer."""
import copy
import json
from pathlib import Path
import unittest
import jsonschema

ROOT=Path(__file__).resolve().parents[1]

class Schema(unittest.TestCase):
    def test_v2_sidecar_keeps_unknown_costs_and_separate_owner_status(self):
        schema_path=ROOT/'templates/rounds.schema.json'
        self.assertTrue(schema_path.exists(),'v2 observation schema missing')
        schema=json.loads(schema_path.read_text())
        jsonschema.Draft202012Validator.check_schema(schema)
        validate=jsonschema.Draft202012Validator(schema,format_checker=jsonschema.FormatChecker()).validate
        row=json.loads((ROOT/'templates/round.example.json').read_text());validate(row)
        self.assertIsNone(row['cost']['api_usd']['value'])
        self.assertEqual(row['outcomes']['owner'],'not_reviewed')
        for modify in [lambda x:x['cost']['api_usd'].update(value=-1),
                       lambda x:x['cost']['api_usd'].update(value=0,status='unknown'),
                       lambda x:x['outcomes'].update(owner='auto_approved'),
                       lambda x:x['cohort'].update(target_sha256='not-a-hash'),
                       lambda x:x.update(event='discovery_node'),
                       lambda x:x.update(timestamp='yesterday')]:
            invalid=copy.deepcopy(row);modify(invalid)
            with self.assertRaises(jsonschema.ValidationError):validate(invalid)

if __name__=='__main__':unittest.main()
