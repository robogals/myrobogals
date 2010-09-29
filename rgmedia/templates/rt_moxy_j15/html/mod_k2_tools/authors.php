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

<div id="k2ModuleBox<?php echo $module->id; ?>" class="k2AuthorsListBlock <?php echo $params->get('moduleclass_sfx'); ?>">
  <ul>
    <?php foreach ($authors as $author): ?>
    <li>
      <?php if ($params->get('authorAvatar')):?>
      <img class="abAuthorAvatar" src="<?php echo $author->avatar;?>" alt="<?php echo $author->name; ?>" />
      <?php endif; ?>
      
      <a class="abAuthorName" href="<?php echo $author->link; ?>">
      	<?php echo $author->name; ?>
      	
      	<?php if ($params->get('authorItemsCounter')):?>
      	<span>(<?php echo $author->items; ?>)</span>
      	<?php endif; ?>
      </a>
      
      <br class="clr" />
      
      <?php if ($params->get('authorLatestItem')):?>
      <a class="abAuthorLatestItem" href="<?php echo $author->latest->link;?>" title="<?php echo $author->latest->title; ?>">
      	<?php echo $author->latest->title; ?>
      </a>
      <?php endif; ?>
      
      <br class="clr" />
      
      <span class="abAuthorCommentsCount">
      	<?php echo $author->latest->numOfComments;?> <?php echo JText::_('comments');?>
      </span>
    </li>
    <?php endforeach; ?>
  </ul>
</div>
