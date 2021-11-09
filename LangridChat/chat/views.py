import string, random
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from chat.models import Room
from langrid.TranslationClient import SupportLanguages
import csv
import time
from django.db.models.base import ObjectDoesNotExist


def index(request):
    return render(request, 'chat/index.html', {})


def support_languages(request):
    """
    :return: '{ja: "日本語", zh: "简体中文", en: "English", es: "Español"}'
    """
    return JsonResponse(SupportLanguages)


@csrf_exempt
def room(request, room_name='aaa'):
    if request.method == "GET":
        get_object_or_404(Room, room=room_name)
        return JsonResponse({'room': room_name})
    elif request.method == 'POST':
        is_exist = True
        room_name = ''.join(random.sample(string.ascii_letters + string.digits, 13))
        while is_exist:
            room_instance, is_exist = Room.objects.get_or_create(room=room_name)
        return JsonResponse({'room': room_name})
    return HttpResponse(status=404)


def csv_download(request, room_name=''):
    if not room_name:
        return render(request, 'chat/csv_download.html', {})
    # Create the HttpResponse object with the appropriate CSV header.
    now_time = time.strftime('%Y_%m_%d_%H_%M', time.localtime(time.time()))
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{room_name}_{now_time}.csv"'

    languages = list(SupportLanguages.keys())
    writer = csv.writer(response)
    writer.writerow(['Create Time', 'Sender', 'language', 'source message'] + languages)
    messages = get_object_or_404(Room, room=room_name).messages_received.all()
    for message in messages:
        row = [message.created_time, message.sender.name, message.language, message.message]
        for language in languages:
            if language == message.language:
                row.append(message.message)
                continue
            try:
                row.append(message.translatemessage_set.get(language=language).message)
            except ObjectDoesNotExist:
                row.append('null')
        writer.writerow(row)
    return response
