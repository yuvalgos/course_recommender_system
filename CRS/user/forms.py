from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from ..models import Student, CourseRating
from ..widgets import RangeInput


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ("email",)


class StudentRegForm(ModelForm):
    class Meta:
        model = Student
        fields = ('faculty', 'degree_path', 'credit_points', 'semester')


class EditCourseRatingForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['difficulty'].widget.attrs.update(
            {'type': 'range', 'min': '1',
             'max': '10', 'value': '5', 'style': 'width:60'})

        self.fields['workload'].widget.attrs.update(
            {'type': 'range', 'min': '1',
             'max': '10', 'value': '5', 'style': 'width:60'})

        self.fields['final_grade'].widget.attrs.update(
            {'type': 'range', 'min': '0',
             'max': '100', 'step': '1', 'style': 'width:60'})

    class Meta:
        model = CourseRating
        fields = ('difficulty', 'workload', 'final_grade')
        labels = {
            'difficulty': 'רמת קושי',
            'workload': 'רמת עומס',
            'final_grade': 'ציון סופי (לא חובה)',
        }
