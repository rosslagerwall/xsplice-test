import xsplicetest

# Introduce some new static and global data
#
# Ensure that the data is initialized to the expected values.
# Access the data from a different compilation unit.
#
# Access previously introduced data from a different compilation unit
#
# Repatch a function using previously introduced static and
# global data, and continue to use it.

class Testcase(xsplicetest._Testcase):
    def __init__(self, host, patches):
        super().__init__(host, patches)

    def run(self):
        super().run()

        self.load("vars")
        self.record_log()
        self.runcmd("xl debug-key h")
        self.assert_log("global_x = 0")
        self.assert_log("global_z = 42")
        self.assert_log("static_x = 0")
        self.assert_log("static_z = 43")

        self.record_log()
        self.runcmd("xl debug-key h")
        self.assert_log("global_x = 1")
        self.assert_log("global_z = 43")
        self.assert_log("static_x = 1")
        self.assert_log("static_z = 44")

        self.record_log()
        self.runcmd("xl debug-key s")
        self.assert_log("global_x = 2")
        self.assert_log("global_z = 44")


        self.load("vars2")
        self.record_log()
        self.runcmd("xl debug-key c")
        self.assert_log("global_x = 2")
        self.assert_log("global_y = 0")
        self.assert_log("global_z = 44")

        self.record_log()
        self.runcmd("xl debug-key c")
        self.assert_log("global_x = 3")
        self.assert_log("global_y = 1")
        self.assert_log("global_z = 45")


        self.load("vars3")
        self.runcmd("xl debug-key h")
        self.runcmd("xl debug-key h")
        self.record_log()
        self.runcmd("xl debug-key h")
        self.assert_log("global_x = -10")
        self.assert_log("global_z = 32")
        self.assert_log("static_x = -12")
        self.assert_log("static_z = 31")
        self.assert_log("global_y != 0")
