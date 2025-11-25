from chatpage.forms import ChatForm
from chatpage.services import llm
from django.shortcuts import render
from django.views import View

chat_history = []


class ChatView(View):
    def get(self, request):
        form = ChatForm()
        return render(
            request,
            "chatpage/chat.html",
            context={"form": form, "chat_history": chat_history},
        )

    def post(self, request):
        form = ChatForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data["query"]
            answer = llm.ask(query)
            chat_history.append({"role": "user", "text": query})
            chat_history.append({"role": "assistant", "text": answer})

            return render(
                request,
                "chatpage/chat.html",
                {"form": form, "chat_history": chat_history},
            )

        return render(
            request,
            "chatpage/chat.html",
            {"form": form, "chat_history": chat_history},
        )
