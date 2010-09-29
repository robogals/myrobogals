<?php
/*
// "K2 Content" Module by JoomlaWorks for Joomla! 1.5.x - Version 2.0
// Copyright (c) 2006 - 2009 JoomlaWorks Ltd. All rights reserved.
// Released under the GNU/GPL license: http://www.gnu.org/copyleft/gpl.html
// More info at http://www.joomlaworks.gr and http://k2.joomlaworks.gr
// Designed and developed by the JoomlaWorks team
// *** Last update: August 6th, 2009 ***
*/

// no direct access
defined('_JEXEC') or die ('Restricted access');

?>

<div id="k2ModuleBox<?php echo $module->id; ?>" class="k2ItemsBlock <?php echo $params->get('moduleclass_sfx'); ?>">

	<?php if($params->get('itemPreText')): ?>
	<p class="modulePretext"><?php echo $params->get('itemPreText'); ?></p>
	<?php endif; ?>
	
  <ul>
    <?php foreach ($items as $key=>$item):	?>
    <li class="<?php echo ($key%2) ? "odd" : "even"; ?>">
    
      <!-- Plugins: BeforeDisplay -->
      <?php echo $item->event->BeforeDisplay; ?>
      
      <!-- K2 Plugins: K2BeforeDisplay -->
      <?php echo $item->event->K2BeforeDisplay; ?>

      <?php if($params->get('itemAuthorAvatar')): ?>
			<img class="moduleItemAuthorAvatar" src="<?php echo $item->authorAvatar; ?>" alt="<?php echo $item->author; ?>" />
      <?php endif; ?>
      
      <?php if($params->get('itemTitle')): ?>
      <a class="moduleItemTitle" href="<?php echo $item->link; ?>"><?php echo $item->title; ?></a>
      <?php endif; ?>

      <?php if($params->get('itemAuthor')): ?>
      <?php echo K2HelperUtilities::writtenBy($item->authorGender); ?>

			<?php if(isset($item->authorLink)): ?>
			<a class="moduleItemAuthorLink" href="<?php echo $item->authorLink; ?>"><?php echo $item->author; ?></a>
			<?php else: ?>
			<?php echo $item->author; ?>
			<?php endif; ?>
			<?php endif; ?>
			      
      <!-- Plugins: AfterDisplayTitle -->
      <?php echo $item->event->AfterDisplayTitle; ?>
      
      <!-- K2 Plugins: K2AfterDisplayTitle -->
      <?php echo $item->event->K2AfterDisplayTitle; ?>

      <!-- Plugins: BeforeDisplayContent -->
      <?php echo $item->event->BeforeDisplayContent; ?>
      
      <!-- K2 Plugins: K2BeforeDisplayContent -->
      <?php echo $item->event->K2BeforeDisplayContent; ?>

      <?php if($params->get('itemImage') || $params->get('itemIntroText')): ?>
      <div class="moduleItemIntrotext">
      
	      <?php if($params->get('itemImage') && isset($item->image)): ?>
	      <a class="moduleItemImage" href="<?php echo $item->link; ?>" title="<?php echo JText::_('Continue reading'); ?> &quot;<?php echo htmlentities($item->title, ENT_QUOTES, 'UTF-8'); ?>&quot;">
	      	<img src="<?php echo $item->image; ?>" alt="<?php echo $item->title; ?>"/>
	      </a>
	      <?php endif; ?>
      
      	<?php if($params->get('itemIntroText')): ?>
      	<?php echo $item->introtext; ?>
      	<?php endif; ?>
      	
      </div>
      <?php endif; ?>
      
      <?php if($params->get('itemExtraFields') && count($item->extra_fields)): ?>  
      <b><?php echo JText::_('Additional Info'); ?></b>
      <ul class="moduleItemExtraFields">
        <?php foreach ($item->extra_fields as $extraField): ?>
				<li class="type<?php echo ucfirst($extraField->type); ?> group<?php echo $extraField->group; ?>">
					<span class="moduleItemExtraFieldsLabel"><?php echo $extraField->name; ?></span>
					<span class="moduleItemExtraFieldsValue"><?php echo $extraField->value; ?></span>
					<br class="clr" />		
				</li>
        <?php endforeach; ?>
      </ul>
      <?php endif; ?>
      
      <br class="clr" />

      <?php if($params->get('itemVideo')): ?>
      <div class="moduleItemVideo">
      	<?php echo $item->video ;?>
      	<br class="clr" />
      	<span class="moduleItemVideoCaption"><?php echo $item->video_caption ;?></span>
      	<span class="moduleItemVideoCredits"><?php echo $item->video_credits ;?></span>
      	<br class="clr" />
      </div>
      <br class="clr" />
      <?php endif; ?>     

      <!-- Plugins: AfterDisplayContent -->
      <?php echo $item->event->AfterDisplayContent; ?>
      
      <!-- K2 Plugins: K2AfterDisplayContent -->
      <?php echo $item->event->K2AfterDisplayContent; ?>
      
      <?php if($params->get('itemDateCreated')): ?>
      <span class="moduleItemDateCreated"><?php echo JText::_('Written on') ;?> <?php echo JHTML::_('date', $item->created, JText::_('DATE_FORMAT_LC2')); ?></span>
      <?php endif; ?>
      
      <?php if($params->get('itemCategory')): ?>
      <?php echo JText::_('in') ;?> <a class="moduleItemCategory" href="<?php echo $item->categoryLink; ?>"><?php echo $item->categoryname; ?></a>
      <?php endif; ?>
      
      <br class="clr" />

      <?php if($params->get('itemTags') && count($item->tags)>0): ?>
      <span class="moduleItemTags">
      	<b><?php echo JText::_('Tags'); ?>:</b>
        <?php foreach ($item->tags as $tag): ?>
        <a href="<?php echo $tag->link; ?>"><?php echo $tag->name; ?></a>
        <?php endforeach; ?>
      </span>
      <?php endif; ?>
      
      <?php if($params->get('itemAttachments') && count($item->attachments)): ?>
	  <p class="moduleAttachements">
	  <?php foreach ($item->attachments as $attachment): ?>
		<a title="<?php echo $attachment->titleAttribute; ?>" href="<?php echo JRoute::_('index.php?option=com_k2&view=item&task=download&id='.$attachment->id); ?>">
			<?php echo $attachment->title ; ?>
		</a>
	  <?php endforeach;?>
	  </p>
      <?php endif; ?>

			<?php if($params->get('itemCommentsCounter')): ?>
			<?php if($item->numOfComments>0): ?>
			<a class="moduleItemComments" href="<?php echo $item->link.'#itemCommentsAnchor'; ?>">
				<?php echo $item->numOfComments; ?> <?php if($item->numOfComments>1) echo JText::_('comments'); else echo JText::_('comment'); ?>
			</a>
			<?php else: ?>
			<a class="moduleItemComments" href="<?php echo $item->link.'#itemCommentsAnchor'; ?>">
				<?php echo JText::_('Be the first to comment!'); ?>
			</a>
			<?php endif; ?>
			<?php endif; ?>

			<?php if($params->get('itemHits')): ?>
			<span class="moduleItemHits">
				<?php echo JText::_('Read'); ?> <?php echo $item->hits; ?> <?php echo JText::_('times'); ?>
			</span>
			<?php endif; ?>
			
			<?php if($params->get('itemReadMore')): ?>
			<div class="readon-wrap1"><div class="readon1-l"></div><a class="readon-main" href="<?php echo $item->link;?>"><span class="readon1-m"><span class="readon1-r"><?php echo JText::_('Read more...');?></span></span></a></div><div class="clr"></div>
			<?php endif; ?>
      
      <!-- Plugins: AfterDisplay -->
      <?php echo $item->event->AfterDisplay; ?>
      
      <!-- K2 Plugins: K2AfterDisplay -->
      <?php echo $item->event->K2AfterDisplay; ?>
      
      <br class="clr" />
    </li>
    <?php endforeach; ?>
  </ul>
  
	<?php if($params->get('itemCustomLink')): ?>
	<a class="moduleCustomLink" href="<?php echo $params->get('itemCustomLinkURL'); ?>" title="<?php echo htmlentities($params->get('itemCustomLinkTitle'), ENT_QUOTES, 'UTF-8'); ?>">
		<?php echo $params->get('itemCustomLinkTitle'); ?>
	</a>
	<?php endif; ?>
</div>
