"""단계 구성 승인과 결과 수용의 변경·보류·출처 가드를 검증한다."""

from contextlib import redirect_stdout, redirect_stderr
from copy import deepcopy
import io
import json
from pathlib import Path
import tempfile
import unittest

import stage_review as control


class StageReviewTests(unittest.TestCase):
    def record(self):
        data = control.template('test-project', ['S1', 'S2'])
        for stage in data['stages']:
            stage['configuration']['agents'][0].update(model='requested-model', effort='high')
            stage['configuration']['permissions'] = ['소유 파일 편집만; 원격 쓰기 금지']
            stage['configuration']['cost_scope'] = '현재 승인된 구독 범위'
            stage['result'] = {
                'revision': 'result-v1', 'summary': '검토 가능한 구현',
                'artifacts': ['https://github.com/example/repo/pull/1'],
                'checks': ['unit tests: PASS, 대상 result-v1'], 'limitations': ['실행 모델 준수 미검증'],
            }
            self.review(stage)
            self.review(stage, result=True)
        return data

    def review(self, stage, result=False, decision=None, at=None):
        review = {
            'decision': decision or ('accepted' if result else 'approved'),
            'target': control.target(stage, result),
            'source': {
                'kind': 'chat', 'reference': '대화 test / 사용자 응답 1',
                'at': at or ('2026-11-08T09:02:00+09:00' if result else '2026-11-08T09:00:00+09:00'),
                'actor': 'user', 'recorded_by': 'agent',
            },
            'response': '테스트용 명시적 사용자 답변', 'scope': '해당 단계의 지정 구성/결과만',
        }
        stage['result_reviews' if result else 'configuration_reviews'].append(review)
        return review

    def test_normal_transition_requires_previous_acceptance_and_current_configuration(self):
        data = self.record()
        data['stages'][1]['result_reviews'] = []
        self.assertEqual(control.check(data, 'S2', 'enter')['status'], 'PASS')
        with self.assertRaisesRegex(ValueError, '사용자 검토 대기'):
            control.check(data, 'S2', 'accept')
        self.review(data['stages'][1], result=True)
        self.assertEqual(control.check(data, 'S2', 'accept')['status'], 'PASS')

    def test_approved_configuration_can_enter_before_result_exists(self):
        data = control.template('project', ['S2'])
        self.review(data['stages'][0])
        self.assertEqual(control.check(data, 'S2', 'enter')['status'], 'PASS')
        with self.assertRaises(ValueError):
            control.check(data, 'S2', 'accept')

    def test_malformed_records_fail_with_validation_errors(self):
        for data in (None, [], {}, {'schema_version': True, 'project': 'p', 'stages': []}):
            with self.subTest(data=data), self.assertRaises(ValueError):
                control.validate(data)
        for section, value in [('configuration', []), ('configuration_reviews', None),
                               ('result', []), ('result_reviews', {})]:
            data = self.record()
            data['stages'][0][section] = value
            with self.subTest(section=section), self.assertRaises(ValueError):
                control.validate(data)

    def test_no_approval_is_created_by_template_or_validation(self):
        data = control.template('project', ['S1'])
        before = deepcopy(data)
        control.validate(data)
        with self.assertRaisesRegex(ValueError, '사용자 검토 대기'):
            control.check(data, 'S1', 'enter')
        self.assertEqual(data, before)

    def test_every_configuration_change_expires_existing_approval_without_version_bump(self):
        mutations = {
            'model': lambda c: c['agents'][0].update(model='another-model'),
            'effort': lambda c: c['agents'][0].update(effort='medium'),
            'role': lambda c: c['agents'][0].update(role='reviewer'),
            'ownership': lambda c: c['agents'][0].update(ownership=['another/path']),
            'permissions': lambda c: c.update(permissions=['원격 쓰기']),
            'cost_scope': lambda c: c.update(cost_scope='추가 유료 실행'),
            'agents': lambda c: c['agents'].append({**c['agents'][0], 'id': 'second'}),
            'max_concurrency': lambda c: c.update(max_concurrency=2),
            'version': lambda c: c.update(version='v2'),
        }
        for name, mutate in mutations.items():
            data = self.record()
            stage = data['stages'][1]
            if name == 'max_concurrency':
                stage['configuration']['agents'].append({**stage['configuration']['agents'][0], 'id': 'second'})
                stage['configuration_reviews'] = []
                self.review(stage)
            mutate(stage['configuration'])
            with self.subTest(field=name), self.assertRaisesRegex(ValueError, '검토 대상 변경'):
                control.check(data, 'S2', 'enter')

    def test_stage_contract_revision_or_wrong_stage_expires_approval(self):
        for field in ('revision', 'id'):
            data = self.record()
            data['stages'][1][field] = 'changed'
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, '검토 대상 변경'):
                control.check(data, data['stages'][1]['id'], 'enter')

    def test_result_revision_and_content_changes_only_expire_result_acceptance(self):
        for field, value in [('revision', 'result-v2'), ('summary', '추가 요청 반영'),
                             ('artifacts', ['new-output']), ('checks', ['새 검사 PASS']),
                             ('limitations', [])]:
            data = self.record()
            stage = data['stages'][0]
            stage['result'][field] = value
            with self.subTest(field=field):
                self.assertEqual(control.check(data, 'S1', 'enter')['status'], 'PASS')
                with self.assertRaisesRegex(ValueError, '검토 대상 변경'):
                    control.check(data, 'S1', 'accept')
                with self.assertRaises(ValueError):
                    control.check(data, 'S2', 'enter')
                self.review(stage, result=True, at='2026-11-08T09:03:00+09:00')
                self.assertEqual(control.check(data, 'S2', 'enter')['status'], 'PASS')

    def test_changes_requested_allows_same_stage_rework_but_blocks_next(self):
        data = self.record()
        self.review(data['stages'][0], result=True, decision='changes_requested')
        self.assertEqual(control.check(data, 'S1', 'enter')['status'], 'PASS')
        with self.assertRaisesRegex(ValueError, 'changes_requested'):
            control.check(data, 'S2', 'enter')

    def test_result_hold_blocks_execution_until_explicit_resume_record(self):
        data = self.record()
        self.review(data['stages'][0], result=True, decision='held')
        for stage_id in ('S1', 'S2'):
            with self.subTest(stage=stage_id), self.assertRaises(ValueError):
                control.check(data, stage_id, 'enter')
        self.review(data['stages'][0], result=True, decision='changes_requested')
        self.assertEqual(control.check(data, 'S1', 'enter')['status'], 'PASS')

    def test_latest_configuration_rejection_or_hold_overrides_earlier_approval(self):
        for decision in ('held', 'changes_requested'):
            data = self.record()
            self.review(data['stages'][1], decision=decision)
            with self.subTest(decision=decision), self.assertRaises(ValueError):
                control.check(data, 'S2', 'enter')

    def test_predecessors_all_need_acceptance_not_just_immediate_predecessor(self):
        data = self.record()
        last = deepcopy(data['stages'][1])
        last['id'] = 'S3'
        last['configuration_reviews'] = []
        self.review(last)
        data['stages'].append(last)
        data['stages'][0]['result_reviews'] = []
        with self.assertRaisesRegex(ValueError, 'S1'):
            control.check(data, 'S3', 'enter')

    def test_missing_required_configuration_and_source_fields_fail_closed(self):
        for field in ('version', 'agents', 'max_concurrency', 'permissions', 'cost_scope'):
            data = self.record()
            del data['stages'][0]['configuration'][field]
            with self.subTest(field=field), self.assertRaises(ValueError):
                control.validate(data)
        for field in ('kind', 'reference', 'at', 'actor', 'recorded_by'):
            data = self.record()
            del data['stages'][0]['configuration_reviews'][0]['source'][field]
            with self.subTest(field=field), self.assertRaises(ValueError):
                control.validate(data)
        for field in ('target', 'response', 'scope'):
            data = self.record()
            del data['stages'][0]['configuration_reviews'][0][field]
            with self.subTest(field=field), self.assertRaises(ValueError):
                control.validate(data)

    def test_missing_result_fields_are_rejected(self):
        for field in ('revision', 'summary', 'artifacts', 'checks', 'limitations'):
            data = self.record()
            del data['stages'][0]['result'][field]
            with self.subTest(field=field), self.assertRaises(ValueError):
                control.validate(data)

    def test_agent_ci_silence_and_invalid_time_cannot_be_approval_sources(self):
        for field, value in [('actor', 'agent'), ('actor', 'CI'), ('reference', ''),
                             ('at', '2026-11-08T09:00:00'), ('at', 'bad'), ('kind', 'consensus')]:
            data = self.record()
            data['stages'][0]['configuration_reviews'][0]['source'][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                control.validate(data)
        data = self.record()
        data['stages'][0]['configuration_reviews'][0]['response'] = ''
        with self.assertRaises(ValueError):
            control.validate(data)

    def test_out_of_order_history_and_result_older_than_configuration_are_rejected(self):
        data = self.record()
        self.review(data['stages'][0], at='2026-11-08T08:00:00+09:00')
        with self.assertRaisesRegex(ValueError, '시각 순서'):
            control.validate(data)
        data = self.record()
        self.review(data['stages'][0], at='2026-11-08T09:03:00+09:00')
        with self.assertRaisesRegex(ValueError, '오래된 결과'):
            control.check(data, 'S1', 'accept')

    def test_duplicate_ids_and_boolean_counts_are_rejected(self):
        data = self.record()
        data['stages'][1]['id'] = 'S1'
        with self.assertRaises(ValueError):
            control.validate(data)
        data = self.record()
        data['stages'][0]['configuration']['max_concurrency'] = True
        with self.assertRaises(ValueError):
            control.validate(data)

    def test_cli_validation_is_distinct_from_guard_and_never_claims_remote_or_human_proof(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'record.json'
            path.write_text(json.dumps(control.template('project', ['S1'])), encoding='utf-8')
            for command, extra, expected in [
                ('validate', [], 0),
                ('digest', ['--stage', 'S1', '--target', 'configuration'], 0),
                ('check', ['--stage', 'S1', '--action', 'enter'], 1),
            ]:
                output = io.StringIO()
                with redirect_stdout(output):
                    code = control.main([command, '--file', str(path), *extra])
                report = json.loads(output.getvalue())
                self.assertEqual(code, expected)
                for key in ('human_verified', 'remote_verified', 'model_compliance_verified'):
                    self.assertFalse(report[key])
            path.write_text('{"schema_version": 1, "schema_version": 1}', encoding='utf-8')
            with redirect_stdout(io.StringIO()):
                self.assertEqual(control.main(['validate', '--file', str(path)]), 1)
        output = io.StringIO()
        with redirect_stdout(output), redirect_stderr(io.StringIO()):
            self.assertEqual(control.main(['template', '--project', 'p', '--stage', 'S1']), 0)
        self.assertEqual(json.loads(output.getvalue())['stages'][0]['configuration_reviews'], [])


if __name__ == '__main__':
    unittest.main()
