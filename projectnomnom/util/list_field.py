import operator
from django import forms
from django.core import exceptions
from django.core import validators
from django.forms.formsets import formset_factory
from django.utils import safestring
from django.utils import datastructures


class ListInput(forms.Widget):
    def __init__(self, base_form, default_length=5, is_ordered=True, attrs=None):
        self.base_form = base_form
        temp_form = self.base_form()
        self.num_base_fields = len(temp_form.fields)
        self.default_length = default_length
        self.is_ordered = is_ordered
        super(ListInput, self).__init__(attrs)

    def __call__(self):
        return self

    def render(self, name, values, attrs=None, add_javascript=True):
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
        temp_form = self.base_form()
        print temp_form.fields
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
        parts = key.split('-')
        parts[-2] = str(num)
        return '-'.join(parts)

    def value_from_datadict(self, data, files, name):
        """
            Removes and renumbers empty forms. If all the forms were empty then all the form
            values are returned.
        """
        relevant_data = filter(lambda thing: name in thing[0], data.items())
        relevant_data = sorted(relevant_data, key=operator.itemgetter(0))
        i = 0
        values = []
        form_count = 0
        while i < len(relevant_data):
            form_num = int(relevant_data[i][0].split('-')[-2])
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
    widget = ListInput

    def __init__(self, base_form=None, default_length=5, is_ordered=True, *args, **kwargs):
        if base_form is None:
            raise ValueError('A form must be specified for the list input.')
        self.base_form = base_form
        self.widget = self.widget(base_form, default_length, is_ordered)
        super(ListField, self).__init__(*args, **kwargs)

    def validate(self, values):
        super(ListField, self).validate(values)
        if len(values) <= 3:
            raise exceptions.ValidationError('This field group is required.')
        factory_class = formset_factory(self.base_form)
        formset = factory_class(values, prefix=self.label.lower())
        if not formset.is_valid():
            raise exceptions.ValidationError('')