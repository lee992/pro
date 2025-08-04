from django.contrib import admin
from .models import Post, Comment, Like, Bookmark, Category

class PostAdmin(admin.ModelAdmin):
    """게시글 관리자 페이지 설정"""
    list_display = ('title', 'author', 'category', 'created_at')
    list_filter = ('created_at', 'author', 'category')
    search_fields = ('title', 'content')

class CommentAdmin(admin.ModelAdmin):
    """댓글 관리자 페이지 설정"""
    list_display = ('post', 'author', 'content_preview', 'created_at')
    list_filter = ('created_at', 'author')
    search_fields = ('content', 'post__title')

    def content_preview(self, obj):
        """댓글 내용을 30자만 미리 보여줍니다."""
        return obj.content[:30] + '...' if len(obj.content) > 30 else obj.content
    content_preview.short_description = '내용 미리보기'

class LikeAdmin(admin.ModelAdmin):
    """좋아요 관리자 페이지 설정"""
    list_display = ('post', 'user', 'created_at')
    list_filter = ('created_at',)

class BookmarkAdmin(admin.ModelAdmin):
    """북마크 관리자 페이지 설정"""
    list_display = ('post', 'user', 'created_at')
    list_filter = ('created_at',)

# 관리자 페이지에 모델 등록
admin.site.register(Post, PostAdmin)
admin.site.register(Category)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Like, LikeAdmin)
admin.site.register(Bookmark, BookmarkAdmin)
