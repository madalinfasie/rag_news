from chatpage.forms import ChatForm
from chatpage.services import llm
from django.shortcuts import render, redirect
from django.views import View


class ChatView(View):
    def get(self, request):
        form = ChatForm()
        return render(
            request,
            "chatpage/chat.html",
            context={
                "form": form,
                "chat_history": request.session.get("chat_history", []),
            },
        )

    def post(self, request):
        form = ChatForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data["query"]
            answer = llm.ask(query)

            history = request.session.get("chat_history", [])
            history.append({"role": "user", "text": query})
            history.append({"role": "assistant", "text": answer})

            request.session["chat_history"] = history
            return redirect("query")

        return render(
            request,
            "chatpage/chat.html",
            {"form": form, "chat_history": request.session.get("chat_history", [])},
        )
