# admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Subject, Task, PlannerTask

class TaskInline(admin.TabularInline):
    model = Task
    extra = 0
    fields = ('title', 'due_date', 'due_time', 'completed')
    can_delete = True
    show_change_link = True

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'color_display', 'task_count', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('name', 'user__username')
    inlines = [TaskInline]
    
    def color_display(self, obj):
        return format_html(
            '<span style="background-color: {}; padding: 5px 15px; border-radius: 3px; color: white;">{}</span>',
            obj.color,
            obj.color
        )
    color_display.short_description = 'Color'
    
    def task_count(self, obj):
        return obj.tasks.count()
    task_count.short_description = 'Tasks'

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'subject_user', 'due_date', 'due_time', 'completed_status', 'is_due_today')
    list_filter = ('completed', 'due_date', 'subject')
    search_fields = ('title', 'notes', 'subject__name')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Task Information', {
            'fields': ('subject', 'title', 'completed')
        }),
        ('Due Information', {
            'fields': ('due_date', 'due_time', 'ideal_time')
        }),
        ('Additional Information', {
            'fields': ('notes', 'created_at')
        }),
    )
    actions = ['mark_completed', 'mark_incomplete']
    
    def subject_user(self, obj):
        return obj.subject.user.username
    subject_user.short_description = 'User'
    
    def completed_status(self, obj):
        if obj.completed:
            return format_html('<span style="color: green; font-weight: bold;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    completed_status.short_description = 'Completed'
    
    def is_due_today(self, obj):
        if obj.is_due_today:
            return format_html('<span style="color: orange; font-weight: bold;">Today</span>')
        return ''
    is_due_today.short_description = 'Due Today'
    
    def mark_completed(self, request, queryset):
        queryset.update(completed=True)
    mark_completed.short_description = "Mark selected tasks as completed"
    
    def mark_incomplete(self, request, queryset):
        queryset.update(completed=False)
    mark_incomplete.short_description = "Mark selected tasks as incomplete"

@admin.register(PlannerTask)
class PlannerTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'due_date', 'due_time', 'duration_display', 'repeat_info', 'completed_status', 'is_due_today')
    list_filter = ('completed', 'due_date', 'repeat_enabled', 'repeat_type', 'user')
    search_fields = ('title', 'notes', 'user__username')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Task Information', {
            'fields': ('user', 'title', 'completed')
        }),
        ('Schedule Information', {
            'fields': ('due_date', 'due_time', 'duration_hours')
        }),
        ('Repeat Settings', {
            'fields': ('repeat_enabled', 'repeat_type', 'repeat_until'),
            'classes': ('collapse',),
        }),
        ('Additional Information', {
            'fields': ('notes', 'created_at')
        }),
    )
    actions = ['mark_completed', 'mark_incomplete', 'disable_repeat']
    
    def duration_display(self, obj):
        if obj.duration_hours:
            hours = int(obj.duration_hours)
            minutes = int((obj.duration_hours - hours) * 60)
            return f"{hours}h {minutes}m"
        return "-"
    duration_display.short_description = 'Duration'
    
    def repeat_info(self, obj):
        if not obj.repeat_enabled:
            return '-'
        
        info = f"{obj.get_repeat_type_display()}"
        if obj.repeat_until:
            info += f" until {obj.repeat_until}"
        return info
    repeat_info.short_description = 'Repeats'
    
    def completed_status(self, obj):
        if obj.completed:
            return format_html('<span style="color: green; font-weight: bold;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    completed_status.short_description = 'Completed'
    
    def is_due_today(self, obj):
        if obj.is_due_today:
            return format_html('<span style="color: orange; font-weight: bold;">Today</span>')
        return ''
    is_due_today.short_description = 'Due Today'
    
    def mark_completed(self, request, queryset):
        queryset.update(completed=True)
    mark_completed.short_description = "Mark selected tasks as completed"
    
    def mark_incomplete(self, request, queryset):
        queryset.update(completed=False)
    mark_incomplete.short_description = "Mark selected tasks as incomplete"
    
    def disable_repeat(self, request, queryset):
        queryset.update(repeat_enabled=False)
    disable_repeat.short_description = "Disable repeating for selected tasks"

# Customize the admin site title and header
admin.site.site_header = "Calendar App Administration"
admin.site.site_title = "Calendar App Admin Portal"
admin.site.index_title = "Welcome to Calendar App Admin Panel"