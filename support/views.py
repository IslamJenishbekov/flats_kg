import base64
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Appeal, AppealPicture


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
    appeals = Appeal.objects.filter(closed=False).order_by('-created_at')

    # Передаем их в контекст
    return render(request, 'support/appeals.html', {'appeals': appeals})
