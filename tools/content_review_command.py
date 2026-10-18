"""Apply, resume, or inspect a local authoring review; never publish lesson files."""
import argparse
import json
from pathlib import Path
import subprocess
import sqlite3
import sys

from content_review import Artifact, ContentTree, ReviewLedger
from content_review_model import JsonReviewModel


def read_json(path):
    if path.stat().st_size > 4_000_000:
        raise ValueError('입력 파일이 너무 커요.')
    return json.loads(path.read_text(encoding='utf-8'))


def load_model(path):
    config = read_json(path)
    if (not isinstance(config, dict) or not {'command', 'model_revision'} <= set(config)
            or set(config) - {'command', 'model_revision', 'timeout', 'prd', 'target_steps'}):
        raise ValueError('모델 설정 필드를 확인하세요.')
    if 'prd' in config:
        config['prd'] = read_json(path.parent / config['prd'])
    return JsonReviewModel(**config)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ['apply', 'resume']:
        command = commands.add_parser(name)
        command.add_argument('--state', type=Path, required=True)
        command.add_argument('--ledger', type=Path, required=True)
        command.add_argument('--model-config', type=Path, required=True)
        if name == 'apply':
            command.add_argument('--replacement', type=Path, required=True)
    history = commands.add_parser('history')
    history.add_argument('--ledger', type=Path, required=True)
    history.add_argument('--target', required=True)
    args = parser.parse_args()
    try:
        if args.command == 'history':
            if not args.ledger.is_file():
                raise ValueError('검토 이력 파일이 없어요.')
            with ReviewLedger(args.ledger) as ledger:
                result = dict(reviews=ledger.history(args.target), generations=ledger.generation_history(args.target))
        else:
            tree = ContentTree.load(args.state)
            model = load_model(args.model_config)
            with ReviewLedger(args.ledger) as ledger:
                options = dict(assessor_key=model.identity, generator_key=model.identity,
                               before_generate=model.authorize_lineage)
                if args.command == 'apply':
                    value = read_json(args.replacement)
                    if not isinstance(value, dict) or set(value) != {'key', 'layer', 'text'}:
                        raise ValueError('변경할 원문의 코드·레이어·내용을 확인하세요.')
                    tree.apply(Artifact(**value), ledger, model.assess, model.generate, **options)
                else:
                    tree.resume(ledger, model.assess, model.generate, **options)
            result = dict(status='completed')
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, KeyError, TypeError, RuntimeError, sqlite3.Error):
        print('검토를 마치지 못했어요. 입력·모델 설정과 검토 이력을 확인하세요.', file=sys.stderr)
        return 1
    except subprocess.TimeoutExpired:
        print('모델 호출 시간이 초과됐어요. 저장된 검토 상태에서 다시 시작하세요.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
