from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm, ValidationError
from ..models import Student, CourseRating, Faculty
from ..widgets import RangeInput
from django import forms


class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(
        label="סיסמא",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text="8 תווים, לפחות אות אחת, שונה משם המשתמש והמייל, לא סיסמא 'טרוויאלית'.<br><br>",
    )
    password2 = forms.CharField(
        label="אימות סיסמא",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        help_text="<br><br>",
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if not email.endswith('technion.ac.il'):
            raise ValidationError('חובה להרשם עם מייל טכניוני')
        return email

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ("email",)
        labels = {
            'username': 'שם משתמש',
            'email': 'מייל טכניוני',
            'password1': '[[[',
            'password2': 'אימות סיסמא',
        }
        help_texts = {
            'username': '<br><br>',
            'email': ' חובה להשתמש במייל טכניוני לאימות<br><br>',
        }


class StudentRegForm(ModelForm):
    faculty = forms.ModelChoiceField(
        queryset=Faculty.objects.all().order_by('faculty'),
        label='פקולטה'
    )

    def clean_credit_points(self):
        cp = self.cleaned_data['credit_points']
        if cp is not None:
            if cp < 0 or cp > 400:
                raise ValidationError('אם אתה לא רוצה להגיד כמה נק"ז צברת, לא צריך טובות, פשוא השאר את השדה ריק')
        return cp

    def clean_semester(self):
        semester = self.cleaned_data['semester']
        if semester is not None:
            if semester < 0 or semester > 20:
                raise ValidationError('אם אתה לא רוצה להגיד באיזה סמסטר אתה, לא צריך טובות, פשוא השאר את השדה ריק')
        return semester

    class Meta:
        model = Student
        fields = ('faculty', 'degree_path', 'credit_points', 'semester')
        labels = {
            'faculty': 'שם משתמש',
            'degree_path': 'מסלול (לא חובה)',
            'credit_points': 'נקודות זכות שצברת (לא חובה)',
            'semester': 'סמסטר (לא חובה) :',
        }
        help_texts = {
            'semester': 'כמה סמסטרים עברת מתחילת התואר, לא כולל הנוכחי',
        }


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
