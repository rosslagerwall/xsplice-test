import xsplicetest

# Ensure that symbols to existing data are resolved correctly by
# checking that for_each_online_cpu actually finds CPUs online.
# This was provoked by a bug where the embedded symbol table in Xen
# contained incorrect offsets.
# https://github.com/rosslagerwall/xen/commit/bc57134fb2e9e822828b783f6ecc733334e46762

class Testcase(xsplicetest._Testcase):
    def __init__(self, host, patches):
        super().__init__(host, patches)

    def run(self):
        super().run()

        self.load("cpuonline")
        self.record_log()
        self.runcmd("xl debug-key c")
        self.assert_log("got herex")
        self.assert_log("==cpu0==")
