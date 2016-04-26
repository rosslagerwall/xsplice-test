import xsplicetest

# Test symbol resolution during backtrace
# (part1):
# for patched existing global/static functions
# for new global/static functions
# (part2):
# for patched new global/static functions

class Testcase(xsplicetest._Testcase):
    def __init__(self, host, patches):
        super().__init__(host, patches)

    def run(self):
        super().run()

        self.load("backtrace1")
        self.record_log()
        self.runcmd("xl debug-key h")
        self.assert_log("Xen WARN at keyhandler.c")
        self.assert_log("RIP.*new_global.*[backtrace1]")
        self.assert_log("new_global.*[backtrace1]")
        self.assert_log("get_random.*[backtrace1]")
        self.assert_log("keyhandler.c#new_static.*[backtrace1]")
        self.assert_log("keyhandler.c#show_handlers.*[backtrace1]")


        self.record_log()
        self.load("backtrace2")
        self.runcmd("xl debug-key h")
        self.assert_log("patching new_static")
        self.assert_log("patching new_global")
        self.assert_log("Xen WARN at keyhandler.c")
        self.assert_log("RIP.*new_global.*[backtrace2]")
        self.assert_log("new_global.*[backtrace2]")
        self.assert_log("get_random.*[backtrace1]")
        self.assert_log("keyhandler.c#new_static.*[backtrace2]")
        self.assert_log("keyhandler.c#show_handlers.*[backtrace1]")
