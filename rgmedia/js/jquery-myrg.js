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
					$('#status_newsletter').hide();
					$('#html_normal').show();
					$('#from_normal').show();
					$('#status_normal').show();
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
					$('#status_newsletter').hide();
					$('#html_normal').show();
					$('#from_normal').show();
					$('#status_normal').show();
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
					$('#status_newsletter').hide();
					$('#html_normal').show();
					$('#from_normal').show();
					$('#status_normal').show();
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
					$('#status_newsletter').show();
					$('#html_normal').hide();
					$('#from_normal').hide();
					$('#status_normal').hide();
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
					$('#status_newsletter').hide();
					$('#html_normal').show();
					$('#from_normal').show();
					$('#status_normal').show();
					break;
			}
		});
		$('input[name=type]:radio').change();

		$('input[name=scheduling]:radio').change(function() {
			switch ($('input[name=scheduling]:radio:checked').val()) {
				case '0':
					$('#form_table_scheduling').hide();
					break;
				case '1':
					$('#form_table_scheduling').show();
					break;
			}
		});
		$('input[name=scheduling]:radio').change();
		
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
		
		$('input[name=invitee_type]:radio').change(function() {
			switch ($('input[name=invitee_type]:radio:checked').val()) {
				case '5':
					$('#form_table_recipientes').show();
					break;
				default:  $('#form_table_recipientes').hide();
			}
		});
		$('input[name=invitee_type]:radio').change();
		
		$('#basic-info-title').click(function() {
			$('#basic-info-table').toggle(0, function() {
				if ($('#basic-info-table').is(':hidden')) {
					$('#basic-info-title').addClass('nopadtitle moduletablenobottom');
					$('#basic-info-collapse').hide();
					$('#basic-info-expand').show();
				} else {
					$('#basic-info-title').removeClass('nopadtitle moduletablenobottom');
					$('#basic-info-collapse').show();
					$('#basic-info-expand').hide();
				}
			});
		});

		$('#privacy-setting-title').click(function() {
			$('#privacy-setting-table').toggle(0, function() {
				if ($('#privacy-setting-table').is(':hidden')) {
					$('#privacy-setting-title').addClass('nopadtitle moduletablenobottom');
					$('#privacy-setting-collapse').hide();
					$('#privacy-setting-expand').show();
				} else {
					$('#privacy-setting-title').removeClass('nopadtitle moduletablenobottom');
					$('#privacy-setting-collapse').show();
					$('#privacy-setting-expand').hide();
				}
			});
		});

		$('#profile-info-title').click(function() {
			$('#profile-info-table').toggle(0, function() {
				if ($('#profile-info-table').is(':hidden')) {
					$('#profile-info-title').addClass('nopadtitle moduletablenobottom');
					$('#profile-info-collapse').hide();
					$('#profile-info-expand').show();
				} else {
					$('#profile-info-title').removeClass('nopadtitle moduletablenobottom');
					$('#profile-info-collapse').show();
					$('#profile-info-expand').hide();
				}
			});
		});
		
		$('#email-sms-title').click(function() {
			$('#email-sms-table').toggle(0, function() {
				if ($('#email-sms-table').is(':hidden')) {
					$('#email-sms-title').addClass('nopadtitle moduletablenobottom');
					$('#email-sms-collapse').hide();
					$('#email-sms-expand').show();
				} else {
					$('#email-sms-title').removeClass('nopadtitle moduletablenobottom');
					$('#email-sms-collapse').show();
					$('#email-sms-expand').hide();
				}
			});
		});

		$('#exec-fields-title').click(function() {
			$('#exec-fields-table').toggle(0, function() {
				if ($('#exec-fields-table').is(':hidden')) {
					$('#exec-fields-title').addClass('nopadtitle moduletablenobottom');
					$('#exec-fields-collapse').hide();
					$('#exec-fields-expand').show();
				} else {
					$('#exec-fields-title').removeClass('nopadtitle moduletablenobottom');
					$('#exec-fields-collapse').show();
					$('#exec-fields-expand').hide();
				}
			});
		});
		
		if ($('#profile-info-table').hasClass('jqerror')) {
			$('#profile-info-title').removeClass('nopadtitle moduletablenobottom');
			$('#profile-info-collapse').show();
			$('#profile-info-expand').hide();
			$('#profile-info-table').show();
		}
    
    
    
    
    
    /* 
     * 2013-06-16 
     * Invitees to conferences
     */
     
    $("form[action^='/conferences'] input[name='invitee_type']").change(function(){
      $(".invitee_email_selector").hide();
      $(".invitee_email_selector").filter("."+$(this).filter(":checked").attr("id")).show();
    });
    
    $("form[action^='/conferences'] input[name='invitee_type']:eq(0)").change();
    
    
    
    
	});
