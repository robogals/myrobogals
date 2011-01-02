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
					$('#newsletter_warning').hide();
					$('#html_newsletter').hide();
					$('#from_newsletter').hide();
					$('#html_normal').show();
					$('#from_normal').show();
					break;
				case '2':
					$('#form_table_chapters').hide();
					$('#form_table_exec').show();
					$('#form_table_recipients').hide();
					$('#form_table_newsletter').hide();
					$('#form_table_lists').hide();
					$('#newsletter_warning').hide();
					$('#html_newsletter').hide();
					$('#from_newsletter').hide();
					$('#html_normal').show();
					$('#from_normal').show();
					break;
				case '3':
					$('#form_table_chapters').hide();
					$('#form_table_exec').hide();
					$('#form_table_recipients').show();
					$('#form_table_newsletter').hide();
					$('#form_table_lists').hide();
					$('#newsletter_warning').hide();
					$('#html_newsletter').hide();
					$('#from_newsletter').hide();
					$('#html_normal').show();
					$('#from_normal').show();
					break;
				case '4':
					$('#form_table_chapters').hide();
					$('#form_table_exec').hide();
					$('#form_table_recipients').hide();
					$('#form_table_newsletter').show();
					$('#form_table_lists').hide();
					$('#newsletter_warning').show();
					$('#html_newsletter').show();
					$('#from_newsletter').show();
					$('#html_normal').hide();
					$('#from_normal').hide();
					break;
				case '5':
					$('#form_table_chapters').hide();
					$('#form_table_exec').hide();
					$('#form_table_recipients').hide();
					$('#form_table_newsletter').hide();
					$('#form_table_lists').show();
					$('#newsletter_warning').hide();
					$('#html_newsletter').hide();
					$('#from_newsletter').hide();
					$('#html_normal').show();
					$('#from_normal').show();
					break;
			}
		});
		$('input[name=type]:radio').change();
		
		$('input[name=editor]:radio').change(function() {
			switch ($('input[name=editor]:radio:checked').val()) {
				case 'wysiwyg':
					$('#wysiwyg').show();
					$('#plain_text').hide();
					break;
				case 'plain_text':
					$('#wysiwyg').hide();
					$('#plain_text').show();
					break;
			}
		});
		$('input[name=editor]:radio').change();
		
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

		$('#id_importaction').change(function() {
			switch ($('#id_importaction').val()) {
				case '1':
					$('#welcomeemail').show();
					break;
				case '2':
					$('#welcomeemail').hide();
					break;
				case '3':
					$('#welcomeemail').show();
					break;
			}
		});
		$('#id_importaction').change();
	});
