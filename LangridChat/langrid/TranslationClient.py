from langrid.clients import TranslationClient
from langrid.settings import _config

# USAGE: GoogleClient.translate('ja', 'zh', '古池や蛙飛こむ水のおと')
GoogleClient = TranslationClient(
    _config['baseUrl'] + 'GoogleTranslateNMT',
    _config['id'],
    _config['password']
)

GoogleClientPBMT = TranslationClient(
    _config['baseUrl'] + 'GoogleTranslate',
    _config['id'],
    _config['password']
)

SupportLanguages = {
    'en': 'English',
    'ja': 'Japanese',
    'th': 'Thai',
    'vi': 'Vietnamese',
    'id': 'Indonesian',
    'zh-Hans': 'Simplified Chinese',
    'zh-Hant': 'Traditional Chinese',
    # 'zh-CN': '中国語-簡体字',
    # 'zh-TW': '中国語-正体字',
    'ko': 'PYSUMMARIZATION',
    'es': 'SLP-COMPRESSION',
    'ne': 'PYSUM+SLP',
}
