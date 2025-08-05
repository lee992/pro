from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .models import Post, Comment, Category


class UserProfileForm(forms.ModelForm):
    """
    A form for users to edit their basic profile information.
    """
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['first_name'].label = _("First name")
        self.fields['last_name'].label = _("Last name")


class PostForm(forms.ModelForm):
    """
    A form for creating and editing posts.
    """
    class Meta:
        model = Post
        fields = ['title', 'category', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].label = _("Title")
        self.fields['category'].label = _("Category")
        self.fields['content'].label = _("Content")
        self.fields['category'].queryset = Category.objects.all()
        # 사용자가 카테고리를 선택하지 않고 폼을 제출하는 것을 방지하기 위해
        # 이 필드를 명시적으로 필수로 설정합니다.
        self.fields['category'].empty_label = _("카테고리를 선택해주세요")
        self.fields['category'].required = True


class CommentForm(forms.ModelForm):
    """
    A form for adding comments to a post.
    """
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': _("Add a comment...")
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].label = "" # No label for the comment box