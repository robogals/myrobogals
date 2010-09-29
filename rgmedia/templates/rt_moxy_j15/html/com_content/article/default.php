<?php // @version $Id: default.php 11917 2009-05-29 19:37:05Z ian $
defined('_JEXEC') or die('Restricted access');
include_once(dirname(__FILE__).DS.'..'.DS.'icon.php');
?>
<div class="<?php echo $this->escape($this->params->get('pageclass_sfx')); ?>">
	<div id="page" class="full-article">
		<?php if (($this->user->authorize('com_content', 'edit', 'content', 'all') || $this->user->authorize('com_content', 'edit', 'content', 'own')) && !($this->print)) : ?>
		<div class="contentpaneopen_edit">
			<?php echo JHTML::_('icon.edit', $this->article, $this->params, $this->access); ?>
		</div>
		<?php endif; ?>

		<?php if ($this->params->get('show_page_title',1) && $this->params->get('page_title') != $this->article->title) : ?>
		<h1 class="componentheading"><?php echo $this->escape($this->params->get('page_title')); ?></h1>
		<?php endif; ?>
		<div class="article-rel-wrapper">
			<?php if ($this->params->get('show_title')) : ?>
			<h2 class="contentheading">
				<?php if ($this->params->get('link_titles') && $this->article->readmore_link != '') : ?>
				<a href="<?php echo $this->article->readmore_link; ?>" class="contentpagetitle"><?php echo $this->escape($this->article->title); ?></a>
				<?php else :
				echo $this->escape($this->article->title);
				endif; ?>
			</h2>
			<?php endif; ?>
	 	</div>
		<?php if (($this->params->get('show_section') && $this->article->sectionid) || ($this->params->get('show_category') && $this->article->catid)) : ?>
		<p class="pageinfo">
			<?php if ($this->params->get('show_section') && $this->article->sectionid) : ?>
			<span>
				<?php if ($this->params->get('link_section')) : ?>
					<?php echo '<a href="'.JRoute::_(ContentHelperRoute::getSectionRoute($this->article->sectionid)).'">'; ?>
				<?php endif; ?>
		<?php echo $this->escape($this->article->section); ?>
				<?php if ($this->params->get('link_section')) : ?>
					<?php echo '</a>'; ?>
				<?php endif; ?>
				<?php if ($this->params->get('show_category')) : ?>
					<?php echo ' - '; ?>
				<?php endif; ?>
			</span>
			<?php endif; ?>
			<?php if ($this->params->get('show_category') && $this->article->catid) : ?>
			<span>
				<?php if ($this->params->get('link_category')) : ?>
					<?php echo '<a href="'.JRoute::_(ContentHelperRoute::getCategoryRoute($this->article->catslug, $this->article->sectionid)).'">'; ?>
				<?php endif; ?>
		<?php echo $this->escape($this->article->category); ?>
				<?php if ($this->params->get('link_category')) : ?>
					<?php echo '</a>'; ?>
				<?php endif; ?>
			</span>
			<?php endif; ?>
		</p>
		<?php endif; ?>
		
		<?php if ((intval($this->article->modified) !=0 && $this->params->get('show_modify_date')) || ($this->params->get('show_author') && ($this->article->author != "")) || ($this->params->get('show_create_date')) || ($this->params->get('show_pdf_icon') || $this->params->get('show_print_icon') || $this->params->get('show_email_icon'))) : ?>
		<div class="article-info-surround">
			<div class="article-info-right">
				<?php if (($this->params->get('show_author')) && ($this->article->author != "")) : ?>
				<span class="createdby">
	<?php JText::printf(($this->article->created_by_alias ? $this->escape($this->article->created_by_alias) : $this->escape($this->article->author))); ?>
				</span>
				<?php endif; ?>
				<p class="buttonheading">
					<?php if ($this->print) :
						echo RokIcon::print_screen($this->article, $this->params, $this->access);
					elseif ($this->params->get('show_pdf_icon') || $this->params->get('show_print_icon') || $this->params->get('show_email_icon')) : ?>
					<?php if ($this->params->get('show_pdf_icon')) :
						echo RokIcon::pdf($this->article, $this->params, $this->access);
					endif;
					if ($this->params->get('show_print_icon')) :
						echo RokIcon::print_popup($this->article, $this->params, $this->access);
					endif;
					if ($this->params->get('show_email_icon')) :
						echo RokIcon::email($this->article, $this->params, $this->access);
					endif;
					endif; ?>
				</p>
			</div>
			<div class="iteminfo">
				<div class="article-info-left">
					<?php if ($this->params->get('show_create_date')) : ?>
					<span class="createdate">
						<span class="date1"><?php echo JHTML::_('date', $this->article->created, JText::_('%b %d')); ?></span>
						<span class="date2"><span class="date-div">|</span><?php echo JHTML::_('date', $this->article->created, JText::_('%H:%M %p')); ?></span>
					</span>
					<?php endif; ?>	
					<div class="clr"></div>
				</div>
				<?php if (intval($this->article->modified) !=0 && $this->params->get('show_modify_date')) : ?>
				<span class="modifydate">
					<?php echo JText::sprintf('LAST_UPDATED2', JHTML::_('date', $this->article->modified, JText::_('DATE_FORMAT_LC2'))); ?>
				</span>
				<?php endif; ?>
			</div>
		</div>
		<?php endif; ?>

		<?php if (!$this->params->get('show_intro')) :
			echo $this->article->event->afterDisplayTitle;
		endif; ?>
		
		<?php if ($this->params->get('show_url') && $this->article->urls) : ?>
		<span class="small">
	<a href="<?php echo $this->escape($this->article->urls); ?>" target="_blank">
		<?php echo $this->escape($this->article->urls); ?></a>
		</span>
		<?php endif; ?>

		<?php if (isset ($this->article->toc)) :
			echo $this->article->toc;
		endif; ?>

		<?php echo JFilterOutput::ampReplace($this->article->text); ?>

		<?php echo $this->article->event->afterDisplayContent; ?>
		<div class="article-ratings">
			<?php echo $this->article->event->beforeDisplayContent; ?>
		</div>
	</div>
</div>