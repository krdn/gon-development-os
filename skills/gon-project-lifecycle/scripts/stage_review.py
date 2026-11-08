#!/usr/bin/env python3
"""단계 검토 JSON의 구조와 진입/수용 조건만 검사한다. 원격·사람 진위는 검증하지 않는다."""

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import sys


LIMITS = {
    'scope': 'local_record_only',
    'human_verified': False,
    'remote_verified': False,
    'model_compliance_verified': False,
    'notice': ('JSON 일치 검사이며 실제 실행 차단 장치가 아닙니다. '
               '사람의 승인 진위·원격 저장·실제 모델 준수를 증명하지 않습니다.'),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def text(value, path):
    require(isinstance(value, str) and bool(value.strip()), f'{path}: 비어 있지 않은 문자열 필요')


def fields(value, names, path):
    require(isinstance(value, dict), f'{path}: 객체 필요')
    for name in names:
        require(name in value, f'{path}.{name}: 필드 누락')


def strings(value, path, empty=False):
    require(isinstance(value, list) and (empty or bool(value)), f'{path}: 문자열 목록 필요')
    for index, item in enumerate(value):
        text(item, f'{path}[{index}]')


def stamp(value, path):
    text(value, path)
    try:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError as error:
        raise ValueError(f'{path}: ISO 8601 시각 필요') from error
    require(parsed.utcoffset() is not None, f'{path}: 시간대 필요')
    return parsed


def digest(value):
    canonical = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'),
                           allow_nan=False)
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


def validate_reviews(reviews, path, result=False):
    require(isinstance(reviews, list), f'{path}: 목록 필요')
    previous = None
    for index, review in enumerate(reviews):
        label = f'{path}[{index}]'
        fields(review, ('decision', 'target', 'source', 'response', 'scope'), label)
        allowed = ('accepted', 'changes_requested', 'held') if result else (
            'approved', 'changes_requested', 'held',
        )
        require(review['decision'] in allowed, f'{label}.decision: 허용되지 않은 검토 상태')
        for name in ('response', 'scope'):
            text(review[name], f'{label}.{name}')
        target_names = ['stage_id', 'stage_revision', 'configuration_version', 'configuration_digest']
        if result:
            target_names.extend(('result_revision', 'result_digest'))
        fields(review['target'], target_names, f'{label}.target')
        for name in target_names:
            value = review['target'][name]
            text(value, f'{label}.target.{name}')
            if name.endswith('_digest'):
                require(re.fullmatch('[0-9a-f]{64}', value) is not None,
                        f'{label}.target.{name}: SHA-256 필요')
        source = review['source']
        fields(source, ('kind', 'reference', 'at', 'actor', 'recorded_by'), f'{label}.source')
        require(source['kind'] in ('chat', 'github'), f'{label}.source.kind: chat 또는 github 필요')
        require(source['actor'] == 'user', f'{label}: 사용자 답변만 검토 기록으로 사용')
        require(source['recorded_by'] in ('user', 'agent'), f'{label}: 기록 주체 필요')
        text(source['reference'], f'{label}.source.reference')
        observed = stamp(source['at'], f'{label}.source.at')
        require(previous is None or observed >= previous, f'{label}: 답변 시각 순서로 추가 필요')
        previous = observed


def validate(data):
    fields(data, ('schema_version', 'project', 'stages'), 'record')
    require(type(data['schema_version']) is int and data['schema_version'] == 1,
            'schema_version: 1만 지원')
    text(data['project'], 'project')
    stages = data['stages']
    require(isinstance(stages, list) and bool(stages), 'stages: 실행 순서의 비어 있지 않은 목록 필요')
    ids = set()
    for stage in stages:
        fields(stage, ('id', 'revision', 'configuration', 'configuration_reviews',
                       'result', 'result_reviews'), 'stage')
        for name in ('id', 'revision'):
            text(stage[name], f'stage.{name}')
        label = stage['id']
        require(label not in ids, f'{label}: 중복 단계')
        ids.add(label)
        config = stage['configuration']
        fields(config, ('version', 'agents', 'max_concurrency', 'permissions', 'cost_scope'), label)
        text(config['version'], f'{label}.configuration.version')
        text(config['cost_scope'], f'{label}.configuration.cost_scope')
        strings(config['permissions'], f'{label}.configuration.permissions')
        agents = config['agents']
        require(isinstance(agents, list) and bool(agents), f'{label}: 실제 구성원 목록 필요')
        count = config['max_concurrency']
        require(type(count) is int and 1 <= count <= len(agents), f'{label}: 동시 인원 범위 오류')
        agent_ids = set()
        for agent in agents:
            fields(agent, ('id', 'role', 'model', 'effort', 'ownership'), f'{label}.agent')
            for name in ('id', 'role', 'model', 'effort'):
                text(agent[name], f'{label}.agent.{name}')
            require(agent['id'] not in agent_ids, f'{label}: 중복 구성원')
            agent_ids.add(agent['id'])
            strings(agent['ownership'], f'{label}.agent.ownership')
        validate_reviews(stage['configuration_reviews'], f'{label}.configuration_reviews')
        result = stage['result']
        if result is not None:
            fields(result, ('revision', 'summary', 'artifacts', 'checks', 'limitations'), f'{label}.result')
            for name in ('revision', 'summary'):
                text(result[name], f'{label}.result.{name}')
            for name in ('artifacts', 'checks', 'limitations'):
                strings(result[name], f'{label}.result.{name}', empty=name == 'limitations')
        validate_reviews(stage['result_reviews'], f'{label}.result_reviews', result=True)
    return data


def target(stage, result=False):
    value = {
        'stage_id': stage['id'], 'stage_revision': stage['revision'],
        'configuration_version': stage['configuration']['version'],
        'configuration_digest': digest(stage['configuration']),
    }
    if result:
        require(stage['result'] is not None, f"{stage['id']}: 결과 없음")
        value.update(result_revision=stage['result']['revision'], result_digest=digest(stage['result']))
    return value


def approved(stage, result=False):
    name = 'result_reviews' if result else 'configuration_reviews'
    decision = 'accepted' if result else 'approved'
    reviews = stage[name]
    require(bool(reviews), f"{stage['id']}: {name} 사용자 검토 대기")
    latest = reviews[-1]
    require(latest['decision'] == decision, f"{stage['id']}: 최신 검토가 {latest['decision']}")
    expected = target(stage, result)
    require(all(latest['target'].get(key) == value for key, value in expected.items()),
            f"{stage['id']}: 검토 대상 변경 — 현재 revision·구성·결과로 사용자 재검토 필요")
    return latest


def accepted(stage):
    configuration = approved(stage)
    result = approved(stage, result=True)
    require(stamp(result['source']['at'], 'result.at') >= stamp(configuration['source']['at'], 'configuration.at'),
            f"{stage['id']}: 현재 구성 승인보다 오래된 결과 수용")


def find_stage(data, stage_id):
    for index, stage in enumerate(data['stages']):
        if stage['id'] == stage_id:
            return index, stage
    raise ValueError(f'{stage_id}: 단계 없음')


def check(data, stage_id, action):
    validate(data)
    require(action in ('enter', 'accept'), 'action: enter 또는 accept 필요')
    index, stage = find_stage(data, stage_id)
    for prior in data['stages'][:index]:
        accepted(prior)
    approved(stage)
    if action == 'accept':
        accepted(stage)
    elif stage['result_reviews']:
        require(stage['result_reviews'][-1]['decision'] != 'held',
                f'{stage_id}: 결과 보류 — 사용자 재개 답변 필요')
    return {'status': 'PASS', 'stage': stage_id, 'action': action, **LIMITS}


def template(project, stage_ids):
    return {
        'schema_version': 1, 'project': project,
        'stages': [{
            'id': stage_id, 'revision': 'contract-v1',
            'configuration': {
                'version': 'v1', 'agents': [{
                    'id': 'coordinator', 'role': '조정자', 'model': '미정', 'effort': '미정',
                    'ownership': ['미정 — 실제 파일/책임 범위로 교체'],
                }],
                'max_concurrency': 1, 'permissions': ['미정 — 허용/금지 작업으로 교체'],
                'cost_scope': '미정 — 허용 비용/호출 한도로 교체',
            },
            'configuration_reviews': [], 'result': None, 'result_reviews': [],
        } for stage_id in stage_ids],
    }


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        require(key not in value, f'JSON 중복 키: {key}')
        value[key] = item
    return value


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    create = commands.add_parser('template', help='승인 없는 초안 출력')
    create.add_argument('--project', required=True)
    create.add_argument('--stage', action='append', required=True, help='실행 순서대로 반복 지정')
    for name in ('validate', 'check', 'digest'):
        command = commands.add_parser(name)
        command.add_argument('--file', type=Path, required=True)
        if name != 'validate':
            command.add_argument('--stage', required=True)
        if name == 'check':
            command.add_argument('--action', choices=('enter', 'accept'), required=True)
        if name == 'digest':
            command.add_argument('--target', choices=('configuration', 'result'), required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'template':
            report = validate(template(args.project, args.stage))
            print(LIMITS['notice'], file=sys.stderr)
        else:
            data = validate(json.loads(args.file.read_text(encoding='utf-8'),
                                       object_pairs_hook=unique_object))
            if args.command == 'check':
                report = check(data, args.stage, args.action)
            elif args.command == 'digest':
                _, stage = find_stage(data, args.stage)
                report = {'status': 'PASS', 'target': target(stage, args.target == 'result'), **LIMITS}
            else:
                report = {'status': 'PASS', **LIMITS}
    except (ValueError, OSError) as error:
        report = {'status': 'BLOCKED', 'error': str(error), **LIMITS}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report.get('status') == 'BLOCKED' else 0


if __name__ == '__main__':
    sys.exit(main())
