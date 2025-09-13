from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, ActivityLog

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_active', 'created_at')
    list_filter = ('is_active', 'is_staff', 'created_at')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-created_at',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {
            'fields': ('phone', 'created_at', 'updated_at')
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'ip_address', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__email', 'action', 'description')
    ordering = ('-timestamp',)
    readonly_fields = ('timestamp',)