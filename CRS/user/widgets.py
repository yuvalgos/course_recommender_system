from django import forms
from django.forms import RadioSelect
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string


class CustomRadioSelect(RadioSelect):
    template_name = 'project/widgets/filter.html'

    def render(self, name, value, attrs=None, renderer=None):
        print(super().render(name, value, attrs, renderer))

        return mark_safe(render_to_string(self.template_name))