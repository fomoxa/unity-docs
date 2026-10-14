import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINK = re.compile(r'\]\(([^)\s]+)\)')
IMAGE = re.compile(r'<img[^>]+src="([^"]+)"')
FENCE = re.compile(r'```.*?```', re.S)
HEADING = re.compile(r'^(#{1,6}) (.*)$', re.M)
ANCHOR_ID = re.compile(r'id="([^"]+)"')


def slug(heading):
    text = re.sub(r'<a [^>]*></a>', '', heading).strip().lower()
    text = re.sub(r'[`*_]', '', text)
    text = re.sub(r'[^\w\- ]', '', text)
    return text.replace(' ', '-')


def pages(space):
    base = os.path.join(ROOT, space)
    for folder, folders, files in os.walk(base):
        folders[:] = [name for name in folders if not name.startswith('.') and name not in ('tools', 'diagrams')
                      and not (space == '' and name == 'vi' and folder == base)]
        for name in files:
            if name.endswith('.md'):
                yield os.path.relpath(os.path.join(folder, name), base)


def without_code(text):
    return FENCE.sub('', text)


def anchors(path, cache={}):
    if path not in cache:
        text = without_code(open(path, encoding='utf-8').read())
        found = set()
        for _, heading in HEADING.findall(text):
            found.add(slug(heading))
            found.update(ANCHOR_ID.findall(heading))
        cache[path] = found
    return cache[path]


def check_links(problems):
    for space in ('', 'vi'):
        base = os.path.join(ROOT, space)
        for page in pages(space):
            path = os.path.join(base, page)
            text = without_code(open(path, encoding='utf-8').read())
            for target in LINK.findall(text) + IMAGE.findall(text):
                if re.match(r'[a-z]+:', target):
                    continue
                file_part, _, anchor = target.partition('#')
                full = os.path.normpath(os.path.join(os.path.dirname(path), file_part)) if file_part else path
                if not full.startswith(base if space else ROOT):
                    problems.append(f'{space}/{page}: {target} leaves the space')
                elif not os.path.exists(full):
                    problems.append(f'{space}/{page}: missing {target}')
                elif anchor and full.endswith('.md') and anchor not in anchors(full):
                    problems.append(f'{space}/{page}: no anchor {target}')


def check_summary(problems):
    for space in ('', 'vi'):
        base = os.path.join(ROOT, space)
        listed = set(LINK.findall(open(os.path.join(base, 'SUMMARY.md'), encoding='utf-8').read()))
        for page in pages(space):
            if page not in listed and page not in ('SUMMARY.md', 'DOCUMENTATION-TODO.md') and os.path.join(base, page) != os.path.join(base, 'README.md'):
                problems.append(f'{space or "en"}: {page} is not in SUMMARY.md')


def check_parity(problems):
    english = set(pages(''))
    vietnamese = set(pages('vi'))
    for page in sorted(english - vietnamese - {'DOCUMENTATION-TODO.md'}):
        problems.append(f'vi: {page} has no translation')
    for page in sorted(vietnamese - english):
        problems.append(f'vi: {page} has no English page')
    for page in sorted((english & vietnamese) - {'SUMMARY.md'}):
        en = open(os.path.join(ROOT, page), encoding='utf-8').read()
        vi = open(os.path.join(ROOT, 'vi', page), encoding='utf-8').read()
        en_code = [block for block in FENCE.findall(en) if not block.startswith('```mermaid')]
        vi_code = [block for block in FENCE.findall(vi) if not block.startswith('```mermaid')]
        if en_code != vi_code:
            problems.append(f'vi/{page}: code blocks differ from the English page')
        if len(FENCE.findall(en)) != len(FENCE.findall(vi)):
            problems.append(f'vi/{page}: a different number of code and diagram blocks')
        en_headings = [(level, slug(text)) for level, text in HEADING.findall(without_code(en))]
        vi_headings = HEADING.findall(without_code(vi))
        if len(en_headings) != len(vi_headings):
            problems.append(f'vi/{page}: {len(vi_headings)} headings, English has {len(en_headings)}')
        else:
            for (level, english_slug), (vi_level, text) in zip(en_headings[1:], vi_headings[1:]):
                ids = ANCHOR_ID.findall(text)
                if level != vi_level or english_slug not in ids:
                    problems.append(f'vi/{page}: heading "{text[:40]}" needs level {level} and id "{english_slug}"')
        en_images = [os.path.basename(src) for src in IMAGE.findall(en)]
        vi_images = [os.path.basename(src) for src in IMAGE.findall(vi)]
        if en_images != vi_images:
            problems.append(f'vi/{page}: images differ from the English page')


def check_diagrams(problems):
    result = subprocess.run([sys.executable, os.path.join(ROOT, 'diagrams', 'build.py'), '--check'],
                            capture_output=True, text=True)
    if result.returncode != 0:
        problems.extend('diagrams: ' + line for line in result.stdout.splitlines())


def main():
    problems = []
    check_links(problems)
    check_summary(problems)
    check_parity(problems)
    check_diagrams(problems)
    for problem in problems:
        print(problem)
    print(f'{len(problems)} problems')
    sys.exit(1 if problems else 0)


if __name__ == '__main__':
    main()
