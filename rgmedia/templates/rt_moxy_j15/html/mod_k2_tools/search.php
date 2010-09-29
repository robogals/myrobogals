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

<div id="k2ModuleBox<?php echo $module->id; ?>" class="k2SearchBlock <?php echo $params->get('moduleclass_sfx'); ?>">
  <form action="<?php echo JRoute::_('index.php?option=com_k2&view=itemlist&task=search'); ?>" method="get">
    <?php $app =& JFactory::getApplication(); if (!$app->getCfg('sef')): ?>
    <input type="hidden" name="option" value="com_k2" />
    <input type="hidden" name="view" value="itemlist" />
    <input type="hidden" name="task" value="search" />
    <?php endif; ?>
    
    <input name="searchword" maxlength="<?php echo $maxlength; ?>" alt="<?php echo $button_text; ?>" class="inputbox<?php echo $moduleclass_sfx; ?>" type="text" size="<?php echo $width; ?>" value="<?php echo $text; ?>" onblur="if(this.value=='') this.value='<?php echo $text; ?>';" onfocus="if(this.value=='<?php echo $text; ?>') this.value='';" />
    
    <?php if ($button):?>
    <?php if ($imagebutton):?>
    <input type="image" value="<?php echo $button_text; ?>" class="button<?php echo $moduleclass_sfx;?>" src="<?php echo $img; ?>" onclick="this.form.searchword.focus();"/>
    <?php else:?>
    <input type="submit" value="<?php echo $button_text; ?>" class="button<?php echo $moduleclass_sfx; ?>" onclick="this.form.searchword.focus();"/>
    <?php endif;?>
    <?php endif; ?>
  </form>
</div>
