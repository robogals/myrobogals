	<?php // @version $Id: default_results.php 11917 2009-05-29 19:37:05Z ian $
defined('_JEXEC') or die('Restricted access');

?>

<?php if (!empty($this->searchword)) : ?>
<div class="searchintro<?php echo $this->escape($this->params->get('pageclass_sfx')) ?>">
	<p>
		<?php echo JText::_('Search Keyword') ?> <strong><?php echo $this->escape($this->searchword) ?></strong>
		<?php echo $this->result ?>
	</p>
	<p>
		<div class="readon-wrap1"><div class="readon1-l"></div><a href="#form1" class="readon-main" onclick="document.getElementById('search_searchword').focus();return false" onkeypress="document.getElementById('search_searchword').focus();return false"><span class="readon1-m"><span class="readon1-r"><?php echo JText::_('Search_again') ?></span></span></a></div><div class="clr"></div>
	</p>
</div>
<?php endif; ?>

<?php if (count($this->results)) : ?>
<div class="sidemod-title"><h3 class="side"><?php echo JText :: _('Search_result'); ?></h3></div>
<div class="results">
	<?php $start = $this->pagination->limitstart + 1; ?>
	<ol class="list" start="<?php echo  $start ?>">
		<?php foreach ($this->results as $result) : ?>
		<?php
		$text = $result->text;
		$text = preg_replace( '/\[.+?\]/', '', $text);
		?>	
		<li>
			<?php if ($result->href) : ?>
			<h4>
				<a href="<?php echo JRoute :: _($result->href) ?>" <?php echo ($result->browsernav == 1) ? 'target="_blank"' : ''; ?> >
					<?php echo $this->escape($result->title); ?></a>
			</h4>
			<?php endif; ?>
			<?php if ($result->section) : ?>
			<p><?php echo JText::_('Category') ?>:
				<span class="small">
					<?php echo $this->escape($result->section); ?>
				</span>
			</p>
			<?php endif; ?>

			<div class="description">
				<?php echo $text; ?>
			</div>
			<span class="small">
				<?php echo $result->created; ?>
			</span>
		</li>
		<?php endforeach; ?>
	</ol>
	<?php echo $this->pagination->getPagesLinks(); ?>
</div>
<?php else: ?>
<div class="noresults"></div>
<?php endif; ?>