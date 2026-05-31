from django.shortcuts import render, redirect

from .models import ChatMessage


def support_chat(request):

    if request.method == 'POST':

        message = request.POST.get('message')

        ChatMessage.objects.create(

            user=request.user,

            message=message
        )

        return redirect('support_chat')

    messages = ChatMessage.objects.all().order_by('created_at')

    return render(request,

                  'chat/chat.html',

                  {
                      'messages': messages
                  })