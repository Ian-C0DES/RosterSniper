from django import forms

from .models import SuggestedSchool


class SuggestedSchoolForm(forms.ModelForm):

	class Meta:
		model = SuggestedSchool
		fields = ('school_name', 'edu_site', 'registration_site', 'notes')
		widgets = {
			'notes': forms.Textarea(attrs={'rows': 4}),
		}
