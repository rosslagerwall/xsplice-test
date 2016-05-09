import xsplicetest

# Check that "replace" correctly unloads previously
# applied patches.
# Check that "replace" works when no patches are applied.

class Testcase(xsplicetest._Testcase):
    def __init__(self, host, patches):
        super().__init__(host, patches)

    def check_normal(self):
        self.record_log()
        self.runcmd("xl debug-key h")
        self.runcmd("xl debug-key c")
        self.assert_not_log("PrEsSeD")
        self.assert_not_log("replace test")

    def check_first(self):
        self.record_log()
        self.runcmd("xl debug-key h")
        self.runcmd("xl debug-key c")
        self.assert_log("PrEsSeD")
        self.assert_not_log("replace test")

    def check_second(self):
        self.record_log()
        self.runcmd("xl debug-key h")
        self.runcmd("xl debug-key c")
        self.assert_not_log("PrEsSeD")
        self.assert_log("replace test")

    def run(self):
        super().run()

        self.load("simple")
        self.check_first()

        self.do_upload("simple2")
        self.do_replace("simple2")
        assert self.get_status("simple")[0] == 'CHECKED'
        self.check_second()

        self.do_revert("simple2")
        self.check_normal()

        self.do_replace("simple2")
        self.check_second()
