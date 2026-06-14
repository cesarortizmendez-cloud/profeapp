from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404

from apps.courses.models import Course, Enrollment
from .models import Material


@login_required
def material_list(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    
    if request.user.is_professor:
        if course.professor != request.user:
            raise Http404
        materials = Material.objects.filter(course=course)
    else:
        get_object_or_404(Enrollment, course=course, student=request.user, is_active=True)
        materials = Material.objects.filter(course=course, is_visible=True)

    context = {'course': course, 'materials': materials}
    return render(request, 'materials/list.html', context)


@login_required
def material_upload(request, course_id):
    course = get_object_or_404(Course, pk=course_id, professor=request.user)
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        if not title:
            messages.error(request, 'El título es requerido.')
            return redirect('materials:list', course_id=course_id)
        
        Material.objects.create(
            course=course,
            uploaded_by=request.user,
            title=title,
            description=request.POST.get('description', ''),
            material_type=request.POST.get('material_type', 'document'),
            file=request.FILES.get('file'),
            url=request.POST.get('url', ''),
            is_visible=request.POST.get('is_visible') == 'on',
        )
        messages.success(request, f'Material "{title}" agregado correctamente.')
    
    return redirect('materials:list', course_id=course_id)


@login_required
def material_delete(request, material_id):
    material = get_object_or_404(Material, pk=material_id, course__professor=request.user)
    course_id = material.course_id
    material.file.delete(save=False)
    material.delete()
    messages.success(request, 'Material eliminado.')
    return redirect('materials:list', course_id=course_id)


@login_required
def material_toggle_visibility(request, material_id):
    material = get_object_or_404(Material, pk=material_id, course__professor=request.user)
    material.is_visible = not material.is_visible
    material.save(update_fields=['is_visible'])
    return redirect('materials:list', course_id=material.course_id)
