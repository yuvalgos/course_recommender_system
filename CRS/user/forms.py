from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm, ValidationError, Select
from ..models import Student, CourseRating, Faculty
from ..widgets import RangeInput
from django import forms
from .widgets import CustomRadioSelect


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
            'username': ' רק אותיות באנגלית והסימנים '
                        '@/./+/-/_'
                        '<br>'
                        'מומלץ להשתמש ב-FirstName_LastName. כן, מותר לכתוב פה מייל והוא ישמש כשם משתמש.'
                        '<br><br>',
            'email': ' חובה להשתמש במייל טכניוני לאימות<br><br>',
        }


class StudentRegForm(ModelForm):
    faculty = forms.ModelChoiceField(
        queryset=Faculty.objects.all().order_by('faculty'),
        label='פקולטה',
        empty_label='-בחר פקולטה-',
    )

    def clean_credit_points(self):
        cp = self.cleaned_data['credit_points']
        if cp is not None:
            if cp < 0 or cp > 400:
                raise ValidationError('אם אתה לא רוצה להגיד כמה נק"ז צברת, לא צריך טובות, פשוט השאר את השדה ריק')
        return cp

    def clean_semester(self):
        semester = self.cleaned_data['semester']
        if semester is not None:
            if semester < 0 or semester > 20:
                raise ValidationError('אם אתה לא רוצה להגיד באיזה סמסטר אתה, לא צריך טובות, פשוא השאר את השדה ריק')
        return semester

    class Meta:
        model = Student
        fields = ('faculty', 'degree_path', 'credit_points', 'semester', 'want_emails')
        labels = {
            'faculty': 'שם משתמש',
            'degree_path': 'מסלול (לא חובה)',
            'credit_points': 'נקודות זכות שצברת (לא חובה)',
            'semester': 'סמסטר (לא חובה)',
            'want_emails': 'קבלת מייל על עדכונים ושינויים'
        }
        help_texts = {
            'semester': 'כמה סמסטרים עברת מתחילת התואר, לא כולל הנוכחי'
                        '',
            'want_emails': 'לא נשלח פרסומות או כמות מוגזמת של מיילים, רק עדכונים חשובים לעיתים רחוקות'
        }
        widgets = {'want_emails': Select(choices=[(True, '      אין בעיה'),
                                                  (False, '     עזבו אותי בשקט! לא רוצה לשמוע מכם יותר')],
                                         ),
                   'faculty': Select(attrs={"text-align-last": "center"})
                   }


class StudentEditForm(StudentRegForm):
    pass


class CourseRatingForm(ModelForm):
    class Meta:
        model = CourseRating
        fields = ('difficulty', 'workload', 'final_grade')
        labels = {
            'difficulty': 'רמת קושי',
            'workload': 'רמת עומס',
            'final_grade': 'ציון סופי (לא חובה, הזינו או השאירו ריק)',
        }
        widgets = {
            'difficulty': forms.NumberInput(
                attrs={'type': 'range', 'class': 'form-range', 'min': '1', 'step': '0.5',
                       'max': '10', 'value': '5', 'style': 'border-style: none;',
                       'oninput': 'this.nextElementSibling.value = this.value'}
            ),
            'workload': forms.NumberInput(
                attrs={'type': 'range', 'class': 'form-range', 'min': '1', 'step': '0.5',
                       'max': '10', 'value': '5', 'style': 'border-style: none;',
                       'oninput': 'this.nextElementSibling.value = this.value'}
            ),
            'final_grade': forms.NumberInput(
                attrs={'type': 'Number', 'min': '0',
                       'max': '100', 'step': '1', 'style': 'width:60'}
            ),
        }


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, label='שם')
    email = forms.EmailField(label='מייל לחזרה')
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 30,
                                                           'cols': 30,
                                                           'style': 'height: 30%'}),
                              label='הודעה')
