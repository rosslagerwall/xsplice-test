import xsplicetest

# Test funcions
# Insert a new global function and call it from within and outside
# the object.
# Insert a new static function and call it.
# Patch an existing static function.
# Patch an existing global function.
# Patch new functions introduced in a previous patch.
# Patch existing functions patching in a previous patch.

class Testcase(xsplicetest._Testcase):
    def __init__(self, host, patches):
        super().__init__(host, patches)

    def run(self):
        super().run()

        self.record_log()
        self.load("func")
        self.runcmd("xl debug-key h")
        # Requires a debug hv
        self.assert_log("new symbol keyhandler.c#new_static_func")
        self.assert_log("overriding symbol keyhandler.c#show_handlers")
        self.assert_log("overriding symbol get_random")
        self.assert_log("new symbol new_global_func")

        self.assert_log("patching existing static")
        self.assert_log("called new_static_func 56")
        self.assert_log("called new_global_func 67")
        self.assert_log("patching get_random")
        self.assert_log("called new_global_func 70")


        self.record_log()
        self.load("func2")
        self.runcmd("xl debug-key h")
        # Requires a debug hv
        self.assert_log("overriding symbol keyhandler.c#new_static_func")
        self.assert_log("overriding symbol keyhandler.c#show_handlers")
        self.assert_log("overriding symbol get_random")
        self.assert_log("overriding symbol new_global_func")

        self.assert_log("repatching existing static")
        self.assert_log("called new_static_func 56")
        self.assert_log("patching new_static_func 55")
        self.assert_log("called new_global_func 67")
        self.assert_log("patching called new_global_func 66")
        self.assert_log("patching get_random")
        self.assert_log("repatching get_random")
        self.assert_log("called new_global_func 43")
        self.assert_log("patching called new_global_func 42")
