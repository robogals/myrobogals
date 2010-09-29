<?php
/*
// "K2" Component by JoomlaWorks for Joomla! 1.5.x - Version 2.0
// Copyright (c) 2006 - 2009 JoomlaWorks Ltd. All rights reserved.
// Released under the GNU/GPL license: http://www.gnu.org/copyleft/gpl.html
// More info at http://www.joomlaworks.gr and http://k2.joomlaworks.gr
// Designed and developed by the JoomlaWorks team
// *** Last update: August 6th, 2009 ***
*/

// no direct access
defined('_JEXEC') or die ('Restricted access');

?>

<!-- Start K2 Item Layout -->
<span id="startOfPageId<?php echo JRequest::getInt('id'); ?>"></span>

<div id="k2Container" class="itemView<?php if($this->item->params->get('pageclass_sfx')) echo ' '.$this->item->params->get('pageclass_sfx'); ?>">

	<!-- Plugins: BeforeDisplay -->
	<?php echo $this->item->event->BeforeDisplay; ?>
	
	<!-- K2 Plugins: K2BeforeDisplay -->
	<?php echo $this->item->event->K2BeforeDisplay; ?>

	<?php if(isset($this->item->editLink)): ?>
	<!-- Item edit link -->
	<span class="itemEditLink">
		<a class="modal" rel="{handler:'iframe',size:{x:990,y:650}}" href="<?php echo $this->item->editLink; ?>">
			<?php echo JText::_('Edit item'); ?>
		</a>
	</span>
	<?php endif; ?>

	<div class="itemHeader">
	
		<?php if($this->item->params->get('itemDateCreated')): ?>
		<!-- Date created -->
		<span class="itemDateCreated">
			<?php echo JHTML::_('date', $this->item->created , JText::_('DATE_FORMAT_LC2')); ?>
		</span>
		<?php endif; ?>
	
	  <?php if($this->item->params->get('itemTitle')): ?>
	  <!-- Item title -->
	  <h2 class="itemTitle">
	  	<?php echo $this->item->title; ?>
	  	
	  	<?php if($this->item->params->get('itemFeaturedNotice') && $this->item->featured): ?>
	  	<!-- Featured flag -->
	  	<span>
		  	<sup>
		  		<?php echo JText::_('Featured'); ?>
		  	</sup>
	  	</span>
	  	<?php endif; ?>

	  </h2>
	  <?php endif; ?>
		
  </div>

  <!-- Plugins: AfterDisplayTitle -->
  <?php echo $this->item->event->AfterDisplayTitle; ?>
  
  <!-- K2 Plugins: K2AfterDisplayTitle -->
  <?php echo $this->item->event->K2AfterDisplayTitle; ?>

	<?php if(
		$this->item->params->get('itemFontResizer') || 
		$this->item->params->get('itemPrintButton') || 
		$this->item->params->get('itemEmailButton') || 
		$this->item->params->get('itemSocialButton') || 
		$this->item->params->get('itemVideoAnchor') || 
		$this->item->params->get('itemImageGalleryAnchor') || 
		$this->item->params->get('itemCommentsAnchor')
	): ?>
  <div class="itemToolbar">
		<?php if($this->item->params->get('itemAuthor')): ?>
		<!-- Item Author -->
		<span class="itemAuthor">
			<?php echo K2HelperUtilities::writtenBy($this->item->author->profile->gender); ?> <a href="<?php echo $this->item->author->link; ?>"><?php echo $this->item->author->name; ?></a>
		</span>
		<?php endif; ?>
		<ul>
			<?php if($this->item->params->get('itemFontResizer')): ?>
			<!-- Font Resizer -->
			<li>
				<span class="itemTextResizerTitle"><?php echo JText::_('font size'); ?></span>
				<a href="#" id="fontDecrease">
					<span><?php echo JText::_('decrease font size'); ?></span>
				</a>
				<a href="#" id="fontIncrease">
					<span><?php echo JText::_('increase font size'); ?></span>
				</a>
			</li>
			<?php endif; ?>
			
			<?php if($this->item->params->get('itemPrintButton')): ?>
			<!-- Print Button -->
			<li>
				<?php if(JRequest::getCmd('print')==1): ?>
				<a class="itemPrintLink" href="<?php echo $this->item->printLink; ?>" onclick="window.print();return false;">
					<span><?php echo JText::_('Print'); ?></span>
				</a>		
				<?php else: ?>
				<a class="modal itemPrintLink" href="<?php echo $this->item->printLink; ?>" rel="{handler:'iframe',size:{x:900,y:500}}">
					<span><?php echo JText::_('Print'); ?></span>
				</a>
				<?php endif; ?>
			</li>
			<?php endif; ?>

			<?php if($this->item->params->get('itemEmailButton') && (!JRequest::getInt('print')) ): ?>
			<!-- Email Button -->
			<li>
				<a class="itemEmailLink" onclick="window.open(this.href,'win2','width=400,height=350,menubar=yes,resizable=yes'); return false;" href="<?php echo $this->item->emailLink; ?>">
					<span><?php echo JText::_('E-mail'); ?></span>
				</a>
			</li>
			<?php endif; ?>

			<?php if($this->item->params->get('itemSocialButton') && !is_null($this->item->params->get('socialButtonCode', NULL))): ?>
			<!-- Item Social Button -->
			<li>
				<?php echo $this->item->params->get('socialButtonCode'); ?>
			</li>
			<?php endif; ?>
			
			<?php if($this->item->params->get('itemVideoAnchor') && !empty($this->item->video)): ?>
			<!-- Anchor link to item video below - if it exists -->
			<li>
				<a class="itemVideoLink" href="<?php echo $this->item->link; ?>#itemVideoAnchor"><?php echo JText::_('Video'); ?></a>
			</li>
			<?php endif; ?>
			
			<?php if($this->item->params->get('itemImageGalleryAnchor') && !empty($this->item->gallery)): ?>
			<!-- Anchor link to item image gallery below - if it exists -->
			<li>
				<a class="itemImageGalleryLink" href="<?php echo $this->item->link; ?>#itemImageGalleryAnchor"><?php echo JText::_('Image Gallery'); ?></a>
			</li>
			<?php endif; ?>
			
			<?php if($this->item->params->get('itemCommentsAnchor') && ( ($this->item->params->get('comments') == '2' && !$this->user->guest) || ($this->item->params->get('comments') == '1')) ): ?>
			<!-- Anchor link to comments below - if enabled -->
			<li>
				<?php if($this->item->numOfComments > 0): ?>
				<a class="itemCommentsLink" href="<?php echo $this->item->link; ?>#itemCommentsAnchor">
					<span><?php echo $this->item->numOfComments; ?></span> <?php echo ($this->item->numOfComments>1) ? JText::_('comments') : JText::_('comment'); ?>
				</a>
				<?php else: ?>
				<a class="itemCommentsLink" href="<?php echo $this->item->link; ?>#itemCommentsAnchor">
					<?php echo JText::_('Be the first to comment!'); ?>
				</a>
				<?php endif; ?>
			</li>
			<?php endif; ?>
		</ul>
		<div class="clr"></div>
  </div>
	<?php endif; ?>

	<?php if($this->item->params->get('itemRating')): ?>
	<!-- Item Rating -->
	<div class="itemRatingBlock">
		<span><?php echo JText::_('Rate this item'); ?></span> 
		<div class="itemRatingForm">
			<ul class="itemRatingList">
				<li class="itemCurrentRating" id="itemCurrentRating<?php echo $this->item->id; ?>" style="width:<?php echo $this->item->votingPercentage; ?>%;"></li>
				<li><a href="#" rel="<?php echo $this->item->id; ?>" title="<?php echo JText::_('1 star out of 5'); ?>" class="one-star">1</a></li>
				<li><a href="#" rel="<?php echo $this->item->id; ?>" title="<?php echo JText::_('2 stars out of 5'); ?>" class="two-stars">2</a></li>
				<li><a href="#" rel="<?php echo $this->item->id; ?>" title="<?php echo JText::_('3 stars out of 5'); ?>" class="three-stars">3</a></li>
				<li><a href="#" rel="<?php echo $this->item->id; ?>" title="<?php echo JText::_('4 stars out of 5'); ?>" class="four-stars">4</a></li>
				<li><a href="#" rel="<?php echo $this->item->id; ?>" title="<?php echo JText::_('5 stars out of 5'); ?>" class="five-stars">5</a></li>
			</ul>
			<div id="itemRatingLog<?php echo $this->item->id; ?>" class="itemRatingLog"><?php echo $this->item->numOfvotes; ?></div>
			<div class="clr"></div>
		</div>
		<div class="clr"></div>
	</div>
	<?php endif; ?>

  <div class="itemBody">

	  <!-- Plugins: BeforeDisplayContent -->
	  <?php echo $this->item->event->BeforeDisplayContent; ?>
	  
	  <!-- K2 Plugins: K2BeforeDisplayContent -->
	  <?php echo $this->item->event->K2BeforeDisplayContent; ?>

	  <?php if($this->item->params->get('itemImage') && !empty($this->item->image)): ?>
	  <!-- Item Image -->
	  <div class="itemImageBlock">
		  <span class="itemImage">
		  	<a class="modal" href="<?php echo $this->item->imageXLarge; ?>" title="<?php echo JText::_('Click to preview image'); ?>">
		  		<img src="<?php echo $this->item->image; ?>" alt="<?php if(!empty($this->item->image_caption)) echo $this->item->image_caption; else echo $this->item->title; ?>" />
		  	</a>
		  </span>
		  
		  <?php if($this->item->params->get('itemImageMainCaption') && !empty($this->item->image_caption)): ?>
		  <!-- Image caption -->
		  <span class="itemImageCaption"><?php echo $this->item->image_caption; ?></span>
		  <?php endif; ?>
		  
		  <?php if($this->item->params->get('itemImageMainCredits') && !empty($this->item->image_credits)): ?>
		  <!-- Image credits -->
		  <span class="itemImageCredits"><?php echo $this->item->image_credits; ?></span>
		  <?php endif; ?>
		  
		  <div class="clr"></div>
	  </div>
	  <?php endif; ?>
	  
	  <?php if(!empty($this->item->fulltext)): ?>
	  <?php if($this->item->params->get('itemIntroText')): ?>
	  <!-- Item introtext -->
	  <div class="itemIntroText">
	  	<?php echo $this->item->introtext; ?>
	  </div>
	  <?php endif; ?>

	  <?php if($this->item->params->get('itemFullText')): ?>
	  <!-- Item fulltext -->
	  <div class="itemFullText">
	  	<?php echo $this->item->fulltext; ?>
	  </div>
	  <?php endif; ?>
	  <?php else: ?>
	  <!-- Item text -->
	  <div class="itemFullText">
	  	<?php echo $this->item->introtext; ?>
	  </div>
	  <?php endif; ?>
		
		<div class="clr"></div>

	  <?php if($this->item->params->get('itemExtraFields') && count($this->item->extra_fields)): ?>
	  <!-- Item extra fields -->  
	  <div class="itemExtraFields">
	  	<h3><?php echo JText::_('Additional Info'); ?></h3>
	  	<ul>
			<?php foreach ($this->item->extra_fields as $key=>$extraField):?>
			<li class="<?php echo ($key%2) ? "odd" : "even"; ?> type<?php echo ucfirst($extraField->type); ?> group<?php echo $extraField->group; ?>">
				<span class="itemExtraFieldsLabel"><?php echo $extraField->name; ?>:</span>
				<span class="itemExtraFieldsValue"><?php echo $extraField->value; ?></span>
				<br class="clr" />			
			</li>
			<?php endforeach; ?>
			</ul>
	    <div class="clr"></div>
	  </div>
	  <?php endif; ?>
	  
		<?php if($this->item->params->get('itemDateModified')):?>
		<!-- Item date modified -->
		<?php if($this->item->created != $this->item->modified): ?>
		<span class="itemDateModified">
			<?php echo JText::_('Last modified on'); ?> <?php echo JHTML::_('date', $this->item->modified, JText::_('DATE_FORMAT_LC2')); ?> 
		</span>
		<?php endif; ?>
		<?php endif; ?>

	  <!-- Plugins: AfterDisplayContent -->
	  <?php echo $this->item->event->AfterDisplayContent; ?>
	  
	  <!-- K2 Plugins: K2AfterDisplayContent -->
	  <?php echo $this->item->event->K2AfterDisplayContent; ?>

	  <div class="clr"></div>
  </div>

  <?php if(
  $this->item->params->get('itemHits') || 
  $this->item->params->get('itemTwitterLink') || 
  $this->item->params->get('itemCategory') || 
  $this->item->params->get('itemTags') || 
  $this->item->params->get('itemShareLinks') || 
  $this->item->params->get('itemAttachments')
  ): ?>
  <div class="itemLinks">

		<?php if($this->item->params->get('itemHits') || $this->item->params->get('itemTwitterLink')): ?>
		<div class="itemHitsTwitter">
			<?php if($this->item->params->get('itemHits')): ?>
			<!-- Item Hits -->
			<span class="itemHits">
				<?php echo JText::_('Read'); ?> <b><?php echo $this->item->hits; ?></b> <?php echo JText::_('times'); ?>
			</span>
			<?php endif; ?>
		
			<?php if($this->item->params->get('itemTwitterLink') && $this->item->params->get('twitterUsername')): ?>
			<!-- Twitter Link -->
			<span class="itemTwitterLink">
				<a title="<?php echo JText::_('Like this? Tweet it to your followers!'); ?>" href="<?php echo $this->item->twitterURL; ?>" target="_blank">
					<?php echo JText::_('Like this? Tweet it to your followers!'); ?>
				</a>
			</span>
			<?php endif; ?>
			
			<div class="clr"></div>
		</div>
		<?php endif; ?>

		<?php if($this->item->params->get('itemCategory')): ?>
		<!-- Item category name -->
		<div class="itemCategory">
			<span><?php echo JText::_('Published in'); ?></span>
			<a href="<?php echo $this->item->category->link; ?>"><?php echo $this->item->category->name; ?></a>
		</div>
		<?php endif; ?>
		
	  <?php if($this->item->params->get('itemTags') && count($this->item->tags)): ?>
	  <!-- Item tags -->
	  <div class="itemTagsBlock">
		  <span><?php echo JText::_("Tagged under"); ?></span>
		  <ul class="itemTags">
		    <?php foreach ($this->item->tags as $tag): ?>
		    <li><a href="<?php echo $tag->link; ?>"><?php echo $tag->name; ?></a></li>
		    <?php endforeach; ?>
		  </ul>
		  <div class="clr"></div>
	  </div>
	  <?php endif; ?>

	  <?php if($this->item->params->get('itemShareLinks')): ?>
	  <!-- Item social links -->
		<div class="itemSocialLinksBlock">
			<span><?php echo JText::_("Social sharing"); ?></span>
			<ul class="itemSocialLinks">
				<li><a class="delicious" title="<?php echo JText::_("Add to Delicious"); ?>" href="http://del.icio.us/post?url=<?php echo $this->item->socialLink; ?>&amp;title=<?php echo urlencode($this->item->title); ?>" target="_blank"><span><?php echo JText::_("Add to Delicious"); ?></span></a></li>
				<li><a class="digg" title="<?php echo JText::_("Digg this"); ?>" href="http://digg.com/submit?url=<?php echo $this->item->socialLink; ?>&amp;title=<?php echo urlencode($this->item->title); ?>" target="_blank"><span><?php echo JText::_("Digg this"); ?></span></a></li>
				<li><a class="reddit" title="<?php echo JText::_("Add to Reddit"); ?>" href="http://reddit.com/submit?url=<?php echo $this->item->socialLink; ?>&amp;title=<?php echo urlencode($this->item->title); ?>" target="_blank"><span><?php echo JText::_("Add to Reddit"); ?></span></a></li>
				<li><a class="stumble" title="<?php echo JText::_("Add to StumbleUpon"); ?>" href="http://www.stumbleupon.com/submit?url=<?php echo $this->item->socialLink; ?>&amp;title=<?php echo urlencode($this->item->title); ?>" target="_blank"><span><?php echo JText::_("Add to StumbleUpon"); ?></span></a></li>
				<li><a class="facebook" title="<?php echo JText::_("Add to Facebook"); ?>" href="http://www.facebook.com/share.php?u=<?php echo $this->item->socialLink; ?>&amp;t=<?php echo urlencode($this->item->title); ?>" target="_blank"><span><?php echo JText::_("Add to Facebook"); ?></span></a></li>
				<li><a class="myspace" title="<?php echo JText::_("Add to MySpace"); ?>" href="http://www.myspace.com/Modules/PostTo/Pages/?l=3&amp;u=<?php echo $this->item->socialLink; ?>&amp;t=<?php echo urlencode($this->item->title); ?>" target="_blank"><span><?php echo JText::_("Add to MySpace"); ?></span></a></li>
				<li><a class="technorati" title="<?php echo JText::_("Add to Technorati"); ?>" href="http://www.technorati.com/faves?add=<?php echo $this->item->socialLink; ?>" target="_blank"><span><?php echo JText::_("Add to Technorati"); ?></span></a></li>
				<li class="clr"></li>
			</ul>
			<div class="clr"></div>
		</div>
	  <?php endif; ?>
	  
	  <?php if($this->item->params->get('itemAttachments') && count($this->item->attachments)): ?>
	  <!-- Item attachments -->
	  <div class="itemAttachmentsBlock">
		  <span><?php echo JText::_("Download attachments:"); ?></span>
		  <ul class="itemAttachments">
		    <?php foreach ($this->item->attachments as $attachment): ?>
		    <li>
			    <a title="<?php echo htmlentities($attachment->titleAttribute, ENT_QUOTES, 'UTF-8'); ?>" href="<?php echo JRoute::_('index.php?option=com_k2&view=item&task=download&id='.$attachment->id); ?>">
			    	<?php echo $attachment->title ; ?>
			    </a>
			    <?php if($this->item->params->get('itemAttachmentsCounter')): ?>
			    <span>(<?php echo $attachment->hits; ?> <?php echo (count($attachment->hits)==1) ? JText::_("download") : JText::_("downloads"); ?>)</span>
			    <?php endif; ?>
		    </li>
		    <?php endforeach; ?>
		  </ul>
	  </div>
	  <?php endif; ?>

		<div class="clr"></div>
  </div>
  <?php endif; ?>  
  
  <?php if($this->item->params->get('itemAuthorBlock') && empty($this->item->created_by_alias)):?>
  <!-- Author Block -->
  <div class="itemAuthorBlock">

  	<?php if($this->item->params->get('itemAuthorImage') && !empty($this->item->author->avatar)):?>
  	<img class="itemAuthorAvatar" src="<?php echo $this->item->author->avatar; ?>" alt="<?php echo $this->item->author->name; ?>" />
  	<?php endif; ?>
  	
    <div class="itemAuthorDetails">
      <h3 class="itemAuthorName">
      	<a href="<?php echo $this->item->author->link; ?>"><?php echo $this->item->author->name; ?></a>
      </h3>
      
      <?php if($this->item->params->get('itemAuthorDescription') && !empty($this->item->author->profile->description)):?>
      <p><?php echo $this->item->author->profile->description; ?></p>
      <?php endif; ?>
      
      <?php if($this->item->params->get('itemAuthorURL') && !empty($this->item->author->profile->url)):?>
      <span class="itemAuthorUrl"><?php echo JText::_("Website:"); ?> <a href="<?php echo $this->item->author->profile->url; ?>" target="_blank"><?php echo str_replace('http://','',$this->item->author->profile->url); ?></a></span>
      <?php endif; ?>
      
      <?php if($this->item->params->get('itemAuthorEmail')):?>
      <span class="itemAuthorEmail"><?php echo JText::_("E-mail:"); ?> <?php echo JHTML::_('Email.cloak', $this->item->author->email); ?></span>
      <?php endif; ?>
            
    </div>
    <div class="clr"></div>
  </div>  
  <?php endif; ?>

  <?php if($this->item->params->get('itemAuthorLatest') && empty($this->item->created_by_alias) && isset($this->authorLatestItems)): ?>
  <!-- Latest items from author -->
	<div class="itemAuthorLatest">
		<h3><?php echo JText::_("Latest from"); ?> <?php echo $this->item->author->name; ?></h3>
		<ul>
			<?php foreach($this->authorLatestItems as $key=>$item): ?>
			<li class="<?php echo ($key%2) ? "odd" : "even"; ?>">
				<a href="<?php echo $item->link ?>"><?php echo $item->title; ?></a>
			</li>
			<?php endforeach; ?>
		</ul>
		<div class="clr"></div>
	</div>
	<?php endif; ?>

  <?php if($this->item->params->get('itemRelated') && isset($this->relatedItems)): ?>
  <!-- Related items by tag -->
	<div class="itemRelated">
		<h3><?php echo JText::_("Related items (by tag)"); ?></h3>
		<ul>
			<?php foreach($this->relatedItems as $key=>$item): ?>
			<li class="<?php echo ($key%2) ? "odd" : "even"; ?>">
				<a href="<?php echo $item->link ?>"><?php echo $item->title; ?></a>
			</li>
			<?php endforeach; ?>
		</ul>
		<div class="clr"></div>
	</div>
	<?php endif; ?>

	<div class="clr"></div>

  <?php if($this->item->params->get('itemVideo') && !empty($this->item->video)): ?>
  <!-- Item video -->
  <a name="itemVideoAnchor" id="itemVideoAnchor"></a>
  <div class="itemVideoBlock">
  	<h3><?php echo JText::_('Related Video'); ?></h3>
	  <span class="itemVideo"><?php echo $this->item->video; ?></span>
	  
	  <?php if($this->item->params->get('itemVideoCaption') && !empty($this->item->video_caption)): ?>
	  <span class="itemVideoCaption"><?php echo $this->item->video_caption; ?></span>
	  <?php endif; ?>
	  
	  <?php if($this->item->params->get('itemVideoCredits') && !empty($this->item->video_credits)): ?>
	  <span class="itemVideoCredits"><?php echo $this->item->video_credits; ?></span>
	  <?php endif; ?>
	  
	  <div class="clr"></div>
  </div>
  <?php endif; ?>
  
  <?php if($this->item->params->get('itemImageGallery') && !empty($this->item->gallery)): ?>
  <!-- Item image gallery -->
  <a name="itemImageGalleryAnchor" id="itemImageGalleryAnchor"></a>
  <div class="itemImageGallery">
	  <h3><?php echo JText::_('Image Gallery'); ?></h3>
	  <?php echo $this->item->gallery; ?>
  </div>
  <?php endif; ?>

  <?php if($this->item->params->get('itemNavigation') && !JRequest::getCmd('print') && (isset($this->item->nextLink) || isset($this->item->previousLink))): ?>
  <!-- Item navigation -->
  <div class="itemNavigation">
  	<span class="itemNavigationTitle"><?php echo JText::_('More in this category:'); ?></span>
	
		<?php if(isset($this->item->previousLink)): ?>
		<a class="itemPrevious" href="<?php echo $this->item->previousLink; ?>">
			&laquo; <?php echo $this->item->previousTitle; ?>
		</a>
		<?php endif; ?>
		
		<?php if(isset($this->item->nextLink)): ?>
		<a class="itemNext" href="<?php echo $this->item->nextLink; ?>">
			<?php echo $this->item->nextTitle; ?> &raquo;
		</a>
		<?php endif; ?>
		
  </div>
  <?php endif; ?>

  <!-- Plugins: AfterDisplay -->
  <?php echo $this->item->event->AfterDisplay; ?>
  
  <!-- K2 Plugins: K2AfterDisplay -->
  <?php echo $this->item->event->K2AfterDisplay; ?>
  
 <?php if(
 $this->item->params->get('itemComments') && !JRequest::getInt('print') && ($this->item->params->get('comments') == '1' || ($this->item->params->get('comments') == '2'))):?>
  <!-- Item comments -->
  <a name="itemCommentsAnchor" id="itemCommentsAnchor"></a>
  
  <div class="itemComments">
  
	  <?php if($this->item->params->get('commentsFormPosition')=='above' && $this->item->params->get('itemComments') && !JRequest::getInt('print') && ($this->item->params->get('comments') == '1' || ($this->item->params->get('comments') == '2' && K2HelperPermissions::canAddComment($this->item->catid)))): ?>
	  <!-- Item comments form -->
	  <div class="itemCommentsForm">
	  	<?php echo $this->loadTemplate('comments_form'); ?>
	  </div>
	  <?php endif; ?>

	  <?php if($this->item->numOfComments>0 && $this->item->params->get('itemComments') && !JRequest::getInt('print') && ($this->item->params->get('comments') == '1' || ($this->item->params->get('comments') == '2'))): ?>
	  <!-- Item user comments -->
	  <h3 class="itemCommentsCounter">
	  	<span><?php echo $this->item->numOfComments; ?></span> <?php echo ($this->item->numOfComments>1) ? JText::_('comments') : JText::_('comment'); ?>
	  </h3>
	  
	  <ul class="itemCommentsList">
	    <?php foreach ($this->item->comments as $key=>$comment): ?>
	    <li class="<?php echo ($key%2) ? "odd" : "even"; ?>">
	    
	    	<span class="commentLink">
		    	<a href="<?php echo $this->item->link; ?>#comment<?php echo $comment->id; ?>" name="comment<?php echo $comment->id; ?>" id="comment<?php echo $comment->id; ?>">
		    		<?php echo JText::_('Comment Link'); ?>
		    	</a>
		    </span>
		    
				<?php if($comment->userImage):?>
				<img src="<?php echo $comment->userImage; ?>" alt="<?php echo $comment->userName; ?>" width="<?php echo $this->item->params->get('commenterImgWidth'); ?>" />
				<?php endif; ?>
			
				<span class="commentDate">
		    	<?php echo JHTML::_('date', $comment->commentDate, JText::_('DATE_FORMAT_LC2')); ?>
		    </span>
		    
		    <span class="commentAuthorName">
			    <?php echo JText::_("posted by"); ?>
			    <?php if(!empty($comment->userLink)): ?>
			    <a href="<?php echo $comment->userLink; ?>" title="<?php echo $comment->userName; ?>">
			    	<?php echo $comment->userName; ?>
			    </a>
			    <?php else: ?>
			    <?php echo $comment->userName; ?>
			    <?php endif; ?>
		    </span>
		    
		    <p><?php echo $comment->commentText; ?></p>
		    
		    <span class="commentAuthorEmail">
		    	<?php echo JHTML::_('Email.cloak', $comment->commentEmail, 0); ?>
		    </span>
		    
				<br class="clr" />
	    </li>
	    <?php endforeach; ?>
	  </ul>
	  
	  <div class="itemCommentsPagination">
	  	<?php echo $this->pagination->getPagesLinks(); ?>
	  	<div class="clr"></div>
	  </div>
		<?php endif; ?>

		<?php if($this->item->params->get('commentsFormPosition')=='below' && $this->item->params->get('itemComments') && !JRequest::getInt('print') && ($this->item->params->get('comments') == '1' || ($this->item->params->get('comments') == '2' && K2HelperPermissions::canAddComment($this->item->catid)))): ?>
	  <!-- Item comments form -->
	  <div class="itemCommentsForm">
	  	<?php echo $this->loadTemplate('comments_form'); ?>
	  </div>
	  <?php endif; ?>
	  
  </div>
  <?php endif; ?>

	<div class="itemBackToTop">
		<a href="<?php echo $this->item->link; ?>#startOfPageId<?php echo JRequest::getInt('id'); ?>"><?php echo JText::_("back to top"); ?></a>
	</div>
	
	<div class="clr"></div>
</div>
<!-- End K2 Item Layout -->
