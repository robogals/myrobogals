	$(document).ready(function() {
		var int = 1;

		$('input[name=type]:radio').change(function() {
			switch ($('input[name=type]:radio:checked').val()) {
				case '1':
					$('#form_table_chapters').show();
					$('#form_table_exec').hide();
					$('#form_table_recipients').hide();
					$('#form_table_newsletter').hide();
					$('#form_table_lists').hide();
					break;
				case '2':
					$('#form_table_chapters').hide();
					$('#form_table_exec').show();
					$('#form_table_recipients').hide();
					$('#form_table_newsletter').hide();
					$('#form_table_lists').hide();
					break;
				case '3':
					$('#form_table_chapters').hide();
					$('#form_table_exec').hide();
					$('#form_table_recipients').show();
					$('#form_table_newsletter').hide();
					$('#form_table_lists').hide();
					break;
				case '4':
					$('#form_table_chapters').hide();
					$('#form_table_exec').hide();
					$('#form_table_recipients').hide();
					$('#form_table_newsletter').show();
					$('#form_table_lists').hide();
					break;
				case '5':
					$('#form_table_chapters').hide();
					$('#form_table_exec').hide();
					$('#form_table_recipients').hide();
					$('#form_table_newsletter').hide();
					$('#form_table_lists').show();
					break;
			}
		});
		$('input[name=type]:radio').change();
		
		$('#id_action').change(function() {
			switch ($('#id_action').val()) {
				case '1':
					$('#inviteemail').show();
					break;
				case '2':
					$('#inviteemail').hide();
					break;
			}
		});
		$('#id_action').change();
	});
