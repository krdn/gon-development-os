"""원격 변경 금지와 미확인 관리 기록의 성공 오판 방지를 검증한다."""

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

import github_control as control


class GitHubControlTests(unittest.TestCase):
    def synced(self):
        data = control.template('owner/repo', 'github.com', 'TASK-001')
        data['sync_state'] = 'synced'
        for feature in data['features'].values():
            feature.update(status='not_applicable', reason='이번 단계 적용 대상 아님')
        for key, path in [('documents', 'commit/' + 'a'*40), ('issues', 'issues/1')]:
            data['features'][key].update(status='used', evidence=[{
                'url': 'https://github.com/owner/repo/' + path,
                'checked_at': '2026-10-31T12:00:00+00:00',
            }])
        return data

    def test_valid_receipt_explicitly_does_not_verify_remote_truth(self):
        result = control.validate_receipt(self.synced())
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['scope'], 'structure_only')
        self.assertFalse(result['remote_verified'])

    def test_pending_record_cannot_claim_synced(self):
        data = self.synced()
        data['features']['projects'].update(status='pending', reason='권한 확인 중')
        with self.assertRaises(ValueError):
            control.validate_receipt(data)

    def test_unavailable_feature_requires_fallback_when_synced(self):
        data = self.synced()
        data['features']['projects'].update(status='unavailable', reason='프로젝트 읽기 권한 없음')
        with self.assertRaises(ValueError):
            control.validate_receipt(data)
        data['features']['projects']['fallback'] = [{
            'url':'https://github.com/owner/repo/issues/1',
            'checked_at':'2026-10-31T12:00:00Z',
        }]
        self.assertEqual(control.validate_receipt(data)['status'], 'PASS')

    def test_missing_coverage_reason_or_evidence_is_rejected(self):
        for change in ('coverage', 'reason', 'evidence', 'work_link'):
            data = self.synced()
            if change == 'coverage':
                del data['features']['security']
            elif change == 'reason':
                data['features']['wiki']['reason'] = ''
            elif change == 'evidence':
                data['features']['documents']['evidence'] = []
            else:
                data['features']['issues'].update(status='not_applicable', reason='작업 연결 없음')
            with self.subTest(change=change), self.assertRaises(ValueError):
                control.validate_receipt(data)

    def test_cross_repository_host_credentials_and_path_traversal_are_rejected(self):
        for url in (
            'https://github.com/other/repo/issues/1',
            'https://github.com/owner/repo-other/issues/1',
            'https://evil.example/owner/repo/issues/1',
            'https://token@github.com/owner/repo/issues/1',
            'https://github.com/owner/repo/issues/1?token=private',
            'https://github.com/owner/repo/%2e%2e/other',
            'file:///owner/repo/issues/1',
        ):
            with self.subTest(url=url), self.assertRaises(ValueError):
                control.check_evidence({'url':url,'checked_at':'2026-10-31T12:00:00Z'},
                                       'owner/repo','github.com')

    def test_organization_project_is_allowed_only_for_project_evidence(self):
        entry={'url':'https://github.com/orgs/org/projects/7',
               'checked_at':'2026-10-31T12:00:00Z'}
        control.check_evidence(entry,'owner/repo','github.com',allow_project=True)
        with self.assertRaises(ValueError):
            control.check_evidence(entry,'owner/repo','github.com')

    def test_missing_or_naive_observation_time_is_rejected(self):
        for stamp in (None,'not-a-time','2026-10-31T12:00:00'):
            with self.subTest(stamp=stamp), self.assertRaises(ValueError):
                control.check_evidence({'url':'https://github.com/owner/repo/issues/1',
                                        'checked_at':stamp},'owner/repo','github.com')

    def test_all_inspection_requests_are_explicit_get_and_do_not_expose_payloads(self):
        calls=[]
        def fake_run(command, **kwargs):
            calls.append(command)
            value={'full_name':'owner/repo','has_issues':True} if command[-1]=='repos/owner/repo' else []
            return SimpleNamespace(returncode=0,stdout=json.dumps(value),stderr='')
        with patch.object(control.subprocess,'run',side_effect=fake_run):
            result=control.inspect_repo('owner/repo','github.com')
        self.assertEqual(len(calls),8)
        self.assertTrue(all(command[command.index('--method')+1]=='GET' for command in calls))
        self.assertFalse(result['writes_verified'])
        self.assertEqual(result['projects']['read_access'],'unknown')

    def test_forbidden_probe_is_unknown_and_does_not_claim_disabled(self):
        def getter(host,path):
            if path=='repos/owner/repo':
                return {'full_name':'owner/repo'}
            raise control.ProbeError('HTTP 403')
        result=control.inspect_repo('owner/repo','github.com',getter=getter)
        self.assertTrue(all(probe['read_access']=='unknown' for probe in result['probes'].values()))

    def test_raw_authentication_error_is_never_returned(self):
        response=SimpleNamespace(returncode=1,stdout='',stderr='sensitive-response HTTP 404')
        with patch.object(control.subprocess,'run',return_value=response):
            with self.assertRaises(control.ProbeError) as error:
                control.gh_get('github.com','repos/owner/repo')
        self.assertEqual(str(error.exception),'HTTP 404')

    def test_wrong_repository_and_invalid_input_are_rejected(self):
        with self.assertRaises(ValueError):
            control.inspect_repo('owner/repo','github.com',getter=lambda *args: {'full_name':'other/repo'})
        for repo,host in [('owner/repo;echo','github.com'),('owner/repo','https://github.com'),
                          ('owner/repo','github.com/path')]:
            with self.subTest(repo=repo,host=host), self.assertRaises(ValueError):
                control.identity(repo,host)

    def test_offline_validation_never_calls_cli(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'receipt.json'
            path.write_text(json.dumps(self.synced()))
            with patch.object(control.subprocess,'run',side_effect=AssertionError('네트워크 호출 금지')):
                with redirect_stdout(io.StringIO()) as output:
                    result=control.main(['validate','--file',str(path)])
        self.assertEqual(result,0)
        self.assertFalse(json.loads(output.getvalue())['remote_verified'])


if __name__=='__main__':
    unittest.main()
