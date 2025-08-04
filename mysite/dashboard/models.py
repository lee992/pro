from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Post(models.Model):
    # 게시글 작성자를 연결합니다.
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    # 글 제목을 저장할 글자 칸
    title = models.CharField(max_length=200)
    # 글 내용을 저장할 긴 글자 칸
    content = models.TextField()
    # 작성 시각을 자동으로 저장
    created_at = models.DateTimeField(auto_now_add=True)
 
    def __str__(self):
        # 객체를 문자열로 보여줄 때 제목이 보이도록
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.author} on {self.post}'

class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # 사용자가 게시물에 한 번만 '좋아요'를 누를 수 있도록 설정
        unique_together = ('post', 'user')

    def __str__(self):
        return f'Like by {self.user} on {self.post}'

class Bookmark(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='bookmarks')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # 사용자가 게시물을 한 번만 북마크할 수 있도록 설정
        unique_together = ('post', 'user')

    def __str__(self):
        return f'Bookmark by {self.user} on {self.post}'
