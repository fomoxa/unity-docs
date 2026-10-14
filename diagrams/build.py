import argparse
import importlib
import os
import pkgutil
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTPUTS = {
    'en': os.path.join(ROOT, '.gitbook', 'assets', 'diagrams'),
    'vi': os.path.join(ROOT, 'vi', '.gitbook', 'assets', 'diagrams'),
}
EDGE = '/mnt/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'

sys.path.insert(0, HERE)
from registry import DIAGRAMS  # noqa: E402


def load_all():
    for module in pkgutil.iter_modules([HERE]):
        if module.name.startswith('d_'):
            importlib.import_module(module.name)


def render_all(only=None):
    rendered = {}
    for name, function in sorted(DIAGRAMS.items()):
        if only and not re.search(only, name):
            continue
        for language in OUTPUTS:
            rendered[(language, name)] = function(language).svg()
    return rendered


def write(rendered):
    for (language, name), svg in rendered.items():
        os.makedirs(OUTPUTS[language], exist_ok=True)
        path = os.path.join(OUTPUTS[language], name + '.svg')
        if not os.path.exists(path) or open(path, encoding='utf-8').read() != svg:
            with open(path, 'w', encoding='utf-8') as file:
                file.write(svg)
            print('wrote', os.path.relpath(path, ROOT))


def check(rendered):
    stale = []
    for (language, name), svg in rendered.items():
        path = os.path.join(OUTPUTS[language], name + '.svg')
        if not os.path.exists(path) or open(path, encoding='utf-8').read() != svg:
            stale.append(os.path.relpath(path, ROOT))
    for path in stale:
        print('stale', path)
    return not stale


def preview(rendered, folder):
    os.makedirs(folder, exist_ok=True)
    for (language, name), svg in rendered.items():
        width, height = map(int, re.search(r'width="(\d+)" height="(\d+)"', svg).groups())
        source = os.path.join(folder, f'{name}.{language}.html')
        with open(source, 'w', encoding='utf-8') as file:
            file.write(
                '<!doctype html><meta charset="utf-8"><style>html,body{margin:0;background:#fff}'
                'svg{display:block}</style>' + svg
            )
        target = os.path.join(folder, f'{name}.{language}.png')
        subprocess.run(
            [EDGE, '--headless', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=1.5',
             f'--window-size={width},{height}', '--screenshot=' + windows_path(target), 'file:///' + windows_path(source).replace('\\', '/')],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd='/mnt/c',
        )
        print('preview', target)


def windows_path(path):
    return subprocess.run(['wslpath', '-w', path], check=True, capture_output=True, text=True).stdout.strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--only')
    parser.add_argument('--preview')
    args = parser.parse_args()
    load_all()
    rendered = render_all(args.only)
    if args.check:
        sys.exit(0 if check(rendered) else 1)
    write(rendered)
    if args.preview:
        preview(rendered, args.preview)


if __name__ == '__main__':
    main()
