<?php // @version $Id: default.php 11796 2009-05-06 02:03:15Z ian $
defined('_JEXEC') or die('Restricted access');
?>

<?php
$return = base64_encode(base64_decode($return).'#content');

if ($type == 'logout') : ?>
<form action="index.php" method="post" name="login" class="log">
	<?php if ($params->get('greeting')) : ?>
	<p>
	<?php if ($params->get('name')) : {
		echo JText::sprintf( 'HINAME', $user->get('name') );
	} else : {
		echo JText::sprintf( 'HINAME', $user->get('username') );
	} endif; ?>
	</p>
	<?php endif; ?>
	<div class="readon-wrap1"><div class="readon1-l"></div><a class="readon-main"><span class="readon1-m"><span class="readon1-r"><input type="submit" name="Submit" class="button" value="<?php echo JText::_('BUTTON_LOGOUT'); ?>" /></span></span></a></div><div class="clr"></div>
	<input type="hidden" name="option" value="com_user" />
	<input type="hidden" name="task" value="logout" />
	<input type="hidden" name="return" value="<?php echo $return; ?>" />
</form>
<?php else : ?>
<div class="main-login-form">
	<form action="<?php echo JRoute::_( 'index.php', true, $params->get('usesecure')); ?>" method="post" name="login" class="form-login">
		<?php if ($params->get('pretext')) : ?>
		<p>
			<?php echo $params->get('pretext'); ?>
		</p>
		<?php endif; ?>
		<div class="username-block">
			<input name="username" type="text" class="inputbox" value="<?php echo JText::_('Username'); ?>" alt="<?php echo JText::_('Username'); ?>" onblur="if(this.value=='') this.value='<?php echo JText::_('Username'); ?>';" onfocus="if(this.value=='<?php echo JText::_('Username'); ?>') this.value='';" />
		</div>
		<div class="password-block">
			<input type="password" name="passwd" class="inputbox" alt="<?php echo JText::_('Password'); ?>" />
		</div>
		<div class="login-extras">
			<div class="remember-me">
			<input type="checkbox" name="remember" class="checkbox" value="yes" alt="<?php echo JText::_('Remember me'); ?>" />
			<label class="remember">
				<?php echo JText::_('Remember me'); ?>
			</label>	
			</div>
			<div class="readon-wrap1"><div class="readon1-l"></div><a class="readon-main"><span class="readon1-m"><span class="readon1-r"><input type="submit" name="Submit" class="button" value="<?php echo JText::_('BUTTON_LOGIN'); ?>" /></span></span></a></div><div class="clr"></div>
			<div class="login-links">
			<p>
				<a href="<?php echo JRoute::_('index.php?option=com_user&view=reset#content'); ?>">
					<?php echo JText::_('FORGOT_YOUR_PASSWORD'); ?></a>
			</p>
			<p>
				<a href="<?php echo JRoute::_('index.php?option=com_user&view=remind#content'); ?>">
					<?php echo JText::_('FORGOT_YOUR_USERNAME'); ?></a>
			</p>
			</div>
			<?php $usersConfig =& JComponentHelper::getParams('com_users');
			if ($usersConfig->get('allowUserRegistration')) : ?>
			<p>
				<?php echo JText::_('No account yet?'); ?>
		<a href="<?php echo JRoute::_('index.php?option=com_user&view=register#content'); ?>">
					<?php echo JText::_('Register'); ?></a>
			</p>
			<?php endif;
			echo $params->get('posttext'); ?>
			<input type="hidden" name="option" value="com_user" />
			<input type="hidden" name="task" value="login" />
			<input type="hidden" name="return" value="<?php echo $return; ?>" />
			<?php echo JHTML::_( 'form.token' ); ?>
		</div>
	</form>
</div>
<?php endif;
