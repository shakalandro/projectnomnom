$(document).ready(function() {
	$('#ingredients_list ul li:nth-child(7)').hide();
	$('#ingredients_list ul li:nth-child(6)').hide();
	$('#ingredients_list input[id*="substitute"]').click(substitute_onclick);
	$('#ingredients_list').sortable({update: renumber_ingredients_list});
	$('#directions_list').sortable({update: renumber_directions_list});
});

function ingredients_hook(e) {
	/*
	 * Respond to the add ingredient 'event' performed by the ingredients list widget.
	 * Hides the substitute ui and registers the onclick event.
	 * */
	var item_num = parseInt($(e).find('label').attr('for').split('-')[1]);
	$(e).find('label[for=id_ingredients-' + item_num + '-sub_ingredient]').parent().hide();
	$(e).find('label[for=id_ingredients-' + item_num + '-comment]').parent().hide();
	$(e).find('input[id*="substitute"]').click(substitute_onclick);
}

function substitute_onclick() {
	/*
	 * This function toggles the substitute elements when the substitute box is checked.
	 * Provides the current ingredients as substitute options.
	 * */
	if ($(this).attr('checked') == 'checked') {
		var item_num = parseInt($(this).attr('id').split('-')[1]);
		// Show the list and associated label
		$('#ingredients_list label[for=id_ingredients-' + item_num + '-sub_ingredient]').parent().show();
		$('#ingredients_list label[for=id_ingredients-' + item_num + '-comment]').parent().show();
		var select_element = $(this).parent().parent().find('select');
		// Create the options list for the current ingredients
		select_element.append("<option value='-none-' class='null_option'>-none-</option>");
		$('#ingredients_list input[id*="item"]').each(function(i, e) {
			var value = $(e).val();
			var ingr_num = parseInt($(e).attr('id').split('-')[1]);
			if (value.length > 0 && ingr_num != item_num) {
				select_element.append('<option value="' + value + '">' + value + '</option>');
			}
		});
	} else {
		var item_num = parseInt($(this).attr('id').split('-')[1]);
		$(this).parent().parent().find('select').empty();
		$(this).parent().parent().find('input[id*="comment"]').empty();
		$('#ingredients_list label[for=id_ingredients-' + item_num + '-sub_ingredient]').parent().hide();
		$('#ingredients_list label[for=id_ingredients-' + item_num + '-comment]').parent().hide();
	}
}

function build_item_attr(s, idx) {
	var parts = s.split('-');
	parts[1] = idx;
	return parts.join('-');
}

function renumber_ingredients_list(e, ui) {
	$('> li', $(ui.item).parent()).each(function(idx, elem) {
		$(elem).find('li').each(function(idx2, elem2) {
			var input = $(elem2).find('input,select');
			input.attr({'id': build_item_attr(input.attr('id'), idx),
						'name': build_item_attr(input.attr('name'), idx)});
			var label = $(elem2).find('label');
			label.attr('for', build_item_attr(label.attr('for'), idx));
		});
	});
}

function renumber_directions_list(e, ui) {
	$('> li', $(ui.item).parent()).each(function(idx, elem) {
		var input = $(elem).find('input,select');
		input.attr({'id': build_item_attr(input.attr('id'), idx),
					'name': build_item_attr(input.attr('name'), idx)});
	});
}