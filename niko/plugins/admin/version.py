# import pkg_resources
from niko.core.plugin import NikoPlugin
from niko.core.decorators import respond_to

class VersionPlugin(NikoPlugin):

    @respond_to("^version$")
    def say_version(self, message):
        version = '2.0.0'#pkg_resources.get_distribution("niko").version
        self.say("I'm running version %s" % version, message=message)