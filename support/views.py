import base64
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Appeal, AppealPicture, AppealStatus
from django.utils.timezone import now


@login_required
def support(request):
    if request.user.role == 'support':
        return redirect('appeals')
    if request.method == "POST":
        text = request.POST.get("message", "").strip()

        if not text:
            return render(request, 'support/support.html', {"message": "Сообщение не может быть пустым"})

        # Создаём объект обращения
        appeal = Appeal.objects.create(user=request.user, text=text)

        # Обрабатываем загруженные файлы
        files = request.FILES.getlist("file")  # Получаем список загруженных файлов

        for file in files:
            if file.content_type == "image/jpeg":  # Проверяем, что файл - JPG
                image_data = base64.b64encode(file.read()).decode('utf-8')  # Кодируем в Base64
                AppealPicture.objects.create(appeal=appeal, image_base64=image_data)

        return render(request, 'support/support.html', {'message': 'Ваше обращение успешно получено, наш менеджер '
                                                                   'свяжется с вами в ближайшее время!'})

    return render(request, 'support/support.html')


@login_required
def show_appeals(request):
    # Получаем все обращения вместе с картинками
    appeals = Appeal.objects.filter(closed=False).order_by('-last_answered_at')

    # Передаем их в контекст
    return render(request, 'support/appeals.html', {'appeals': appeals})


@login_required()
def work_with_appeal(request, appeal_id):
    appeal = get_object_or_404(Appeal, id=appeal_id)
    user = appeal.user
    pictures = appeal.pictures.all()
    statuses = appeal.appeal_status.all()

    if request.method == "POST":
        # Обработка закрытия обращения
        if 'close_appeal' in request.POST:
            appeal.closed = True
            appeal.save()
            AppealStatus.objects.create(
                appeal=appeal,
                comment="Обращение закрыто"
            )
            return redirect('appeals')

        comment = request.POST.get("comment")  # Получаем текст комментария из формы
        if comment:
            AppealStatus.objects.create(appeal=appeal, comment=comment)
            appeal.last_answered_at = now()
            appeal.save(update_fields=['last_answered_at'])
            return redirect("work_with_appeal", appeal_id=appeal.id)  # Перенаправляем на ту же страницу

    context = {
        'appeal': appeal,
        'user': user,
        'pictures': pictures,
        'statuses': statuses
    }
    return render(request, 'support/work_with_appeal.html', context)
