from django import forms

from apps.user_profile.models import Profile


class ProfileSettingsForm(forms.ModelForm):
    class Meta:

        model = Profile
        fields = [
            'access_messaging',
            'access_posts',
            'access_about',
            'access_albums',
            'access_images',
            'access_stats',
        ]