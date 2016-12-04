from niko.core.plugin import NikoPlugin
from niko.core.decorators import respond_to

class MorninPlugin(NikoPlugin):

    @respond_to("^(good )?(morning?)\b")
    #on(Event.CHAT_MESSAGE_NEW, '^(good )?(morning?)\b', False)
    def morning(self, message):
        self.say("mornin', %s" % message.sender.nick, message=message)

    @respond_to("^(good ?|g')?('?night)\b")
    def good_night(self, message):
        now = datetime.datetime.now()
        if now.weekday() == 4:  # Friday
            self.say("have a good weekend!", message=message)
        else:
			self.say("have a good night!", message=message)