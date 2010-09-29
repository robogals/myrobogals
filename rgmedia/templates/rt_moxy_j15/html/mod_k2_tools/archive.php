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

<div id="k2ModuleBox<?php echo $module->id; ?>" class="k2ArchivesBlock <?php echo $params->get('moduleclass_sfx'); ?>">
	<ul>
		<?php foreach($months as $month): ?>
		<li>
			<a href="<?php echo JRoute::_('index.php?option=com_k2&view=itemlist&task=date&month='.$month->m.'&year='.$month->y); ?>">
				<?php echo $month->name.' '.$month->y; ?>
				<?php if($params->get('archiveItemsCounter')) echo '('.$month->numOfItems.')'; ?> 
			</a>
		</li>
		<?php endforeach; ?>
	</ul>
</div>
