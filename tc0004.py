import xsplicetest

# Verify using WARN works
# This tests the bug frame code

class Testcase(xsplicetest._Testcase):
    def __init__(self, host, patches):
        super().__init__(host, patches)

    def run(self):
        super().run()

        self.load("warn")
        self.record_log()
        self.runcmd("xl debug-key h")
        self.assert_log("Xen WARN at keyhandler.c")
