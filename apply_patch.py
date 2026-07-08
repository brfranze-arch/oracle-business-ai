from pathlib import Path
import shutil

ROOT = Path.cwd()
PATCH = Path(__file__).resolve().parent


def copy_add(src_rel, dst_rel):
    src = PATCH / 'ADD' / src_rel
    dst = ROOT / dst_rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f'ADD/UPDATE {dst_rel}')


def ensure_text(path_rel, marker, insert_text, after_marker=None):
    path = ROOT / path_rel
    text = path.read_text(encoding='utf-8')
    if marker in text:
        print(f'OK {path_rel}: already contains {marker}')
        return
    if after_marker and after_marker in text:
        text = text.replace(after_marker, after_marker + insert_text, 1)
    else:
        text += insert_text
    path.write_text(text, encoding='utf-8')
    print(f'PATCH {path_rel}: inserted {marker}')


def patch_main():
    path_rel = 'backend/main.py'
    path = ROOT / path_rel
    text = path.read_text(encoding='utf-8')

    import_line = 'from routers.digital_twin_router import router as digital_twin_router\n'
    if import_line not in text:
        if 'from routers.openai_router import router as openai_router\n' in text:
            text = text.replace(
                'from routers.openai_router import router as openai_router\n',
                'from routers.openai_router import router as openai_router\n' + import_line,
                1,
            )
        else:
            text = import_line + text
        print('PATCH backend/main.py: digital_twin_router import')
    else:
        print('OK backend/main.py: digital_twin_router import exists')

    include_line = 'app.include_router(digital_twin_router)\n'
    if include_line not in text:
        if 'app.include_router(openai_router)\n' in text:
            text = text.replace(
                'app.include_router(openai_router)\n',
                'app.include_router(openai_router)\n' + include_line,
                1,
            )
        else:
            marker = 'app = FastAPI(title="Oracle Business AI")\n'
            text = text.replace(marker, marker + include_line, 1)
        print('PATCH backend/main.py: include digital_twin_router')
    else:
        print('OK backend/main.py: include digital_twin_router exists')

    path.write_text(text, encoding='utf-8')


def patch_create_tables():
    ensure_text(
        'backend/create_tables.py',
        'import digital_twin_models',
        '\nimport digital_twin_models\n',
        after_marker='import openai_models\n' if (ROOT/'backend/create_tables.py').read_text(encoding='utf-8').find('import openai_models\n') != -1 else None,
    )


def patch_index():
    path_rel = 'frontend/index.html'
    path = ROOT / path_rel
    text = path.read_text(encoding='utf-8')
    script = '<script src="js/digital_twin.js"></script>'
    if script in text:
        print('OK frontend/index.html: digital_twin.js script exists')
        return
    if '<script src="js/reports.js"></script>' in text:
        text = text.replace('<script src="js/reports.js"></script>', script + '\n<script src="js/reports.js"></script>', 1)
    else:
        text = text.replace('</body>', f'  {script}\n</body>', 1)
    path.write_text(text, encoding='utf-8')
    print('PATCH frontend/index.html: added digital_twin.js script')


def patch_reports():
    path_rel = 'frontend/js/reports.js'
    path = ROOT / path_rel
    text = path.read_text(encoding='utf-8')
    if 'runDigitalTwin()' in text:
        print('OK frontend/js/reports.js: Digital Twin buttons exist')
        return
    anchor = '<button onclick="loadAgentsHistory()">Storico Agents</button>'
    addition = anchor + '\n            <button onclick="runDigitalTwin()">Digital Twin</button>\n            <button onclick="loadDigitalTwinHistory()">Storico Digital Twin</button>'
    if anchor in text:
        text = text.replace(anchor, addition, 1)
    else:
        anchor2 = '<button onclick="loadRevenueAnalyticsReport()">Revenue Analytics</button>'
        text = text.replace(anchor2, anchor2 + '\n            <button onclick="runDigitalTwin()">Digital Twin</button>\n            <button onclick="loadDigitalTwinHistory()">Storico Digital Twin</button>', 1)
    path.write_text(text, encoding='utf-8')
    print('PATCH frontend/js/reports.js: added Digital Twin buttons')


def main():
    copy_add('backend/digital_twin_models.py', 'backend/digital_twin_models.py')
    copy_add('backend/digital_twin_engine.py', 'backend/digital_twin_engine.py')
    copy_add('backend/routers/digital_twin_router.py', 'backend/routers/digital_twin_router.py')
    copy_add('frontend/js/digital_twin.js', 'frontend/js/digital_twin.js')
    patch_create_tables()
    patch_main()
    patch_index()
    patch_reports()
    print('\nPatch 02 applicata. Ora esegui: cd backend; python create_tables.py; uvicorn main:app --reload')

if __name__ == '__main__':
    main()
