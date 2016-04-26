import xsplicetest

# Duplicate object symbol test
# Using __func__ generates an object symbol like keyhandler.c#show_handlers.__func__.2142
# If repatching a patch, this might be considered a duplicate symbol.
# Duplicate object symbols are ignored for now.

class Testcase(xsplicetest._Testcase):
    def __init__(self, host, patches):
        super().__init__(host, patches)

    def run(self):
        super().run()

        self.load("dup-rodata")
        self.record_log()
        self.runcmd("xl debug-key h")
        self.assert_log("func: show_handlers")

        self.load("dup-rodata2")
        self.record_log()
        self.runcmd("xl debug-key h")
        self.assert_log("func1: show_handlers")
        self.assert_log("func2: show_handlers")
