import json, os
from flask import g, session, request, current_app

def setup_i18n(app):
    @app.before_request
    def set_language():
        # هەڵبژاردنی زمان: لە کاربەر > لە سێشن > دیفۆڵت ku
        if hasattr(g, 'user') and getattr(g, 'user', None) and g.user.is_authenticated:
            g.lang = g.user.preferred_language
        else:
            g.lang = request.args.get('lang', session.get('lang', 'ku'))
        session['lang'] = g.lang

        # بارکردنی فایلەکانی وەرگێڕان
        path = os.path.join(current_app.config['TRANSLATION_FOLDER'], f'{g.lang}.json')
        g.translations = {}
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                g.translations = json.load(f)

    @app.context_processor
    def inject_translations():
        return {'t': lambda key: g.translations.get(key, key), 'current_lang': g.lang}
