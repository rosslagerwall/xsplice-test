import xsplicetest

# Test the exception handling code
# Write an invalid msr to generate a (caught) exception).

class Testcase(xsplicetest._Testcase):
    def __init__(self, host, patches):
        super().__init__(host, patches)

    def run(self):
        super().run()

        self.load("exception")
        self.record_log()
        self.runcmd("xl debug-key h")
        # requires a debug hv
        self.assert_log("traps.c.*GPF")
        self.assert_log("ret = -14")
