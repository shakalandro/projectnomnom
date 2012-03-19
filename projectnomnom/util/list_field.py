"""
This module adds a ListField to the standard django field types. ListField operates as a dynamic
list of a collection of kinds of fields.

@author: Roy McElmurry (roy.miv@gmail.com)
"""

from django import forms
from django.core import exceptions
from django.core import validators
from django.forms.formsets import formset_factory
from django.utils import safestring
from django.utils import datastructures


class ListInput(forms.Widget):
    """
    This class acts as the primary widget for the ListField class. It's HTML representation is a
    list of the form elements that correspond to the elements of the ListField.
    """
    
    def __init__(self, base_form, default_length=5, is_ordered=True, attrs=None):
        """
        Params:
            base_form: The django form object from which the list elements will be based.
            default_list: How many list elements to produce initially for HTML output.
            in_ordered: Whether the HTML list is an ordered or unordered list.
            attrs: Any additional attributes that generic django Widgets can take. 
        """
        self.base_form = base_form
        temp_form = self.base_form()
        self.num_base_fields = len(temp_form.fields)
        self.default_length = default_length
        self.is_ordered = is_ordered
        super(ListInput, self).__init__(attrs)

    def __call__(self):
        """
        Required hack so that ListInput plays nice with the existing django widget framework.
        """
        return self

    def render(self, name, values, attrs=None, add_javascript=True):
        """
        Overrides super class
        
        Produces HTML content. The returned HTML is a list of form data that corresponds to the
        HTML rendered by the base_form constructor argument. If add_javascript is True then an HTML
        button will be added that generates a new list element when clicked.
        
        In addition if add_javascript is True a javascript method by the name of "name_hook" where
        name is the one provided will be called when a new list element is added and passed the
        corresponding element. Depends on the JQuery library.
        
        Params:
            name: A name for this HTML widget.
            values: Data to be filled in as defaults to the form data elements.
            attrs: Additional attributes that are passed to generic django widgets.
            add_javascript: Whether to add Javascript that makes the list dynamic.
        Return: A django safestring that represents the HTML representation of this widget.
        """
        format_func = lambda x: '<ul>%s</ul>' % x.as_ul()
        if self.num_base_fields <= 1:
            format_func = lambda x: x.as_p()[3:-4]

        result = "<ol id='%s_list'>" % name if self.is_ordered else "<ul id='%s_list'>" % name
        num_forms = 1 if values and len(values) - 3 > 0 else self.default_length
        factory_class = formset_factory(self.base_form,
                                        extra=num_forms)
        factory_forms = factory_class(data=values, prefix=name).forms
        for form in factory_forms:
            result += '<li>%s</li>' % format_func(form)
        result += '</ol>' if self.is_ordered else '</ul>'
        if add_javascript:
            result += "<script type='text/javascript'>%s</script>" % self._get_javascript(name, format_func)
            result += "<button id='add-%s' onclick='__add_%s();return false;'>Add</button>" % (name, name)
        return safestring.mark_safe(result)
    
    def _get_javascript(self, name, format_func):
        """
        Produces Javascript code that makes the list widget dynamic. Depends on the JQuery library.
        
        Params:
            name: A name for this HTML widget.
            format_func: A function that will properly format a new element of the list in HTML.
        Return: A string consisting of Javascript code.
        """
        temp_form = self.base_form()
        res = """
        function __add_%s() {
            $('#%s_list').append("<li>%s</li>");
            __renumber_%s();
            return false;
        }
        function __renumber_%s() {
            var last_elem = $('#%s_list > li').last();
            var pieces = %s;
            for (i in pieces) {
                last_elem.find('label[for="id_' + pieces[i] + '"]').attr('for', 'id_%s-' + __get_%s_number() + '-' + pieces[i]);
                last_elem.find('#id_' + pieces[i]).attr('id', 'id_%s-' + __get_%s_number() + '-' + pieces[i])
                        .attr('name', '%s-' + __get_%s_number() + '-' + pieces[i]);
            }
            try {
                %s_hook(last_elem);
            } catch (e) {}
        }
        function __get_%s_number() {
            return $('#%s_list > li').length;
        }
        """ % (name, name, format_func(temp_form).replace('"', "'").replace('\n',' \\\n'), name,
               name, name, temp_form.fields.keys(), name, name, name, name, name, name, name,
               name, name)
        return res
        

    def _renumber_form_key(self, key, num):
        """
        Properly renumbers a form element's id.
        
        Params:
            key: The original id string.
            num: The desired id number.
        Return: A string of the form %s-{num}-%s
        """
        parts = key.split('-')
        parts[-2] = str(num)
        return '-'.join(parts)

    def value_from_datadict(self, data, files, name):
        """
        Removes and renumbers empty forms. If all the forms were empty then all the form
        values are returned.
        
        Params:
            data: A dict of form data.
            files: Any file objects that are associated with this form.
            name: The name of this form element for use in filtering from the dict.
        
        Return: A dict of the relevant data for this field in a format that form_factory can
            understand.
        """
        relevant_data = filter(lambda thing: name in thing[0], data.items())
        relevant_data = sorted(relevant_data, key=lambda x: int(x[0].split('-')[-2]))
        i = 0
        values = []
        form_count = 0
        while i < len(relevant_data):
            form_num = int(relevant_data[i][0].split('-')[-2])
            print str(i) + str(relevant_data[i])
            j = i + 1
            all_blank = relevant_data[i][1] in validators.EMPTY_VALUES
            while j < len(relevant_data) and int(relevant_data[j][0].split('-')[-2]) == form_num:
                all_blank = all_blank and relevant_data[j][1] in validators.EMPTY_VALUES
                j += 1
            if not all_blank:
                values += map(lambda x: (self._renumber_form_key(x[0], form_count), x[1]),
                              relevant_data[i:j])
                form_count += 1
            i = j
        if form_count == 0:
            values = relevant_data
        values = datastructures.SortedDict(values)
        values[u'%s-TOTAL_FORMS' % name] = form_count if form_count else self.default_length
        values[u'%s-INITIAL_FORMS' % name] = u'0'
        values[u'%s-MAX_NUM_FORMS' % name] = u''
        return values



class ListField(forms.Field):
    """
    This class is a form field that can be included in any django model.
    Uses another form as a reference for what to have as list elements.
    """
    widget = ListInput

    def __init__(self, base_form=None, default_length=5, is_ordered=True, *args, **kwargs):
        """
        Params:
            base_form: The django form object from which the list elements will be based.
            default_list: How many list elements to produce initially for HTML output.
            in_ordered: Whether the HTML list is an ordered or unordered list.
        """
        if base_form is None:
            raise ValueError('A form must be specified for the list input.')
        self.base_form = base_form
        self.widget = self.widget(base_form, default_length, is_ordered)
        super(ListField, self).__init__(*args, **kwargs)

    def validate(self, values):
        """
        Determines if the given values represent a valid non-empty instance of this field.
        
        Params:
            values: A dict of the form data that corresponds to this field form in a format that
                form_factory understands.
        Return: Whether the date is valid or not.
        """
        super(ListField, self).validate(values)
        if len(values) <= 3:
            raise exceptions.ValidationError('This field group is required.')
        factory_class = formset_factory(self.base_form)
        formset = factory_class(values, prefix=self.label.lower())
        if not formset.is_valid():
            raise exceptions.ValidationError('')
