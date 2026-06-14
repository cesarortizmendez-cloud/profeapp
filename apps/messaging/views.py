from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from apps.courses.models import Course, Enrollment
from apps.accounts.models import User
from .models import Message, Announcement


@login_required
def inbox(request):
    """Bandeja de entrada."""
    msgs = Message.objects.filter(recipient=request.user).select_related('sender', 'course')
    return render(request, 'messaging/inbox.html', {'messages_list': msgs})


@login_required
def sent(request):
    """Mensajes enviados."""
    msgs = Message.objects.filter(sender=request.user).select_related('recipient', 'course')
    return render(request, 'messaging/sent.html', {'messages_list': msgs})


@login_required
def message_detail(request, message_id):
    """Ver un mensaje."""
    msg = get_object_or_404(
        Message,
        Q(recipient=request.user) | Q(sender=request.user),
        pk=message_id,
    )
    if msg.recipient == request.user and not msg.is_read:
        msg.is_read = True
        msg.save(update_fields=['is_read'])
    
    replies = msg.replies.all().select_related('sender')
    return render(request, 'messaging/detail.html', {'msg': msg, 'replies': replies})


@login_required
def compose(request):
    """Redactar un mensaje nuevo."""
    # Determinar destinatarios disponibles
    if request.user.is_professor:
        # Profesor puede escribir a sus alumnos
        from apps.courses.models import Enrollment
        student_ids = Enrollment.objects.filter(
            course__professor=request.user
        ).values_list('student_id', flat=True)
        recipients = User.objects.filter(id__in=student_ids, is_active=True)
        courses = Course.objects.filter(professor=request.user, is_active=True)
    else:
        # Alumno solo puede escribir a sus profesores
        prof_ids = Course.objects.filter(
            enrollments__student=request.user,
            enrollments__is_active=True,
        ).values_list('professor_id', flat=True)
        recipients = User.objects.filter(id__in=prof_ids, is_active=True)
        courses = Course.objects.filter(
            enrollments__student=request.user,
            enrollments__is_active=True,
        )

    if request.method == 'POST':
        recipient_id = request.POST.get('recipient')
        subject = request.POST.get('subject', '').strip()
        body = request.POST.get('body', '').strip()
        course_id = request.POST.get('course') or None

        if not recipient_id or not subject or not body:
            messages.error(request, 'Completa todos los campos.')
        else:
            recipient = get_object_or_404(User, pk=recipient_id)
            course = Course.objects.filter(pk=course_id).first() if course_id else None
            Message.objects.create(
                sender=request.user,
                recipient=recipient,
                subject=subject,
                body=body,
                course=course,
            )
            messages.success(request, f'Mensaje enviado a {recipient.get_full_name()}.')
            return redirect('messaging:inbox')

    # Pre-seleccionar destinatario desde query param
    pre_recipient = request.GET.get('to')
    pre_course = request.GET.get('course')

    context = {
        'recipients': recipients,
        'courses': courses,
        'pre_recipient': pre_recipient,
        'pre_course': pre_course,
    }
    return render(request, 'messaging/compose.html', context)


@login_required
def reply(request, message_id):
    """Responder un mensaje."""
    original = get_object_or_404(
        Message,
        Q(recipient=request.user) | Q(sender=request.user),
        pk=message_id,
    )

    if request.method == 'POST':
        body = request.POST.get('body', '').strip()
        if body:
            recipient = original.sender if original.recipient == request.user else original.recipient
            Message.objects.create(
                sender=request.user,
                recipient=recipient,
                subject=f'Re: {original.subject}',
                body=body,
                course=original.course,
                parent=original,
            )
            messages.success(request, 'Respuesta enviada.')
        return redirect('messaging:detail', message_id=message_id)

    return redirect('messaging:detail', message_id=message_id)


@login_required
def announcements(request, course_id):
    """Anuncios de un curso."""
    course = get_object_or_404(Course, pk=course_id)
    
    if request.user.is_professor and course.professor != request.user:
        messages.error(request, 'No tienes acceso.')
        return redirect('dashboard:home')
    if request.user.is_student:
        get_object_or_404(Enrollment, course=course, student=request.user, is_active=True)

    if request.method == 'POST' and request.user.is_professor:
        title = request.POST.get('title', '').strip()
        body = request.POST.get('body', '').strip()
        is_pinned = request.POST.get('is_pinned') == 'on'
        if title and body:
            Announcement.objects.create(
                course=course,
                author=request.user,
                title=title,
                body=body,
                is_pinned=is_pinned,
            )
            messages.success(request, 'Anuncio publicado.')
        return redirect('messaging:announcements', course_id=course_id)

    announcement_list = Announcement.objects.filter(course=course)
    return render(request, 'messaging/announcements.html', {
        'course': course,
        'announcements': announcement_list,
    })


@login_required
def announcement_delete(request, announcement_id):
    ann = get_object_or_404(Announcement, pk=announcement_id, course__professor=request.user)
    course_id = ann.course_id
    ann.delete()
    messages.success(request, 'Anuncio eliminado.')
    return redirect('messaging:announcements', course_id=course_id)
