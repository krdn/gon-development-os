#!/usr/bin/env python3
"""GitHub 기능을 읽기 전용으로 점검하고 관리 기록의 구조를 검사한다."""

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit


FEATURES = (
    'documents', 'issues', 'projects', 'milestones', 'labels_assignees',
    'discussions', 'wiki', 'pull_requests', 'actions', 'releases', 'deployments',
    'security', 'packages_pages', 'rules_access', 'insights',
)
STATES = ('used', 'not_applicable', 'unavailable', 'pending')


def identity(repo, hostname):
    if not isinstance(repo, str) or not re.fullmatch(r'[A-Za-z0-9_-]+/[A-Za-z0-9_.-]+', repo):
        raise ValueError('저장소는 OWNER/REPO 형식이어야 합니다.')
    if not isinstance(hostname, str) or not re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?', hostname):
        raise ValueError('hostname에는 URL/경로/인증값을 넣을 수 없습니다.')


def template(repo, hostname, task_key):
    identity(repo, hostname)
    if not isinstance(task_key, str) or not task_key.strip():
        raise ValueError('실제 작업 식별자가 필요합니다.')
    return {
        'schema_version': 1, 'repository': repo, 'hostname': hostname,
        'task_key': task_key, 'sync_state': 'pending_sync',
        'features': {key: {'status': 'pending', 'reason': '', 'evidence': [],
                           'fallback': []} for key in FEATURES},
    }


def check_evidence(value, repo, hostname, allow_project=False):
    if not isinstance(value, dict):
        raise ValueError('증거는 url과 checked_at을 가진 객체여야 합니다.')
    url = value.get('url')
    if not isinstance(url, str):
        raise ValueError('증거 URL이 필요합니다.')
    parsed = urlsplit(url)
    if (parsed.scheme != 'https' or parsed.netloc.lower() != hostname.lower()
            or parsed.username or parsed.password or parsed.query):
        raise ValueError('증거는 지정 host의 인증값·query 없는 HTTPS URL이어야 합니다.')
    path = unquote(parsed.path)
    if '..' in path.split('/') or '\\' in path:
        raise ValueError('증거 경로에 상위/우회 경로를 사용할 수 없습니다.')
    in_repo = path.lower().startswith('/' + repo.lower() + '/')
    in_project = bool(re.fullmatch(r'/(?:users|orgs)/[A-Za-z0-9_-]+/projects/[0-9]+/?', path))
    if not in_repo and not (allow_project and in_project):
        raise ValueError('증거는 대상 저장소 경로 또는 Projects 원격 URL이어야 합니다.')
    stamp = value.get('checked_at')
    if not isinstance(stamp, str):
        raise ValueError('원격 재조회 시점 checked_at이 필요합니다.')
    try:
        observed = datetime.fromisoformat(stamp.replace('Z', '+00:00'))
    except ValueError as error:
        raise ValueError('checked_at은 ISO 8601 시각이어야 합니다.') from error
    if observed.tzinfo is None:
        raise ValueError('checked_at에 시간대가 필요합니다.')


def validate_receipt(record):
    if not isinstance(record, dict) or record.get('schema_version') != 1:
        raise ValueError('지원하는 schema_version은 1입니다.')
    repo, host = record.get('repository'), record.get('hostname')
    identity(repo, host)
    if not isinstance(record.get('task_key'), str) or not record['task_key'].strip():
        raise ValueError('task_key가 필요합니다.')
    if record.get('sync_state') not in ('pending_sync', 'synced'):
        raise ValueError('sync_state는 pending_sync 또는 synced입니다.')
    features = record.get('features')
    if not isinstance(features, dict) or not set(FEATURES).issubset(features):
        raise ValueError('필수 GitHub 기능별 검토 항목이 누락됐습니다.')
    for key, feature in features.items():
        if not isinstance(feature, dict) or feature.get('status') not in STATES:
            raise ValueError(f'{key}: 기능 상태가 잘못됐습니다.')
        status = feature['status']
        for collection in ('evidence', 'fallback'):
            entries = feature.get(collection)
            if not isinstance(entries, list):
                raise ValueError(f'{key}: {collection}은 목록이어야 합니다.')
            for entry in entries:
                check_evidence(entry, repo, host, allow_project=(key == 'projects'))
        if status != 'used' and (not isinstance(feature.get('reason'), str)
                                  or not feature['reason'].strip()):
            raise ValueError(f'{key}: 미사용/미완료 사유가 필요합니다.')
        if status == 'used' and not feature['evidence']:
            raise ValueError(f'{key}: 원격 증거가 필요합니다.')
        if record['sync_state'] == 'synced':
            if status == 'pending':
                raise ValueError(f'{key}: pending 항목을 synced로 처리할 수 없습니다.')
            if status == 'unavailable' and not feature['fallback']:
                raise ValueError(f'{key}: 사용 불가 시 대체 GitHub 기록이 필요합니다.')
    if record['sync_state'] == 'synced':
        if features['documents']['status'] != 'used':
            raise ValueError('synced에는 저장소 문서/commit의 원격 근거가 필요합니다.')
        if not any(features[key]['status'] == 'used' for key in ('issues', 'pull_requests')):
            raise ValueError('synced에는 이슈 또는 PR의 작업 연결이 필요합니다.')
    return {'status': 'PASS', 'scope': 'structure_only', 'remote_verified': False,
            'sync_state': record['sync_state'], 'feature_count': len(features)}


class ProbeError(Exception):
    pass


def gh_get(hostname, endpoint):
    command = ['gh', 'api', '--hostname', hostname, '--method', 'GET', endpoint]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=20,
                                check=False)
    except FileNotFoundError as error:
        raise ProbeError('gh 실행파일 없음') from error
    except subprocess.TimeoutExpired as error:
        raise ProbeError('조회 시간 초과') from error
    if result.returncode:
        status = re.search(r'HTTP (\d{3})', result.stderr or '')
        # 원본 응답/오류에는 인증 또는 사적 내용이 있을 수 있어 출력하지 않는다.
        raise ProbeError('HTTP ' + status.group(1) if status else '인증/권한/연결 조회 실패')
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise ProbeError('JSON 응답을 확인할 수 없음') from error


def inspect_repo(repo, hostname, getter=gh_get):
    identity(repo, hostname)
    prefix = 'repos/' + repo
    metadata = getter(hostname, prefix)
    if not isinstance(metadata, dict) or metadata.get('full_name', '').lower() != repo.lower():
        raise ValueError('조회한 저장소와 지정 저장소가 다릅니다.')
    probes = {
        'actions': '/actions/workflows?per_page=1', 'releases': '/releases?per_page=1',
        'deployments': '/deployments?per_page=1', 'environments': '/environments?per_page=1',
        'milestones': '/milestones?state=all&per_page=1', 'labels': '/labels?per_page=1',
        'rulesets': '/rulesets?per_page=1',
    }

    def probe(item):
        key, suffix = item
        try:
            getter(hostname, prefix + suffix)
            return key, {'read_access': 'observed', 'configuration_verified': False}
        except ProbeError as error:
            return key, {'read_access': 'unknown', 'reason': str(error)}

    with ThreadPoolExecutor(max_workers=4) as executor:
        access = dict(executor.map(probe, probes.items()))
    return {
        'scope': 'read_only_capability', 'checked_at': datetime.now(timezone.utc).isoformat(),
        'repository': repo, 'hostname': hostname,
        'metadata': {key: metadata.get(key) for key in (
            'html_url', 'default_branch', 'private', 'archived', 'permissions',
            'has_issues', 'has_discussions', 'has_wiki', 'has_pages',
        )},
        'probes': access, 'writes_verified': False,
        'projects': {'read_access': 'unknown',
                     'reason': '사용자/조직 소유 Project를 별도로 조회해야 합니다.'},
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('inspect', 'template'):
        command = commands.add_parser(name)
        command.add_argument('--repo', required=True)
        command.add_argument('--hostname', default='github.com')
        if name == 'template':
            command.add_argument('--task-key', required=True)
    commands.add_parser('validate').add_argument('--file', required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == 'inspect':
            result = inspect_repo(args.repo, args.hostname)
        elif args.command == 'template':
            result = template(args.repo, args.hostname, args.task_key)
        else:
            result = validate_receipt(json.loads(args.file.read_text(encoding='utf-8')))
    except (ValueError, OSError, ProbeError, TypeError) as error:
        # 입력 JSON의 내용 자체나 인증 응답을 표시하지 않는다.
        print(json.dumps({'status': 'ERROR', 'error': str(error)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
