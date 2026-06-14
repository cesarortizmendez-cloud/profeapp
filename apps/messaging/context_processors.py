def unread_messages_count(request):
    """Inyecta el contador de mensajes no leídos en todos los templates."""
    if request.user.is_authenticated:
        from .models import Message
        count = Message.objects.filter(recipient=request.user, is_read=False).count()
        return {'unread_messages_count': count}
    return {'unread_messages_count': 0}
