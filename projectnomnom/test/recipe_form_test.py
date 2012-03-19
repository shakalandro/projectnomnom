import mox
from django import test
from django.utils import unittest
from django import forms
from django.core import exceptions
from projectnomnom.util import list_field


class FakeForm(forms.Form):
    field1 = forms.CharField()
    field2 = forms.IntegerField()
    field3 = forms.BooleanField()
    field4 = forms.ChoiceField(choices=map(lambda x: (str(x), str(x)), range(3)))


class FakeListForm(forms.Form):
    listfield = list_field.ListField(base_form=FakeForm, default_length=2, label='Listfield')


class RecipeFormTest(unittest.TestCase):
    def setUp(self):
        # Create an instance of Mox
        self.mox = mox.Mox()
        test.utils.setup_test_environment()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_user_stub()

    def tearDown(self):
        self.mox.VerifyAll()
        self.mox.ResetAll()
        self.mox.UnsetStubs()
        self.testbed.deactivate()
        unittest.TestCase.tearDown(self)

    def assertDictEqual(self, dict1, dict2):
        if len(dict1) != len(dict2):
            raise AssertionError('The given dicts have a different number of entries: %d, %d'
                                 % (len(dict1), len(dict2)))
        else:
            for key, value in dict1.iteritems():
                if key not in dict2.keys():
                    raise AssertionError('The first dict has a %s field, but the second does not.'
                                         % key)
                elif dict2[key] != value:
                    raise AssertionError('Dicts disagree on %s: %s, %s' % (key, value, dict2[key]))

    def assertDictListEqual(self, lst1, lst2):
        if len(lst1) != len(lst2):
            raise AssertionError('The given dicts have a different number of entries: %d, %d'
                                 % (len(lst1), len(lst2)))
        else:
            for x, y in zip(lst1, lst2):
                self.assertDictEqual(x, y)
        

    def testListInputRender(self):
        expected = """<ol><li><ul><li><label for="id_test-0-field1">Field1:</label> <input type="text" name="test-0-field1" id="id_test-0-field1" /></li>
<li><label for="id_test-0-field2">Field2:</label> <input type="text" name="test-0-field2" id="id_test-0-field2" /></li>
<li><label for="id_test-0-field3">Field3:</label> <input type="checkbox" name="test-0-field3" id="id_test-0-field3" /></li>
<li><label for="id_test-0-field4">Field4:</label> <select name="test-0-field4" id="id_test-0-field4">
<option value="0">0</option>
<option value="1">1</option>
<option value="2">2</option>
</select></li></ul></li></ol><button id='add-test' onclick='return false;'>Add</button>"""
        expected2 = """<ol><li><ul><li><label for="id_test2-0-field1">Field1:</label> <input type="text" name="test2-0-field1" id="id_test2-0-field1" /></li>
<li><label for="id_test2-0-field2">Field2:</label> <input type="text" name="test2-0-field2" id="id_test2-0-field2" /></li>
<li><label for="id_test2-0-field3">Field3:</label> <input type="checkbox" name="test2-0-field3" id="id_test2-0-field3" /></li>
<li><label for="id_test2-0-field4">Field4:</label> <select name="test2-0-field4" id="id_test2-0-field4">
<option value="0">0</option>
<option value="1">1</option>
<option value="2">2</option>
</select></li></ul></li><li><ul><li><label for="id_test2-1-field1">Field1:</label> <input type="text" name="test2-1-field1" id="id_test2-1-field1" /></li>
<li><label for="id_test2-1-field2">Field2:</label> <input type="text" name="test2-1-field2" id="id_test2-1-field2" /></li>
<li><label for="id_test2-1-field3">Field3:</label> <input type="checkbox" name="test2-1-field3" id="id_test2-1-field3" /></li>
<li><label for="id_test2-1-field4">Field4:</label> <select name="test2-1-field4" id="id_test2-1-field4">
<option value="0">0</option>
<option value="1">1</option>
<option value="2">2</option>
</select></li></ul></li></ol><button id='add-test2' onclick='return false;'>Add</button>"""
        input = list_field.ListInput(FakeForm, default_length=1)
        self.assertEqual(expected, input.render('test', None))
        
        input2 = list_field.ListInput(FakeForm, default_length=2)
        self.assertEqual(expected2, input2.render('test2', None))

    def testListInputValueFromDataDict(self):
        input_data = {'test-0-field1': '1',
                      'test-0-field2': 2,
                      'test-0-field3': True,
                      'test-0-field4': '4'
                      }
        input_data2 = {'test2-0-field1': '1',
                      'test2-0-field2': 2,
                      'test2-0-field3': True,
                      'test2-0-field4': '4',
                      'test2-1-field1': '5',
                      'test2-1-field2': 6,
                      'test2-1-field3': False,
                      'test2-1-field4': '8'
                      }
        expected = {'test-TOTAL_FORMS': '1',
                    'test-INITIAL_FORMS': '0',
                    'test-MAX_NUM_FORMS': '',
                    'test-0-field1': '1',
                    'test-0-field2': 2,
                    'test-0-field3': True,
                    'test-0-field4': '4'}
        expected2 = {'test2-TOTAL_FORMS': '2',
                     'test2-INITIAL_FORMS': '0',
                     'test2-MAX_NUM_FORMS': '',
                     'test2-0-field1': '1',
                     'test2-0-field2': 2,
                     'test2-0-field3': True,
                     'test2-0-field4': '4',
                     'test2-1-field1': '5',
                     'test2-1-field2': 6,
                     'test2-1-field3': False,
                     'test2-1-field4': '8'}
        input = list_field.ListInput(FakeForm, default_length=1)
        self.assertDictEqual(expected, input.value_from_datadict(input_data, None, 'test'))
        
        input2 = list_field.ListInput(FakeForm, default_length=1)
        self.assertDictEqual(expected2, input2.value_from_datadict(input_data2, None, 'test2'))

    def testListField(self):
        input_data = {'test-TOTAL_FORMS': '2',
                      'test-INITIAL_FORMS': '0',
                      'test-MAX_NUM_FORMS': '',
                      'test-0-field1': '1',
                      'test-0-field2': '2',
                      'test-0-field3': 'True',
                      'test-0-field4': '1',
                      'test-1-field1': '5',
                      'test-1-field2': 6,
                      'test-1-field3': 'True',
                      'test-1-field4': '1'}
        field = list_field.ListField(base_form=FakeForm, label='test')
        try:
            field.clean(input_data)
        except exceptions.ValidationError, e:
            self.fail(e)
        
        input_data['test-1-field4'] = '8'
        self.assertRaises(exceptions.ValidationError, field.clean, input_data)

        input_data['test-1-field4'] = '1'
        input_data['test-0-field2'] = 'hi'
        self.assertRaises(exceptions.ValidationError, field.clean, input_data)

    def testFakeListFormRender(self):
        expected = """<p><label for="id_listfield">Listfield:</label> <ol><li><ul><li><label for="id_listfield-0-field1">Field1:</label> <input type="text" name="listfield-0-field1" id="id_listfield-0-field1" /></li>
<li><label for="id_listfield-0-field2">Field2:</label> <input type="text" name="listfield-0-field2" id="id_listfield-0-field2" /></li>
<li><label for="id_listfield-0-field3">Field3:</label> <input type="checkbox" name="listfield-0-field3" id="id_listfield-0-field3" /></li>
<li><label for="id_listfield-0-field4">Field4:</label> <select name="listfield-0-field4" id="id_listfield-0-field4">
<option value="0">0</option>
<option value="1">1</option>
<option value="2">2</option>
</select></li></ul></li><li><ul><li><label for="id_listfield-1-field1">Field1:</label> <input type="text" name="listfield-1-field1" id="id_listfield-1-field1" /></li>
<li><label for="id_listfield-1-field2">Field2:</label> <input type="text" name="listfield-1-field2" id="id_listfield-1-field2" /></li>
<li><label for="id_listfield-1-field3">Field3:</label> <input type="checkbox" name="listfield-1-field3" id="id_listfield-1-field3" /></li>
<li><label for="id_listfield-1-field4">Field4:</label> <select name="listfield-1-field4" id="id_listfield-1-field4">
<option value="0">0</option>
<option value="1">1</option>
<option value="2">2</option>
</select></li></ul></li></ol><button id='add-listfield' onclick='return false;'>Add</button></p>"""
        form = FakeListForm()
        self.assertEqual(expected, form.as_p())

    def testListFormValidation(self):
        input_data = {'listfield-0-field1': '1',
                      'listfield-0-field2': '2',
                      'listfield-0-field3': 'True',
                      'listfield-0-field4': '1',
                      'listfield-1-field1': '5',
                      'listfield-1-field2': 6,
                      'listfield-1-field3': 'True',
                      'listfield-1-field4': '1'}
        input = FakeListForm(data=input_data)
        print input.errors
        self.assertTrue(input.is_valid())

"""
Validation tests to write: verify that the submitted model is as expected 
        in addition to success or not
    - invalid form
    - all required fields
    - with an image
    - optional fields
    - ingredient list
    - ingredient list with skipped numbering
    - ingredient with substitute
    - ingredient with invalid substitute
    - ingredient that is garnish
    - directions list
    - directions list with skipped numbering
    - nutrition and timings info
"""


if __name__ == "__main__":
    test.utils.setup_test_environment()
    unittest.main()