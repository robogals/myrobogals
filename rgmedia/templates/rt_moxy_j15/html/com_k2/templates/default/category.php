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

<!-- Start K2 Category Layout -->
<div id="k2Container" class="itemListView<?php if($this->params->get('pageclass_sfx')) echo ' '.$this->params->get('pageclass_sfx'); ?>">
	
	<?php if($this->params->get('catFeedLink')): ?>
	<!-- RSS feed icon -->
	<div class="k2FeedIcon">
		<a href="<?php echo $this->feed; ?>" title="<?php echo JText::_('Subscribe to this RSS feed'); ?>">
			<span><?php echo JText::_('Subscribe to this RSS feed'); ?></span>
		</a>
		<div class="clr"></div>
	</div>
	<?php endif; ?>
	
	<?php if($this->params->get('show_page_title')): ?>
	<!-- Page title -->
	<div class="componentheading<?php echo $this->params->get('pageclass_sfx')?>">
		<?php echo $this->escape($this->params->get('page_title')); ?>
	</div>
	<?php endif; ?>
	
	
	<?php if(isset($this->category) || ( $this->params->get('subCategories') && isset($this->subCategories) && count($this->subCategories) )): ?>
	<!-- Blocks for current category and subcategories -->
	<div class="itemListCategoriesBlock">
	
		<?php if(isset($this->category) && ( $this->params->get('catImage') || $this->params->get('catTitle') || $this->params->get('catDescription') || $this->category->event->K2CategoryDisplay )): ?>
		<!-- Category block -->
		<div class="itemListCategory">
		
			<?php if(isset($this->addLink)): ?>
			<!-- Item add link -->
			<span class="catItemAddLink">
				<a class="modal" rel="{handler:'iframe',size:{x:990,y:650}}" href="<?php echo $this->addLink; ?>">
					<?php echo JText::_('Add a new item in this category'); ?>
				</a>
			</span>
			<?php endif; ?>
			
			<?php if($this->params->get('catImage')): ?>
			<!-- Category image -->
			<img alt="<?php echo $this->category->name; ?>" src="<?php echo $this->category->image; ?>" />
			<?php endif; ?>
			
			<?php if($this->params->get('catTitle')): ?>
			<!-- Category title -->
			<h2><?php echo $this->category->name; ?><?php if($this->params->get('catTitleItemCounter')) echo ' ('.$this->pagination->total.')'; ?></h2>
			<?php endif; ?>
			
			<?php if($this->params->get('catDescription')): ?>
			<!-- Category description -->
			<p><?php echo $this->category->description; ?></p>
			<?php endif; ?>
			
			<!-- K2 Plugins: K2CategoryDisplay -->
			<?php echo $this->category->event->K2CategoryDisplay; ?>
			
			<div class="clr"></div>
		</div>
		<?php endif; ?>
		
		<?php if($this->params->get('subCategories') && isset($this->subCategories) && count($this->subCategories)): ?>
		<!-- Subcategories -->
		<div class="itemListSubCategories">
			<h3><?php echo JText::_('Children categories'); ?></h3>
			
			<?php foreach($this->subCategories as $key=>$subCategory): ?>
			<div class="subCategoryContainer" style="width:<?php echo number_format(100/$this->params->get('subCatColumns'), 1); ?>%;">
				<div class="subCategory">
					<?php if($this->params->get('subCatImage')): ?>
					<!-- Subcategory image -->
					<a class="subCategoryImage" href="<?php echo $subCategory->link; ?>">
						<img alt="<?php echo $subCategory->name; ?>" src="<?php echo $subCategory->image; ?>" />
					</a>
					<?php endif; ?>
				
					<?php if($this->params->get('subCatTitle')): ?>
					<!-- Subcategory title -->
					<h2>
						<a href="<?php echo $subCategory->link; ?>">
							<?php echo $subCategory->name; ?><?php if($this->params->get('subCatTitleItemCounter')) echo ' ('.$subCategory->numOfItems.')'; ?>
						</a>
					</h2>
					<?php endif; ?>
				
					<?php if($this->params->get('subCatDescription')): ?>
					<!-- Subcategory description -->
					<p><?php echo $subCategory->description; ?></p>
					<?php endif; ?>
					
					<!-- Subcategory more... -->
					<a class="subCategoryMore" href="<?php echo $subCategory->link; ?>">
						<?php echo JText::_('View items...'); ?>
					</a>
					
					<div class="clr"></div>
				</div>
			</div>
			<?php if(($key+1)%($this->params->get('subCatColumns'))==0): ?>
			<div class="clr"></div>
			<?php endif; ?>
			<?php endforeach; ?>
			
			<div class="clr"></div>
		</div>
		<?php endif; ?>

	</div>
	<?php endif; ?>
	
	
	
	<?php if((isset($this->leading) || isset($this->primary) || isset($this->secondary) || isset($this->links)) && (count($this->leading) || count($this->primary) || count($this->secondary) || count($this->links))): ?>
	<!-- Item list -->
	<div class="itemList">
		
		<?php if(isset($this->leading) && count($this->leading)): ?>
		<!-- Leading items -->
		<div id="itemListLeading">
			<?php foreach($this->leading as $key=>$item): ?>
			<div class="itemContainer" style="width:<?php echo number_format(100/$this->params->get('num_leading_columns'), 1); ?>%;">
			<?php
				// Load category_item.php by default
				$this->item=$item;
				echo $this->loadTemplate('item');
			?>
			</div>
			<?php if(($key+1)%($this->params->get('num_leading_columns'))==0): ?>
			<div class="clr"></div>
			<?php endif; ?>
			<?php endforeach; ?>
			<div class="clr"></div>
		</div>
		<?php endif; ?>
		
		<?php if(isset($this->primary) && count($this->primary)): ?>
		<!-- Primary items -->
		<div id="itemListPrimary">
			<?php foreach($this->primary as $key=>$item): ?>
			<div class="itemContainer" style="width:<?php echo number_format(100/$this->params->get('num_primary_columns'), 1); ?>%;">
			<?php
				// Load category_item.php by default
				$this->item=$item;
				echo $this->loadTemplate('item');
			?>
			</div>
			<?php if(($key+1)%($this->params->get('num_primary_columns'))==0): ?>
			<div class="clr"></div>
			<?php endif; ?>
			<?php endforeach; ?>
			<div class="clr"></div>
		</div>
		<?php endif; ?>

		<?php if(isset($this->secondary) && count($this->secondary)): ?>
		<!-- Secondary items -->
		<div id="itemsListSecondary">
			<?php foreach($this->secondary as $key=>$item): ?>
			<div class="itemContainer" style="width:<?php echo number_format(100/$this->params->get('num_secondary_columns'), 1); ?>%;">
			<?php
				// Load category_item.php by default
				$this->item=$item;
				echo $this->loadTemplate('item');
			?>
			</div>
			<?php if(($key+1)%($this->params->get('num_secondary_columns'))==0): ?>
			<div class="clr"></div>
			<?php endif; ?>
			<?php endforeach; ?>
			<div class="clr"></div>
		</div>
		<?php endif; ?>

		<?php if(isset($this->links) && count($this->links)): ?>
		<!-- Link items -->
		<div id="itemListLinks">
			<h4><?php echo JText::_('More...'); ?></h4>
			<?php foreach($this->links as $key=>$item): ?>
			<div class="itemContainer" style="width:<?php echo number_format(100/$this->params->get('num_links_columns'), 1); ?>%;">
			<?php
				// Load category_item_links.php by default
				$this->item=$item;
				echo $this->loadTemplate('item_links');
			?>
			</div>
			<?php if(($key+1)%($this->params->get('num_links_columns'))==0): ?>
			<div class="clr"></div>
			<?php endif; ?>
			<?php endforeach; ?>
			<div class="clr"></div>
		</div>
		<?php endif; ?>
		
	</div>
	
	<!-- Pagination -->
	<?php if(count($this->pagination->getPagesLinks())): ?>
	<div class="k2Pagination">
		<?php if($this->params->get('catPagination')) echo $this->pagination->getPagesLinks(); ?>
		<div class="clr"></div>
		<?php if($this->params->get('catPaginationResults')) echo $this->pagination->getPagesCounter(); ?>
	</div>
	<?php endif; ?>
	
	<?php endif; ?>
</div>
<!-- End K2 Category Layout -->
