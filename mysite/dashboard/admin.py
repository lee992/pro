from django.contrib import admin
from django.utils.text import Truncator
from .models import Post, Comment, Like, Bookmark, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """카테고리 관리자 페이지 설정"""
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """게시글 관리자 페이지 설정"""
    list_display = ('title', 'author', 'category', 'created_at')
    list_filter = ('created_at', 'author', 'category')
    search_fields = ('title', 'content', 'author__username')
    raw_id_fields = ('author', 'category')
    date_hierarchy = 'created_at'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """댓글 관리자 페이지 설정"""
    list_display = ('post', 'author', 'content_preview', 'created_at')
    list_filter = ('created_at', 'author')
    search_fields = ('content', 'post__title', 'author__username')
    raw_id_fields = ('post', 'author')
    date_hierarchy = 'created_at'

    def content_preview(self, obj):
        """댓글 내용을 30자만 미리 보여줍니다."""
        return Truncator(obj.content).chars(30, truncate='...')
    content_preview.short_description = '내용 미리보기'

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    """좋아요 관리자 페이지 설정"""
    list_display = ('post', 'user', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('post__title', 'user__username')
    raw_id_fields = ('post', 'user')
    date_hierarchy = 'created_at'

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    """북마크 관리자 페이지 설정"""
    list_display = ('post', 'user', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('post__title', 'user__username')
    raw_id_fields = ('post', 'user')
    date_hierarchy = 'created_at'
