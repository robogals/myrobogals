from django.core.exceptions import ObjectDoesNotExist

from myrobogals.rgchapter.models import Chapter
from myrobogals.rgprofile.models import Position
from myrobogals.rgprofile.models import User

def get_chapter(chapter_url):
	"""
	Returns the chapter if it exists, None otherwise.
	"""
	try:
		return Chapter.objects.get(myrobogals_url=chapter_url)
	except ObjectDoesNotExist:
		#TODO: log error
		return None


robogalsGlobal = get_chapter('global')
robogalsAPAC = get_chapter('asiapac')
robogalsEMEA = get_chapter('eu')
robogalsNA = get_chapter('na')


def is_president(user, chapter):
	"""
	Returns true if the user is the President of the given chapter, false otherwise.
	"""
	for position in user.cur_positions():
		if position.positionChapter == chapter and position.positionType.description == 'President':
			return True
	return False


def is_executive(user, chapter):
	"""
	Returns true if the user has an executive position in the given chapter, false otherwise.
	"""
	for position in user.cur_positions():
		if position.positionChapter == chapter:
			return True
	return False


def is_regional(user, chapter):
	"""
	Returns true if the user has an executive position in the given chapter's regional team, false otherwise.
	"""
	if chapter.parent == robogalsAPAC or chapter == robogalsAPAC:
		return len(user.cur_positions().filter(positionChapter=robogalsAPAC)) > 0
	if chapter.parent == robogalsEMEA or chapter == robogalsEMEA:
		return len(user.cur_positions().filter(positionChapter=robogalsEMEA)) > 0
	if chapter.parent == robogalsNA or chapter == robogalsNA:
		return len(user.cur_positions().filter(positionChapter=robogalsNA)) > 0
	return False


def is_global(user):
	"""
	Returns true if the user has an executive position in the global team, false otherwise.
	"""
	return len(user.cur_positions().filter(positionChapter=robogalsGlobal)) > 0


def is_executive_or_higher(user, chapter):
	"""
	Returns true if the user has an executive position in the given chapter, 
	chapter's regional team, or the global team, false otherwise.
	"""
	return is_executive(user, chapter) or is_regional(user, chapter) or is_global(user)


def is_regional_or_higher(user, chapter):
	"""
	Returns true if the user has an executive position in the given chapter's 
	regional team or global team, false otherwise.
	"""
	return is_regional(user, chapter) or is_global(user)


def hierarchicalexec(execuser, targetchapter):
    """
    Returns true if execuser is in a chapter that is a transitive parent of the targetchapter.

    Example: Global -> APAC -> {Melbourne, Brisbane, Perth, ..}
    If an execuser is in the APAC chapter, this will return true for APAC, and all children of APAC.
    If an execuser is in the Global chapter, this will return true for Global, and descendents children of Global.
    """
    return execuser.chapter == targetchapter or execuser.chapter == targetchapter.parent or execuser.chapter == targetchapter.parent.parent
