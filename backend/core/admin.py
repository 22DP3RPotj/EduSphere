# from django.contrib import admin
# from .models import User, Room, Topic, Message

# class UserAdmin(admin.ModelAdmin):
#     list_display = ('name', 'username', 'email', 'bio', 'is_staff', 'is_active', 'last_login')
#     list_editable = ('is_staff', 'is_active')
#     list_filter = ('is_staff', 'is_active')
#     search_fields = ('name', 'username', 'email')
    
#     readonly_fields = ('username', 'email', 'password', 'avatar', 'last_login')
    
#     list_per_page = 25


# class RoomAdmin(admin.ModelAdmin):
#     list_display = ('name', 'topic__name', 'description')
#     list_editable = ('description',)
#     search_fields = ('name', 'topic__name', 'description')
    
#     readonly_fields = ('name', 'host')
    
#     list_per_page = 25

    
# class TopicAdmin(admin.ModelAdmin):
#     list_display = ('name',)
#     search_fields = ('name',)
    
#     readonly_fields = ('name',)
    
#     list_per_page = 25

    
# class MessageAdmin(admin.ModelAdmin):
#     list_display = ('user', 'room', 'body', 'edited', 'updated', 'created')
#     list_filter = ('edited',)
#     search_fields = ('user__username', 'room__name', 'body')
    
#     readonly_fields = ('user', 'room', 'body', 'edited', 'updated', 'created')
    
#     list_per_page = 25


# admin.site.register(User, UserAdmin)
# admin.site.register(Room, RoomAdmin)
# admin.site.register(Topic, TopicAdmin)
# admin.site.register(Message, MessageAdmin)
