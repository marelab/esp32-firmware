import os
import sys
import shutil
import subprocess
from base64 import b64encode

import argparse

JS_ANALYZE = False

BUILD_DIR = 'build'

HTML_MINIFIER_TERSER_OPTIONS = [
    '--collapse-boolean-attributes',
    '--collapse-inline-tag-whitespace',
    '--collapse-whitespace',
    '--conservative-collapse',
    '--decode-entities',
    '--no-include-auto-generated-tags',
    '--minify-urls',
    '--prevent-attributes-escaping',
    '--process-conditional-comments',
    '--remove-attribute-quotes',
    '--remove-comments',
    '--remove-empty-attributes',
    '--remove-optional-tags',
    '--remove-redundant-attributes',
    '--remove-script-type-attributes',
    '--remove-style-link-type-attributes',
    '--sort-attributes',
    '--sort-class-name',
    '--trim-custom-fragments',
    '--use-short-doctype'
]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--js-source-map', action='store_true')
    parser.add_argument('--css-source-map', action='store_true')
    build_args = parser.parse_args()

    try:
        shutil.rmtree(BUILD_DIR)
    except FileNotFoundError:
        pass

    os.makedirs(BUILD_DIR)

    print('tsc...')
    subprocess.check_call([
        'npx',
        'tsc',
        '--build',
        'tsconfig.json'
    ], shell=sys.platform == 'win32')

    print('esbuild...')
    args = [
        'npx',
        'esbuild',
        'src/main.ts',
        '--bundle',
        '--minify',
        '--outfile={0}'.format(os.path.join(BUILD_DIR, 'bundle.min.js'))
    ]

    if JS_ANALYZE:
        args += ['--analyze']

    if build_args.js_source_map:
        args += ['--sourcemap']

    subprocess.check_call(args, shell=sys.platform == 'win32')

    if build_args.js_source_map:
        with open(os.path.join(BUILD_DIR, 'bundle.min.js'), 'r', encoding='utf-8') as f:
            js_src = f.read()

        with open(os.path.join(BUILD_DIR, 'bundle.min.js.map'), 'rb') as f:
            js_map = b64encode(f.read()).decode('ascii')

        os.remove(os.path.join(BUILD_DIR, 'bundle.min.js.map'))

        js_src = js_src.replace('sourceMappingURL=bundle.min.js.map', 'sourceMappingURL=data:text/json;base64,{0}'.format(js_map))

        with open(os.path.join(BUILD_DIR, 'bundle.min.js'), 'w', encoding='utf-8') as f:
            f.write(js_src)

    print('sass...')
    args = [
        'npx',
        'sass',
    ]

    if not build_args.css_source_map:
        args += ['--no-source-map']

    args += [
        'src/main.scss',
        os.path.join(BUILD_DIR, 'main.css')
    ]

    subprocess.check_call(args, shell=sys.platform == 'win32')

    print('update-browserslist-db...')
    subprocess.check_call([
        'npx',
        'update-browserslist-db'
    ], shell=sys.platform == 'win32')

    print('postcss...')
    subprocess.check_call([
        'npx',
        'postcss',
        os.path.join(BUILD_DIR, 'main.css'),
        '-o',
        os.path.join(BUILD_DIR, 'main.min.css')
    ], shell=sys.platform == 'win32')

    if build_args.css_source_map:
        with open(os.path.join(BUILD_DIR, 'main.min.css'), 'r') as f:
            css_src = f.read()

        with open(os.path.join(BUILD_DIR, 'main.min.css.map'), 'rb') as f:
            css_map = b64encode(f.read()).decode('ascii')

        os.remove(os.path.join(BUILD_DIR, 'main.min.css.map'))

        css_src = css_src.replace('sourceMappingURL=main.min.css.map', 'sourceMappingURL=data:text/json;base64,{0}'.format(css_map))

        with open(os.path.join(BUILD_DIR, 'main.min.css'), 'w') as f:
            f.write(css_src)

    print('html-minifier-terser...')
    subprocess.check_call([
        'npx',
        'html-minifier-terser'] +
        HTML_MINIFIER_TERSER_OPTIONS + [
        '-o',
        os.path.join(BUILD_DIR, 'index.min.html'),
        'src/index.html'
    ], shell=sys.platform == 'win32')

if __name__ == '__main__':
    main()
