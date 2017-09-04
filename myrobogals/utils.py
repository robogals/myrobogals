from myrobogals.rgchapter.models import Chapter
from myrobogals.rgprofile.models import Position
from myrobogals.rgprofile.models import User


def hierarchicalexec(execuser, targetchapter):
    """
    Returns true if execuser is in a chapter that is a transitive parent of the targetchapter.

    Example: Global -> APAC -> {Melbourne, Brisbane, Perth, ..}
    If an execuser is in the APAC chapter, this will return true for APAC, and all children of APAC.
    If an execuser is in the Global chapter, this will return true for Global, and descendents children of Global.
    """
    print 'hello'
    return execuser.chapter == targetchapter or execuser.chapter == targetchapter.parent or execuser.chapter == targetchapter.parent.parent
