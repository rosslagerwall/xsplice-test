import xsplicetest

# Basic patching testcase.
# Test incremental patching too.

class Testcase(xsplicetest._Testcase):
    def __init__(self, host, patches):
        super().__init__(host, patches)

    def run(self):
        super().run()

        self.load("simple")
        self.record_log()
        self.runcmd("xl debug-key h")
        self.assert_log("PrEsSeD")

        self.load("simple2")
        self.record_log()
        self.runcmd("xl debug-key c")
        self.assert_log("replace test")
