from niko.core.plugin import NikoPlugin
from niko.core.decorators import respond_to

class ThanksPlugin(NikoPlugin):

    @respond_to("^(?:thanks|thank you|tx|thx|ty|tyvm)")
    def respond_to_thanks(self, message):
        self.reply(message, "You're welcome!")
