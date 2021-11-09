from django.contrib import admin
from django.db.models.base import ObjectDoesNotExist
from ...models import TranslateMessage


class TranslateMessageInline(admin.TabularInline):
    model = TranslateMessage
    extra = 4  # 显示多少条


class MessageAdmin(admin.ModelAdmin):
    list_display = (
        'created_time', 'room', 'sender', 'language', 'ja_message', 'zh_message', 'en_message', 'es_message',
        'th_message')

    # 筛选器
    list_filter = ('room', 'sender', 'language')  # 过滤器
    search_fields = ('message', 'show_all_translate_message')  # 搜索字段
    date_hierarchy = 'created_time'  # 详细时间分层筛选

    filter_horizontal = ('addressees',)
    fieldsets = (
        ("Info", {'fields': ['sender', 'language', 'message']}),
        ("受信者", {'fields': ['addressees', ]}),
    )
    inlines = (TranslateMessageInline,)

    @staticmethod
    def ja_message(obj):
        try:
            return obj.translatemessage_set.get(language='ja').message
        except ObjectDoesNotExist:
            return obj.message

    @staticmethod
    def zh_message(obj):
        try:
            return obj.translatemessage_set.get(language='zh').message
        except ObjectDoesNotExist:
            return obj.message

    @staticmethod
    def en_message(obj):
        try:
            return obj.translatemessage_set.get(language='en').message
        except ObjectDoesNotExist:
            return obj.message

    @staticmethod
    def es_message(obj):
        try:
            return obj.translatemessage_set.get(language='es').message
        except ObjectDoesNotExist:
            return obj.message

    @staticmethod
    def th_message(obj):
        try:
            return obj.translatemessage_set.get(language='th').message
        except ObjectDoesNotExist:
            return obj.message
