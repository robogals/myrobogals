<?php // @version $Id: default_login.php 12352 2009-06-24 13:52:57Z ian $
defined( '_JEXEC' ) or die( 'Restricted access' );
?>
<div id="main-login-page">
<form action="<?php echo JRoute::_( 'index.php', true, $this->params->get('usesecure')); ?>" method="post" name="login" id="login" class="form-login<?php echo $this->params->get( 'pageclass_sfx' ); ?>">
<?php if ( $this->params->get( 'show_login_title' ) ) : ?>
	<h1 class="componentheading<?php echo $this->params->get( 'pageclass_sfx' ); ?>">
		<?php echo $this->params->get( 'header_login' ); ?>
	</h1>
	<?php endif; ?>
	
	<?php if ( $this->params->get( 'description_login' ) || isset( $this->image ) ) : ?>
		<div class="contentdescription<?php echo $this->params->get( 'pageclass_sfx' );?>">
			<?php if (isset ($this->image)) :
				echo $this->image;
			endif;
			if ($this->params->get('description_login')) : ?>
			<p>
				<?php echo $this->params->get('description_login_text'); ?>
			</p>
			<?php endif;
			if (isset ($this->image)) : ?>
			<div class="wrap_image">&nbsp;</div>
			<?php endif; ?>
		</div>
	<?php endif; ?>
	<fieldset>
		<div class="name">
			<label for="user" ><?php echo JText::_( 'Username' ); ?></label>
			<input type="text" onfocus="if(this.value=='Username') this.value='';" onblur="if(this.value=='') this.value='Username';" alt="Username" value="Username" class="inputbox" name="username" id="user" size="20"/>
		</div>
		<div class="pass">
			<label for="pass" ><?php echo JText::_( 'Password' ); ?></label>
			<input name="passwd" type="password" class="inputbox" size="20" id="pass" />
		</div>
		<div class="remember">
			<input type="checkbox" name="remember" class="inputbox" value="yes" id="rem" />
			<label for="rem"><?php echo JText::_( 'Remember me' ); ?></label>
		</div>
	</fieldset>
	<p>
		<a href="<?php echo JRoute::_( 'index.php?option=com_user&view=reset#content' ); ?>">
			<?php JPlugin::loadLanguage( 'tpl_beez' ); echo JText::_('Lost Password?'); ?></a>
		<?php if ( $this->params->get( 'registration' ) ) : ?>
		<?php echo JText::_('No account yet?'); ?>
		<a href="<?php echo JRoute::_( 'index.php?option=com_user&view=register#content' ); ?>">
			<?php echo JText::_( 'Register' ); ?></a>
		<?php endif; ?>
	</p>
	<div class="readon-wrap1"><div class="readon1-l"></div><a class="readon-main"><span class="readon1-m"><span class="readon1-r"><input type="submit" name="Submit" class="button" value="<?php echo JText::_('Login'); ?>" /></span></span></a></div><div class="clr"></div>
	<noscript><?php echo JText::_( 'WARNJAVASCRIPT' ); ?></noscript>
	<input type="hidden" name="option" value="com_user" />
	<input type="hidden" name="task" value="login" />
	<input type="hidden" name="return" value="<?php echo $this->return; ?>" />
	<?php echo JHTML::_( 'form.token' ); ?>
</form>
</div>