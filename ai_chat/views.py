import json
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST, require_GET
from .tools import TOOL_SPECS, require_user, can_read
from .lmstudio import answer, ModelError

class FamilyLoginView(LoginView):
    template_name = 'ai_chat/login.html'
    redirect_authenticated_user = True

@require_GET
def home(request):
    if not request.user.is_authenticated:
        return redirect('login')
    require_user(request.user)
    return render(request, 'ai_chat/chat.html', {'verticals': [v for v in ('jardinagem', 'limpeza_predial') if can_read(request.user, v)]})

@require_GET
def catalog(request):
    require_user(request.user)
    return JsonResponse({'tools': TOOL_SPECS})

@require_POST
def ask(request):
    try:
        require_user(request.user)
        if len(request.body) > 60000:
            raise ValidationError('Mensagem muito grande.')
        payload = json.loads(request.body)
        question, history = payload.get('pergunta'), payload.get('historico', [])
        if not isinstance(question, str) or not question.strip() or len(question) > 4000:
            raise ValidationError('Pergunta deve ter de 1 a 4000 caracteres.')
        if not isinstance(history, list) or len(history) > 20 or any(not isinstance(m, dict) or
            set(m) != {'role', 'content'} or m['role'] not in ('user', 'assistant') or
            not isinstance(m['content'], str) or len(m['content']) > 8000 for m in history):
            raise ValidationError('Histórico inválido.')
        return JsonResponse(answer(request.user, question.strip(), history), json_dumps_params={'ensure_ascii': False})
    except PermissionDenied as exc:
        return JsonResponse({'erro': str(exc)}, status=403)
    except (ValidationError, ValueError, TypeError, AttributeError) as exc:
        return JsonResponse({'erro': '; '.join(exc.messages) if isinstance(exc, ValidationError) else 'Solicitação inválida.'}, status=400)
    except ModelError as exc:
        return JsonResponse({'erro': str(exc)}, status=502)
