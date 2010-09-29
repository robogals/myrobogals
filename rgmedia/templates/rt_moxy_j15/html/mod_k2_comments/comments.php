<?php
/*
// "K2 Comments" Module by JoomlaWorks for Joomla! 1.5.x - Version 2.0
// Copyright (c) 2006 - 2009 JoomlaWorks Ltd. All rights reserved.
// Released under the GNU/GPL license: http://www.gnu.org/copyleft/gpl.html
// More info at http://www.joomlaworks.gr and http://k2.joomlaworks.gr
// Designed and developed by the JoomlaWorks team
// *** Last update: August 6th, 2009 ***
*/

// no direct access
defined('_JEXEC') or die ('Restricted access');

?>

<div id="k2ModuleBox<?php echo $module->id; ?>" class="k2LatestCommentsBlock <?php echo $params->get('moduleclass_sfx'); ?>">
	<ul>
		<?php if(count($comments)): ?>
		<?php foreach ($comments as $key=>$comment):	?>
		<li class="<?php echo ($key%2) ? "odd" : "even"; ?>">
			<?php if($comment->userImage): ?>
			<img style="width:<?php echo $componentParams->get('commenterImgWidth'); ?>px;height:auto;" class="lcAvatar" src="<?php echo $comment->userImage; ?>" alt="<?php echo $comment->userName; ?>" />
			<?php endif; ?>
			
			<?php if($params->get('commentLink')): ?>
			<a href="<?php echo $comment->link; ?>"><span class="lcComment"><?php echo $comment->commentText; ?></span></a>
			<?php else: ?>
			<span class="lcComment"><?php echo $comment->commentText; ?></span>
			<?php endif; ?>
			
			<br />
			
			<?php if($params->get('commenterName')): ?>
			<span class="lcUsername"><?php echo JText::_('written by'); ?>
			<?php if (isset($comment->userLink)):?>
			<a href="<?php echo $comment->userLink;?>">
			<?php endif; ?>
			 <?php echo $comment->userName; ?>
			<?php if (isset($comment->userLink)):?>
			</a>
			<?php endif; ?>
			 </span>
			<?php endif; ?>
			
			<?php if($params->get('commentDate')): ?>
			<span class="lcCommentDate">
				<?php if ($params->get('commentDateFormat') == 'relative') :?>
				<?php echo $comment->commentDate;?>
				<?php else:?>
				<?php echo JText::_('on'); ?> <?php echo JHTML::_('date', $comment->commentDate, JText::_('DATE_FORMAT_LC2')); ?>
				<?php endif; ?>
			</span>
			<?php endif; ?>
			
			<br />
			
			<?php if($params->get('itemTitle')): ?>
			<span class="lcItemTitle"><a href="<?php echo $comment->itemLink; ?>"><?php echo $comment->title; ?></a></span>
			<?php endif; ?>
			
			<?php if($params->get('itemCategory')): ?>
			<span class="lcItemCategory">(<a href="<?php echo $comment->catLink; ?>"><?php echo $comment->categoryname; ?></a>)</span>
			<?php endif; ?>
			
		</li>
		<?php endforeach; ?>
		<?php endif; ?>
	</ul>
</div>
