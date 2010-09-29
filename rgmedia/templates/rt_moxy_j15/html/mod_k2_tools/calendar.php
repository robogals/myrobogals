<?php
/*
// "K2 Tools" Module by JoomlaWorks for Joomla! 1.5.x - Version 2.0
// Copyright (c) 2006 - 2009 JoomlaWorks Ltd. All rights reserved.
// Released under the GNU/GPL license: http://www.gnu.org/copyleft/gpl.html
// More info at http://www.joomlaworks.gr and http://k2.joomlaworks.gr
// Designed and developed by the JoomlaWorks team
// *** Last update: August 6th, 2009 ***
*/

// no direct access
defined('_JEXEC') or die ('Restricted access');

?>

<script type="text/javascript">
	//<![CDATA[
	window.addEvent('domready', function(){
	    $$('a.calendarNavLink').addEvent('click', function(e){
	        new Event(e).stop();
					var url = this.getProperty('href');
	        $('k2ModuleBox<?php echo $module->id; ?>').empty().addClass('k2CalendarLoader');
	        new Ajax(url, {
	            method: 'post',
	            update: $('k2ModuleBox<?php echo $module->id; ?>'),
	            onComplete: function(){
	                $('k2ModuleBox<?php echo $module->id; ?>').removeClass('k2CalendarLoader');
									window.fireEvent('k2CalendarEvent');
	            }
	        }).request();
	    });
	    
	});
	
	window.addEvent('k2CalendarEvent', function(){
	    $$('a.calendarNavLink').addEvent('click', function(e){
	        new Event(e).stop();
					var url = this.getProperty('href');
	        $('k2ModuleBox<?php echo $module->id; ?>').empty().addClass('k2CalendarLoader');
	        new Ajax(url, {
	            method: 'post',
	            update: $('k2ModuleBox<?php echo $module->id; ?>'),
	            onComplete: function(){
	                $('k2ModuleBox<?php echo $module->id; ?>').removeClass('k2CalendarLoader');
									window.fireEvent('k2CalendarEvent');
	            }
	        }).request();
	    });
	});
	//]]>
</script>

<div id="k2ModuleBox<?php echo $module->id; ?>" class="k2CalendarBlock <?php echo $params->get('moduleclass_sfx'); ?>">
	<?php echo $calendar; ?>
</div>
